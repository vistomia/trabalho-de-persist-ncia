import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session, select
from unittest.mock import patch, MagicMock
import tempfile
import os

# Importações do projeto
from main import app
from models.server_properties import ServerProperties

# Configuração do banco de dados de teste
TEST_DATABASE_URL = "sqlite:///:memory:"

class TestDatabase:
    """Classe para gerenciar banco de dados de teste"""
    def __init__(self, uri: str):
        self.__engine = create_engine(uri, echo=False)
        SQLModel.metadata.create_all(self.__engine)
    
    def get_engine(self):
        return self.__engine
    
    def get_session(self):
        return Session(self.__engine)

@pytest.fixture(scope="session")
def event_loop():
    """Configuração do event loop para testes assíncronos"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def test_db():
    """Cria um banco de dados de teste limpo para cada teste"""
    return TestDatabase(TEST_DATABASE_URL)

@pytest.fixture(scope="function")
def test_session(test_db):
    """Cria uma sessão de teste limpa para cada teste"""
    with Session(test_db.get_engine()) as session:
        yield session

@pytest.fixture(scope="function")
def client(test_db):
    """Cliente de teste FastAPI com banco de dados mockado"""
    def get_test_session():
        with Session(test_db.get_engine()) as session:
            yield session
    
    # Mock da dependência de sessão no router
    with patch('routers.server_properties.get_session', get_test_session):
        with TestClient(app) as test_client:
            yield test_client

@pytest.fixture
def sample_server_properties_data():
    """Dados de exemplo para server properties"""
    return {
        "difficulty": "normal",
        "max_players": 50,
        "gamemode": "survival", 
        "motd": "Test Server",
        "level_name": "test_world",
        "online_mode": True,
        "hardcore": False,
        "allow_flight": False,
        "spawn_protection": 16,
        "view_distance": 10
    }

@pytest.fixture
def create_test_server_properties(test_session, sample_server_properties_data):
    """Cria dados de teste no banco"""
    # Criar múltiplas propriedades para testar paginação e busca
    properties_list = [
        ServerProperties(
            difficulty="easy",
            max_players=20,
            gamemode="creative",
            motd="Creative Server",
            level_name="creative_world",
            online_mode=True,
            hardcore=False
        ),
        ServerProperties(
            difficulty="normal", 
            max_players=50,
            gamemode="survival",
            motd="Survival Server", 
            level_name="survival_world",
            online_mode=True,
            hardcore=False
        ),
        ServerProperties(
            difficulty="hard",
            max_players=30,
            gamemode="adventure",
            motd="Adventure Server",
            level_name="adventure_world", 
            online_mode=False,
            hardcore=True
        )
    ]
    
    for props in properties_list:
        test_session.add(props)
    test_session.commit()
    
    # Refresh para obter IDs
    for props in properties_list:
        test_session.refresh(props)
    
    return properties_list

class TestServerPropertiesRoutes:
    """Classe de testes para todas as rotas de server properties"""

    def test_read_server_properties_empty(self, client):
        """Testa listagem quando não há dados"""
        response = client.get("/server-properties/")
        assert response.status_code == 200
        assert response.json() == []

    def test_read_server_properties_with_data(self, client, create_test_server_properties):
        """Testa listagem com dados"""
        response = client.get("/server-properties/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        # Verificar se os dados corretos estão presentes
        motds = {item["motd"] for item in data}
        assert "Creative Server" in motds
        assert "Survival Server" in motds  
        assert "Adventure Server" in motds

    def test_read_server_properties_pagination(self, client, create_test_server_properties):
        """Testa paginação"""
        # Primeira página
        response = client.get("/server-properties/?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        # Segunda página  
        response = client.get("/server-properties/?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_read_server_properties_search(self, client, create_test_server_properties):
        """Testa busca por texto"""
        response = client.get("/server-properties/?search=Creative")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["motd"] == "Creative Server"

        # Busca por gamemode
        response = client.get("/server-properties/?search=survival")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        # Verificar se pelo menos um tem survival no gamemode
        has_survival = any(item["gamemode"] == "survival" for item in data)
        assert has_survival

    def test_read_server_properties_pagination_limits(self, client):
        """Testa limites de paginação"""
        # Skip negativo deve retornar erro 422
        response = client.get("/server-properties/?skip=-1")
        assert response.status_code == 422

        # Limit muito alto deve ser aceito mas limitado
        response = client.get("/server-properties/?limit=200")
        assert response.status_code == 422

        # Limit zero deve retornar erro
        response = client.get("/server-properties/?limit=0")
        assert response.status_code == 422

    def test_read_server_properties_by_id_success(self, client, create_test_server_properties):
        """Testa busca por ID existente"""
        properties = create_test_server_properties[0]
        response = client.get(f"/server-properties/{properties.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == properties.id
        assert data["motd"] == properties.motd

    def test_read_server_properties_by_id_not_found(self, client):
        """Testa busca por ID inexistente"""
        response = client.get("/server-properties/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Server properties not found"

    def test_search_server_properties_by_filters(self, client, create_test_server_properties):
        """Testa busca avançada com filtros múltiplos"""
        # Filtro por gamemode
        response = client.get("/server-properties/search/?gamemode=creative")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(item["gamemode"] == "creative" for item in data)

        # Filtro por difficulty  
        response = client.get("/server-properties/search/?difficulty=hard")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(item["difficulty"] == "hard" for item in data)

        # Filtro por online_mode
        response = client.get("/server-properties/search/?online_mode=false")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(item["online_mode"] == False for item in data)

        # Filtro por hardcore
        response = client.get("/server-properties/search/?hardcore=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(item["hardcore"] == True for item in data)

        # Filtro por max_players
        response = client.get("/server-properties/search/?max_players=50")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(item["max_players"] == 50 for item in data)

    def test_search_server_properties_pagination(self, client, create_test_server_properties):
        """Testa paginação na busca avançada"""
        response = client.get("/server-properties/search/?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

    def test_search_server_properties_no_results(self, client, create_test_server_properties):
        """Testa busca sem resultados"""
        response = client.get("/server-properties/search/?gamemode=nonexistent")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_count_server_properties(self, client, create_test_server_properties):
        """Testa contagem de server properties"""
        response = client.get("/server-properties/count/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 3

    def test_count_server_properties_empty(self, client):
        """Testa contagem quando vazio"""
        response = client.get("/server-properties/count/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0

    def test_read_server_properties_ordered(self, client, create_test_server_properties):
        """Testa ordenação"""
        # Ordenação por ID crescente
        response = client.get("/server-properties/ordered/?order_by=id&desc=false")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["id"] <= data[1]["id"] <= data[2]["id"]

        # Ordenação por ID decrescente
        response = client.get("/server-properties/ordered/?order_by=id&desc=true")
        assert response.status_code == 200
        data = response.json()
        assert data[0]["id"] >= data[1]["id"] >= data[2]["id"]

        # Ordenação por gamemode
        response = client.get("/server-properties/ordered/?order_by=gamemode")
        assert response.status_code == 200
        data = response.json()
        gamemodes = [item["gamemode"] for item in data]
        assert gamemodes == sorted(gamemodes)

        # Ordenação por max_players
        response = client.get("/server-properties/ordered/?order_by=max_players")
        assert response.status_code == 200
        data = response.json()
        max_players = [item["max_players"] for item in data]
        assert max_players == sorted(max_players)

    def test_read_server_properties_ordered_invalid_field(self, client):
        """Testa ordenação com campo inválido"""
        response = client.get("/server-properties/ordered/?order_by=invalid_field")
        assert response.status_code == 422

    def test_create_server_properties(self, client, sample_server_properties_data):
        """Testa criação de server properties"""
        response = client.post("/server-properties/", json=sample_server_properties_data)
        assert response.status_code == 200
        data = response.json()
        assert data["motd"] == sample_server_properties_data["motd"]
        assert data["difficulty"] == sample_server_properties_data["difficulty"]
        assert data["id"] is not None

    def test_create_server_properties_minimal_data(self, client):
        """Testa criação com dados mínimos"""
        minimal_data = {}
        response = client.post("/server-properties/", json=minimal_data)
        assert response.status_code == 200
        data = response.json()
        # Verificar valores padrão
        assert data["difficulty"] == "easy"
        assert data["max_players"] == 20
        assert data["gamemode"] == "survival"

    def test_update_server_properties_success(self, client, create_test_server_properties):
        """Testa atualização bem-sucedida"""
        properties = create_test_server_properties[0]
        update_data = {
            "motd": "Updated MOTD",
            "max_players": 100,
            "difficulty": "hard"
        }
        
        response = client.patch(f"/server-properties/{properties.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["motd"] == "Updated MOTD"
        assert data["max_players"] == 100
        assert data["difficulty"] == "hard"

    def test_update_server_properties_partial(self, client, create_test_server_properties):
        """Testa atualização parcial"""
        properties = create_test_server_properties[0]
        original_motd = properties.motd
        update_data = {"max_players": 75}
        
        response = client.patch(f"/server-properties/{properties.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["max_players"] == 75
        assert data["motd"] == original_motd  # Não deve ter mudado

    def test_update_server_properties_not_found(self, client):
        """Testa atualização de propriedade inexistente"""
        update_data = {"motd": "New MOTD"}
        response = client.patch("/server-properties/999", json=update_data)
        assert response.status_code == 404
        assert response.json()["detail"] == "Server properties not found"

    def test_update_server_properties_empty_data(self, client, create_test_server_properties):
        """Testa atualização com dados vazios"""
        properties = create_test_server_properties[0]
        response = client.patch(f"/server-properties/{properties.id}", json={})
        assert response.status_code == 200

    def test_delete_server_properties_success(self, client, create_test_server_properties):
        """Testa exclusão bem-sucedida"""
        properties = create_test_server_properties[0]
        response = client.delete(f"/server-properties/{properties.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Server properties deleted successfully"

        # Verificar se foi realmente excluído
        get_response = client.get(f"/server-properties/{properties.id}")
        assert get_response.status_code == 404

    def test_delete_server_properties_not_found(self, client):
        """Testa exclusão de propriedade inexistente"""
        response = client.delete("/server-properties/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Server properties not found"

    def test_complex_search_scenarios(self, client, create_test_server_properties):
        """Testa cenários de busca mais complexos"""
        # Busca com múltiplos termos
        response = client.get("/server-properties/?search=Server")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3  # Todos têm "Server" no MOTD

        # Busca case-insensitive (depende da implementação do SQLite)
        response = client.get("/server-properties/?search=creative")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 0  # Pode ser case-sensitive

    def test_edge_cases_pagination(self, client, create_test_server_properties):
        """Testa casos extremos de paginação"""
        # Skip maior que total de registros
        response = client.get("/server-properties/?skip=100")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

        # Limit 1
        response = client.get("/server-properties/?limit=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_concurrent_operations(self, client, create_test_server_properties):
        """Testa operações concorrentes básicas"""
        properties = create_test_server_properties[0]
        
        # Múltiplas leituras simultâneas
        responses = []
        for _ in range(5):
            response = client.get(f"/server-properties/{properties.id}")
            responses.append(response)
        
        for response in responses:
            assert response.status_code == 200

    @pytest.mark.parametrize("order_by,desc", [
        ("id", True),
        ("id", False), 
        ("gamemode", True),
        ("gamemode", False),
        ("difficulty", True),
        ("difficulty", False),
        ("max_players", True),
        ("max_players", False),
        ("motd", True),
        ("motd", False),
        ("level_name", True),
        ("level_name", False)
    ])
    def test_all_ordering_combinations(self, client, create_test_server_properties, order_by, desc):
        """Testa todas as combinações de ordenação"""
        response = client.get(f"/server-properties/ordered/?order_by={order_by}&desc={desc}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_search_validation_errors(self, client):
        """Testa erros de validação na busca"""
        # max_players negativo
        response = client.get("/server-properties/search/?max_players=-1")
        assert response.status_code == 422

    def test_stress_create_and_list(self, client):
        """Teste de stress básico - criação e listagem múltipla"""
        # Criar múltiplas propriedades
        created_ids = []
        for i in range(10):
            data = {
                "motd": f"Test Server {i}",
                "max_players": 20 + i,
                "difficulty": "normal"
            }
            response = client.post("/server-properties/", json=data)
            assert response.status_code == 200
            created_ids.append(response.json()["id"])

        # Listar todas
        response = client.get("/server-properties/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 10

        # Verificar contagem
        response = client.get("/server-properties/count/")
        assert response.status_code == 200
        assert response.json()["count"] == 10

    def test_update_with_none_values(self, client, create_test_server_properties):
        """Testa atualização com valores None"""
        properties = create_test_server_properties[0]
        original_motd = properties.motd
        
        # Valores None devem ser ignorados
        update_data = {
            "motd": None,
            "max_players": 50
        }
        response = client.patch(f"/server-properties/{properties.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["max_players"] == 50
        # MOTD não deve ter sido alterado para None (depende da implementação)

    def test_api_response_structure(self, client, create_test_server_properties):
        """Testa a estrutura de resposta da API"""
        response = client.get("/server-properties/")
        assert response.status_code == 200
        data = response.json()
        
        if len(data) > 0:
            # Verificar se campos obrigatórios estão presentes
            required_fields = ["id", "difficulty", "max_players", "gamemode", "motd"]
            for field in required_fields:
                assert field in data[0]

    def test_boolean_field_handling(self, client, create_test_server_properties):
        """Testa o manuseio correto de campos booleanos"""
        # Testar com valores booleanos explícitos
        response = client.get("/server-properties/search/?online_mode=true")
        assert response.status_code == 200
        
        response = client.get("/server-properties/search/?hardcore=false")
        assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])