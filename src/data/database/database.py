import csv
import os
import shutil
import logging
from tempfile import NamedTemporaryFile
from pathlib import Path
from itertools import islice
import colorlog

class Database:
    """Gerencia um banco de dados baseado em um arquivo CSV com um índice sequencial.
    
    :param str data_path: Caminho para o arquivo CSV de dados.
    :param str index_path: Caminho para o arquivo CSV de índice.
    :param str key_column: Nome da coluna que serve como chave primária.
    :param list schema: Lista de nomes de colunas no arquivo CSV.
    :return: None
    """
    def __init__(self, data_path: str, index_path: str, key_column: str, schema: list):
        self.data_path = Path(data_path)
        self.index_path = Path(index_path)
        self.key_column = key_column
        
        self.schema = schema
        self.schema.append('deleted')


        logging.basicConfig(
            level=logging.DEBUG, 
            format='%(log_color)s[%(asctime)s] [%(levelname)s]: %(message)s%(reset)s', 
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                colorlog.StreamHandler()
            ]
        )

        logging.getLogger().handlers[0].setFormatter(
            colorlog.ColoredFormatter(
            '%(log_color)s%(bold)s[%(asctime)s] [%(levelname)s]:%(reset)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'blue',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
            )
        )
        self.logger = logging.getLogger(__name__)

        # O índice em memória: {chave: (num_linha, deleted_flag)}
        self.index = {}

        if key_column not in self.schema:
            raise ValueError(f"A coluna chave '{key_column}' não está no esquema.")

        self._initialize_files()
        self._load_index()

    def _initialize_files(self):
        """Cria os arquivos de dados e índice com cabeçalhos se não existirem.

        :return: None
        """
        if not self.data_path.exists():
            with open(self.data_path, 'w', newline='', encoding='utf-8') as f:
                csv.DictWriter(f, fieldnames=self.schema).writeheader()
        
        if not self.index_path.exists():
            with open(self.index_path, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(['key', 'line_number', 'deleted'])

    def _load_index(self):
        """Lê o arquivo de índice do disco e o carrega no dicionário em memória.

        :return: None
        """
        try:
            with open(self.index_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader) # Pula o cabeçalho
                
                self.index = {key: (int(line), int(deleted)) for key, line, deleted in reader if int(deleted) == 0}
        except (FileNotFoundError, StopIteration):
            pass # Arquivo não existe ou está vazio, o índice fica vazio

    def _atomic_rewrite(self, operation_func, rebuild_index_after=False):
        """Função auxiliar segura para reescrever o arquivo de dados.

        :param function operation_func: Função que define a operação a ser feita em cada linha.
        :param bool rebuild_index_after: Se True, reconstrói o índice após a reescrita.
        :return: None
        """
        temp_file = NamedTemporaryFile(mode='w', newline='', delete=False, encoding='utf-8')
        try:
            with open(self.data_path, 'r', newline='', encoding='utf-8') as infile, temp_file:
                reader = csv.DictReader(infile)
                writer = csv.DictWriter(temp_file, fieldnames=self.schema)
                writer.writeheader()
                for row in reader:
                    # A função de operação decide o que fazer com a linha
                    operation_func(row, writer)
            # shutil.move é uma operação atômica na maioria dos sistemas
            shutil.move(temp_file.name, self.data_path)
        finally:
            if os.path.exists(temp_file.name):
                os.remove(temp_file.name)
        
        if rebuild_index_after:
            self.rebuild_index()

    def rebuild_index(self):
        """Recria o arquivo de índice lendo o arquivo de dados. Lento, mas necessário.

        :return: None
        """
        self.index.clear()
        with open(self.data_path, 'r', newline='') as data_f, \
             open(self.index_path, 'w', newline='') as index_f:
            
            reader = csv.DictReader(data_f)
            index_writer = csv.writer(index_f)
            index_writer.writerow(['key', 'line_number', 'deleted'])

            for i, row in enumerate(reader):
                key = row[self.key_column]
                deleted = int(row.get('deleted', 0))
                self.index[key] = (i, deleted)
                index_writer.writerow([key, i, deleted])

    def insert(self, record: dict):
        """Insere um novo registro. Operação rápida de anexação.

        :param dict record: O registro a ser inserido.
        """
        key = str(record.get(self.key_column))

        if key == 'None':
            incremental_key = str(len(self.index) + 1)
            record[self.key_column] = incremental_key
            key = incremental_key

        if key in self.index:
            raise ValueError(f"A chave '{key}' já existe.")

        record['deleted'] = 0
        line_number = len(self.index)
        
        with open(self.data_path, 'a', newline='') as f_data, \
             open(self.index_path, 'a', newline='') as f_index:
            csv.DictWriter(f_data, fieldnames=self.schema).writerow(record)
            csv.writer(f_index).writerow([key, line_number, 0])
        
        self.index[key] = (line_number, 0)
        logging.debug(f"Registro inserido com chave '{key}' na linha {line_number}.")

    def get(self, key: str) -> dict | None:
        """Busca um registro pela chave usando o índice. Ignora registros deletados.

        :param str key: A chave do registro a ser buscado.
        """
        key = str(key)
        index_entry = self.index.get(key)
        
        if not index_entry or index_entry[1] == 1: # Não existe ou está deletado
            return None
        
        line_number = index_entry[0]
        with open(self.data_path, 'r', newline='') as f:
            reader = csv.reader(f)
            # islice pula eficientemente para a linha alvo
            target_row_values = next(islice(reader, line_number + 1, None), None)
            if target_row_values:
                return dict(zip(self.schema, target_row_values))
        return None
    
    def get_all(self) -> list:
        """Retorna todos os registros ativos (não deletados).

        :return: Lista de dicionários representando os registros.
        """
        records = []
        with open(self.data_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if int(row.get('deleted', 0)) == 0:
                    records.append(row)
        return records

    def update(self, key: str, updates: dict):
        """Atualiza um registro. Requer reescrita do arquivo.

        :param str key: A chave do registro a ser atualizado.
        """
        key = str(key)
        if key not in self.index or self.index[key][1] == 1:
            raise ValueError(f"Registro com chave '{key}' não encontrado ou está deletado.")
        if self.key_column in updates:
            raise ValueError("A coluna chave não pode ser atualizada.")

        def operation(row, writer):
            if str(row[self.key_column]) == key:
                row.update(updates)
            writer.writerow(row)

        self._atomic_rewrite(operation)
        logging.info(f"Registro '{key}' atualizado.")

    def delete(self, key: str):
        """Realiza um 'soft delete', marcando o registro como deletado.
        
        :param str key: A chave do registro a ser deletado.
        :return: None
        """
        key = str(key)
        if key not in self.index or self.index[key][1] == 1:
            logging.warning(f"Chave '{key}' não encontrada ou já deletada.")
            return

        # É uma operação de atualização que muda a flag 'deleted'
        self.update(key, {'deleted': 1})
        
        # Atualiza o índice em memória e no disco
        line_number, _ = self.index[key]
        self.index[key] = (line_number, 1)
        self.rebuild_index() # Necessário para atualizar o arquivo de índice

    def drop(self):
        """Apaga todos os dados e índices, reiniciando o banco de dados.

        :return: None
        """
        if self.data_path.exists():
            self.data_path.unlink()
        if self.index_path.exists():
            self.index_path.unlink()
        
        self.index.clear()
        self._initialize_files()
        logging.info("Banco de dados apagado.")

    def count(self) -> int:
        """Conta apenas os registros ativos (não deletados) usando o índice.

        :return: Número de registros ativos.
        """
        return sum(1 for _, deleted in self.index.values() if deleted == 0)

    def vacuum(self):
        """Remove fisicamente todos os registros marcados como deletados.

        :return: None
        """
        logging.info("Iniciando processo de vacuum...")
        
        def operation(row, writer):
            if int(row.get('deleted', 0)) == 0:
                writer.writerow(row) # Só escreve a linha se não estiver deletada

        # A reescrita invalida todas as posições, então a reconstrução do índice é obrigatória
        self._atomic_rewrite(operation, rebuild_index_after=True)
        logging.info("Vacuum concluído.")
