"""
Testes oficiais das rotas usando FastAPI TestClient
Testa as rotas reais da aplicação sem mocks
"""

import pytest
import os
import tempfile
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
import json

# Importações da aplicação
from main import app
from models.server_properties import ServerProperties
from database.database import Database

class TestRealRoutes:
    """Testes das rotas reais usando TestClient oficial do FastAPI"""
    
    @pytest.fixture(scope="function")
    def client(self):
        """Cliente de teste oficial do FastAPI"""
        return TestClient(app)
    
    @pytest.fixture(scope="function") 
    def temp_db_file(self):
        """Cria um arquivo de banco temporário para cada teste"""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)  # Fecha o file descriptor
        yield path
        # Cleanup - remove o arquivo temporário
        try:
            os.unlink(path)
        except OSError:
            pass

    def test_health_check_if_exists(self, client):
        """Testa se existe uma rota de health check"""
        response = client.get("/health")
        # Se existir, deve retornar 200, se não existir, retorna 404
        assert response.status_code in [200, 404]

    def test_docs_endpoint(self, client):
        """Testa se a documentação Swagger está acessível"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_openapi_json(self, client):
        """Testa se o schema OpenAPI está acessível"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json"
        
        # Verificar se é um JSON válido
        openapi_data = response.json()
        assert "openapi" in openapi_data
        assert "paths" in openapi_data

    def test_server_properties_routes_exist(self, client):
        """Testa se as rotas de server properties existem"""
        # GET /server-properties/
        response = client.get("/server-properties/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_server_properties_count_route(self, client):
        """Testa rota de contagem"""
        response = client.get("/server-properties/count/")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert isinstance(data["count"], int)

    def test_create_server_properties_real(self, client):
        """Testa criação real de server properties"""
        server_data = {
            "motd": "Test Real Server",
            "difficulty": "normal", 
            "max_players": 30,
            "gamemode": "survival",
            "level_name": "test_world",
            "online_mode": True,
            "hardcore": False
        }
        
        response = client.post("/server-properties/", json=server_data)
        assert response.status_code == 200
        
        created_data = response.json()
        assert created_data["motd"] == server_data["motd"]
        assert created_data["difficulty"] == server_data["difficulty"]
        assert "id" in created_data
        
        # Verificar se foi criado consultando por ID
        server_id = created_data["id"]
        get_response = client.get(f"/server-properties/{server_id}")
        assert get_response.status_code == 200
        assert get_response.json()["id"] == server_id

    def test_create_and_update_real(self, client):
        """Testa criação e atualização real"""
        # Criar
        server_data = {
            "motd": "Original MOTD",
            "difficulty": "easy",
            "max_players": 20
        }
        
        create_response = client.post("/server-properties/", json=server_data)
        assert create_response.status_code == 200
        server_id = create_response.json()["id"]
        
        # Atualizar
        update_data = {
            "motd": "Updated MOTD", 
            "difficulty": "hard",
            "max_players": 50
        }
        
        update_response = client.patch(f"/server-properties/{server_id}", json=update_data)
        assert update_response.status_code == 200
        
        updated_data = update_response.json()
        assert updated_data["motd"] == update_data["motd"]
        assert updated_data["difficulty"] == update_data["difficulty"]
        assert updated_data["max_players"] == update_data["max_players"]

    def test_create_and_delete_real(self, client):
        """Testa criação e exclusão real"""
        # Criar
        server_data = {
            "motd": "To be deleted",
            "difficulty": "normal"
        }
        
        create_response = client.post("/server-properties/", json=server_data)
        assert create_response.status_code == 200
        server_id = create_response.json()["id"]
        
        # Verificar se existe
        get_response = client.get(f"/server-properties/{server_id}")
        assert get_response.status_code == 200
        
        # Deletar
        delete_response = client.delete(f"/server-properties/{server_id}")
        assert delete_response.status_code == 200
        
        # Verificar se foi deletado
        get_after_delete = client.get(f"/server-properties/{server_id}")
        assert get_after_delete.status_code == 404

    def test_pagination_real(self, client):
        """Testa paginação com dados reais"""
        # Criar múltiplos registros
        created_ids = []
        for i in range(5):
            server_data = {
                "motd": f"Pagination Test Server {i}",
                "difficulty": "normal",
                "max_players": 20 + i
            }
            response = client.post("/server-properties/", json=server_data)
            assert response.status_code == 200
            created_ids.append(response.json()["id"])
        
        # Testar paginação
        page1_response = client.get("/server-properties/?skip=0&limit=3")
        assert page1_response.status_code == 200
        page1_data = page1_response.json()
        
        page2_response = client.get("/server-properties/?skip=3&limit=3")
        assert page2_response.status_code == 200
        page2_data = page2_response.json()
        
        # Verificar que não há sobreposição
        page1_ids = {item["id"] for item in page1_data}
        page2_ids = {item["id"] for item in page2_data}
        assert len(page1_ids.intersection(page2_ids)) == 0

    def test_search_functionality_real(self, client):
        """Testa busca com dados reais"""
        # Criar registro com dados específicos para busca
        unique_motd = "Unique Search Test Server 12345"
        server_data = {
            "motd": unique_motd,
            "difficulty": "hard",
            "gamemode": "creative"
        }
        
        create_response = client.post("/server-properties/", json=server_data)
        assert create_response.status_code == 200
        
        # Buscar por MOTD
        search_response = client.get(f"/server-properties/?search=Unique Search Test")
        assert search_response.status_code == 200
        search_data = search_response.json()
        
        # Verificar se encontrou o registro
        found = any(item["motd"] == unique_motd for item in search_data)
        assert found, f"Não encontrou o servidor com MOTD: {unique_motd}"

    def test_advanced_search_real(self, client):
        """Testa busca avançada com filtros"""
        # Criar servidor com características específicas
        server_data = {
            "motd": "Advanced Search Test",
            "difficulty": "hard",
            "gamemode": "survival",
            "max_players": 100,
            "hardcore": True,
            "online_mode": False
        }
        
        create_response = client.post("/server-properties/", json=server_data)
        assert create_response.status_code == 200
        server_id = create_response.json()["id"]
        
        # Testar filtros específicos
        filters = [
            ("difficulty=hard", "difficulty", "hard"),
            ("gamemode=survival", "gamemode", "survival"),
            ("max_players=100", "max_players", 100),
            ("hardcore=true", "hardcore", True),
            ("online_mode=false", "online_mode", False)
        ]
        
        for filter_param, field, expected_value in filters:
            response = client.get(f"/server-properties/search/?{filter_param}")
            assert response.status_code == 200
            data = response.json()
            
            # Verificar se o registro criado está nos resultados
            found = any(item["id"] == server_id and item[field] == expected_value for item in data)
            assert found, f"Filtro {filter_param} não funcionou corretamente"

    def test_ordering_real(self, client):
        """Testa ordenação com dados reais"""
        # Criar servidores com valores diferentes para ordenação
        servers_data = [
            {"motd": "Server A", "max_players": 30, "difficulty": "normal"},
            {"motd": "Server B", "max_players": 10, "difficulty": "easy"}, 
            {"motd": "Server C", "max_players": 50, "difficulty": "hard"}
        ]
        
        created_ids = []
        for server_data in servers_data:
            response = client.post("/server-properties/", json=server_data)
            assert response.status_code == 200
            created_ids.append(response.json()["id"])
        
        # Testar ordenação por max_players crescente
        order_response = client.get("/server-properties/ordered/?order_by=max_players&desc=false")
        assert order_response.status_code == 200
        ordered_data = order_response.json()
        
        # Verificar se está ordenado corretamente
        max_players_values = [item["max_players"] for item in ordered_data if item["id"] in created_ids]
        assert max_players_values == sorted(max_players_values)
        
        # Testar ordenação decrescente
        desc_response = client.get("/server-properties/ordered/?order_by=max_players&desc=true")
        assert desc_response.status_code == 200
        desc_data = desc_response.json()
        
        desc_max_players = [item["max_players"] for item in desc_data if item["id"] in created_ids]
        assert desc_max_players == sorted(desc_max_players, reverse=True)

    def test_error_handling_real(self, client):
        """Testa tratamento de erros reais"""
        # Teste 404 - ID não existe
        response = client.get("/server-properties/99999")
        assert response.status_code == 404
        assert "detail" in response.json()
        
        # Teste 422 - Parâmetros inválidos
        response = client.get("/server-properties/?skip=-1")
        assert response.status_code == 422
        
        response = client.get("/server-properties/?limit=0")
        assert response.status_code == 422
        
        # Teste update com ID inexistente
        update_response = client.patch("/server-properties/99999", json={"motd": "test"})
        assert update_response.status_code == 404
        
        # Teste delete com ID inexistente
        delete_response = client.delete("/server-properties/99999")
        assert delete_response.status_code == 404

    def test_data_persistence_real(self, client):
        """Testa se os dados persistem entre requests"""
        # Criar um servidor
        server_data = {
            "motd": "Persistence Test Server",
            "difficulty": "normal",
            "max_players": 25
        }
        
        create_response = client.post("/server-properties/", json=server_data)
        assert create_response.status_code == 200
        server_id = create_response.json()["id"]
        
        # Fazer múltiplas consultas para verificar persistência
        for _ in range(3):
            get_response = client.get(f"/server-properties/{server_id}")
            assert get_response.status_code == 200
            data = get_response.json()
            assert data["motd"] == server_data["motd"]
            assert data["id"] == server_id

    def test_concurrent_requests_real(self, client):
        """Testa requests concorrentes (simulado sequencialmente)"""
        # Criar servidor base
        server_data = {
            "motd": "Concurrent Test Server",
            "difficulty": "normal"
        }
        
        create_response = client.post("/server-properties/", json=server_data)
        assert create_response.status_code == 200
        server_id = create_response.json()["id"]
        
        # Simular múltiplas leituras simultâneas
        responses = []
        for _ in range(10):
            response = client.get(f"/server-properties/{server_id}")
            responses.append(response)
        
        # Verificar se todas foram bem-sucedidas
        for response in responses:
            assert response.status_code == 200
            assert response.json()["id"] == server_id

    def test_full_crud_cycle_real(self, client):
        """Teste completo do ciclo CRUD"""
        # CREATE
        server_data = {
            "motd": "Full CRUD Test",
            "difficulty": "easy",
            "max_players": 20,
            "gamemode": "creative",
            "hardcore": False,
            "online_mode": True
        }
        
        create_response = client.post("/server-properties/", json=server_data)
        assert create_response.status_code == 200
        server_id = create_response.json()["id"]
        
        # READ (individual)
        get_response = client.get(f"/server-properties/{server_id}")
        assert get_response.status_code == 200
        get_data = get_response.json()
        assert get_data["motd"] == server_data["motd"]
        
        # READ (list) - verificar se está na lista
        list_response = client.get("/server-properties/")
        assert list_response.status_code == 200
        list_data = list_response.json()
        found_in_list = any(item["id"] == server_id for item in list_data)
        assert found_in_list
        
        # UPDATE
        update_data = {
            "motd": "Updated Full CRUD Test",
            "difficulty": "hard",
            "max_players": 100
        }
        
        update_response = client.patch(f"/server-properties/{server_id}", json=update_data)
        assert update_response.status_code == 200
        updated_data = update_response.json()
        assert updated_data["motd"] == update_data["motd"]
        assert updated_data["difficulty"] == update_data["difficulty"]
        assert updated_data["max_players"] == update_data["max_players"]
        
        # Verificar se a atualização persistiu
        get_updated_response = client.get(f"/server-properties/{server_id}")
        assert get_updated_response.status_code == 200
        assert get_updated_response.json()["motd"] == update_data["motd"]
        
        # DELETE
        delete_response = client.delete(f"/server-properties/{server_id}")
        assert delete_response.status_code == 200
        
        # Verificar se foi realmente deletado
        get_deleted_response = client.get(f"/server-properties/{server_id}")
        assert get_deleted_response.status_code == 404

    def test_response_format_validation(self, client):
        """Testa se o formato das respostas está correto"""
        # Criar um servidor para testar formatos
        server_data = {"motd": "Format Test Server"}
        create_response = client.post("/server-properties/", json=server_data)
        assert create_response.status_code == 200
        
        created_data = create_response.json()
        
        # Verificar campos obrigatórios na resposta
        required_fields = ["id", "motd", "difficulty", "max_players", "gamemode"]
        for field in required_fields:
            assert field in created_data, f"Campo obrigatório '{field}' não encontrado"
        
        # Verificar tipos de dados
        assert isinstance(created_data["id"], int)
        assert isinstance(created_data["motd"], str)
        assert isinstance(created_data["max_players"], int)
        assert isinstance(created_data["difficulty"], str)

if __name__ == "__main__":
    # Executar os testes
    pytest.main([__file__, "-v", "--tb=short"])