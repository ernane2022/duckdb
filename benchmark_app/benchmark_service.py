import time
import duckdb
import pandas as pd
import subprocess
import json
from django.db import models, connections
from django.conf import settings
from .models import SalesRecord
import random
from faker import Faker
import logging

logger = logging.getLogger(__name__)

class SequentialBenchmarkService:
    def __init__(self):
        self.fake = Faker('pt_BR')
        self.duckdb_conn = duckdb.connect(':memory:')
        
        # Configuração dos databases sequenciais
        self.database_configs = {
            'duckdb': {
                'name': 'DuckDB',
                'icon': '🦆',
                'description': 'Database Analítico OLAP',
                'requires_docker': False,
                'django_db': None
            },
            'sqlite': {
                'name': 'SQLite',
                'icon': '🗃️',
                'description': 'Database Embarcado',
                'requires_docker': False,
                'django_db': 'default'
            },
            'postgresql': {
                'name': 'PostgreSQL',
                'icon': '🐘',
                'description': 'Database Avançado',
                'requires_docker': True,
                'django_db': 'postgresql',
                'container': 'benchmark_postgres',
                'service': 'postgres'
            },
            'mysql': {
                'name': 'MySQL',
                'icon': '🐬',
                'description': 'Database Popular',
                'requires_docker': True,
                'django_db': 'mysql',
                'container': 'benchmark_mysql',
                'service': 'mysql'
            },
            'mariadb': {
                'name': 'MariaDB',
                'icon': '🗂️',
                'description': 'Fork do MySQL',
                'requires_docker': True,
                'django_db': 'mariadb',
                'container': 'benchmark_mariadb',
                'service': 'mariadb'
            }
        }
    
    def stop_all_containers(self):
        """Para todos os containers Docker"""
        try:
            subprocess.run([
                'docker-compose', '-f', 'docker-compose-databases.yml', 'down'
            ], check=True, capture_output=True)
            print("🛑 Todos os containers parados")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Erro ao parar containers: {e}")
            return False
    
    def start_specific_container(self, service_name):
        """Inicia um container específico"""
        try:
            # Para todos primeiro
            self.stop_all_containers()
            time.sleep(2)
            
            # Inicia apenas o serviço específico
            subprocess.run([
                'docker-compose', '-f', 'docker-compose-databases.yml', 
                'up', '-d', service_name
            ], check=True, capture_output=True)
            
            print(f"⏳ Aguardando {service_name} inicializar...")
            time.sleep(15)  # Tempo para inicialização
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"Erro ao iniciar {service_name}: {e}")
            return False
    
    def check_database_connection(self, db_config):
        """Verifica se o database está acessível"""
        if not db_config['requires_docker']:
            return True
            
        try:
            if db_config['django_db']:
                conn = connections[db_config['django_db']]
                cursor = conn.cursor()
                cursor.execute('SELECT 1')
                cursor.fetchone()
                return True
        except Exception as e:
            print(f"❌ Falha na conexão com {db_config['name']}: {e}")
            return False
    
    def migrate_database(self, db_config):
        """Executa migrações para o database"""
        if not db_config['django_db']:
            return True
            
        try:
            from django.core.management import execute_from_command_line
            execute_from_command_line([
                'manage.py', 'migrate', '--database', db_config['django_db']
            ])
            return True
        except Exception as e:
            print(f"❌ Erro ao migrar {db_config['name']}: {e}")
            return False
    
    def generate_test_data(self, num_records=10000):
        """Gera dados de teste"""
        print(f"📊 Gerando {num_records:,} registros de teste...")
        
        categories = ['Eletrônicos', 'Roupas', 'Casa', 'Livros', 'Esportes', 'Automotivo', 'Saúde', 'Beleza']
        regions = ['Norte', 'Sul', 'Leste', 'Oeste', 'Centro', 'Nordeste', 'Sudeste', 'Centro-Oeste']
        
        data = []
        for i in range(num_records):
            data.append({
                'customer_id': random.randint(1, num_records // 10),
                'product_name': self.fake.catch_phrase()[:100],
                'category': random.choice(categories),
                'price': round(random.uniform(10, 5000), 2),
                'quantity': random.randint(1, 20),
                'sale_date': self.fake.date_time_between(start_date='-2y', end_date='now'),
                'region': random.choice(regions),
                'salesperson': self.fake.name()[:100],
            })
        
        return pd.DataFrame(data)
    
    def setup_duckdb_data(self, df):
        """Configura dados no DuckDB"""
        try:
            self.duckdb_conn.execute("DROP TABLE IF EXISTS sales_record")
            self.duckdb_conn.execute("""
                CREATE TABLE sales_record (
                    customer_id INTEGER,
                    product_name VARCHAR,
                    category VARCHAR,
                    price DECIMAL(10,2),
                    quantity INTEGER,
                    sale_date TIMESTAMP,
                    region VARCHAR,
                    salesperson VARCHAR
                )
            """)
            
            self.duckdb_conn.execute("INSERT INTO sales_record SELECT * FROM df")
            count = self.duckdb_conn.execute("SELECT COUNT(*) FROM sales_record").fetchone()[0]
            print(f"✅ DuckDB: {count:,} registros inseridos")
            return True
        except Exception as e:
            print(f"❌ Erro no DuckDB: {e}")
            return False
    
    def setup_django_data(self, df, db_name):
        """Insere dados no Django ORM para um database específico"""
        try:
            # Limpar dados anteriores
            SalesRecord.objects.using(db_name).all().delete()
            
            # Inserir em lotes
            batch_size = 1000
            records = []
            
            for _, row in df.iterrows():
                records.append(SalesRecord(**row.to_dict()))
                
                if len(records) >= batch_size:
                    SalesRecord.objects.using(db_name).bulk_create(records, ignore_conflicts=True)
                    records = []
            
            if records:
                SalesRecord.objects.using(db_name).bulk_create(records, ignore_conflicts=True)
            
            count = SalesRecord.objects.using(db_name).count()
            print(f"✅ {db_name}: {count:,} registros inseridos")
            return True
        except Exception as e:
            print(f"❌ Erro ao inserir dados no {db_name}: {e}")
            return False
    
    def run_database_benchmarks(self, db_key, db_config, df):
        """Executa todos os benchmarks para um database específico"""
        results = {}
        
        if db_key == 'duckdb':
            # DuckDB
            if not self.setup_duckdb_data(df):
                return {}
            
            # Teste de agregação
            results['aggregation'] = self.benchmark_duckdb_aggregation()
            
            # Teste de filtros
            results['filter'] = self.benchmark_duckdb_filter()
            
        else:
            # Django databases
            django_db = db_config['django_db']
            
            if not self.setup_django_data(df, django_db):
                return {}
            
            # Teste de agregação
            results['aggregation'] = self.benchmark_django_aggregation(django_db, db_key)
            
            # Teste de filtros
            results['filter'] = self.benchmark_django_filter(django_db, db_key)
        
        return results
    
    def benchmark_duckdb_aggregation(self):
        """Benchmark DuckDB agregação"""
        try:
            start_time = time.time()
            result = self.duckdb_conn.execute("""
                SELECT category, 
                       COUNT(*) as total_sales,
                       SUM(price * quantity) as total_revenue,
                       AVG(price) as avg_price
                FROM sales_record 
                GROUP BY category 
                ORDER BY total_revenue DESC
            """).fetchall()
            execution_time = time.time() - start_time
            
            return {
                'execution_time': execution_time,
                'rows_returned': len(result),
                'status': 'success'
            }
        except Exception as e:
            return {
                'execution_time': None,
                'rows_returned': 0,
                'status': 'error',
                'error': str(e)
            }
    
    def benchmark_duckdb_filter(self):
        """Benchmark DuckDB filtros"""
        try:
            start_time = time.time()
            result = self.duckdb_conn.execute("""
                SELECT category, region, price, quantity, sale_date
                FROM sales_record 
                WHERE price > 1000 AND quantity > 5
                ORDER BY price DESC
                LIMIT 100
            """).fetchall()
            execution_time = time.time() - start_time
            
            return {
                'execution_time': execution_time,
                'rows_returned': len(result),
                'status': 'success'
            }
        except Exception as e:
            return {
                'execution_time': None,
                'rows_returned': 0,
                'status': 'error',
                'error': str(e)
            }
    
    def benchmark_django_aggregation(self, db_name, db_key):
        """Benchmark Django ORM agregação"""
        try:
            start_time = time.time()
            result = list(SalesRecord.objects.using(db_name).values('category').annotate(
                total_sales=models.Count('id'),
                total_revenue=models.Sum(models.F('price') * models.F('quantity')),
                avg_price=models.Avg('price')
            ).order_by('-total_revenue'))
            execution_time = time.time() - start_time
            
            return {
                'execution_time': execution_time,
                'rows_returned': len(result),
                'status': 'success'
            }
        except Exception as e:
            return {
                'execution_time': None,
                'rows_returned': 0,
                'status': 'error',
                'error': str(e)
            }
    
    def benchmark_django_filter(self, db_name, db_key):
        """Benchmark Django ORM filtros"""
        try:
            start_time = time.time()
            result = list(SalesRecord.objects.using(db_name).filter(
                price__gt=1000,
                quantity__gt=5
            ).order_by('-price')[:100])
            execution_time = time.time() - start_time
            
            return {
                'execution_time': execution_time,
                'rows_returned': len(result),
                'status': 'success'
            }
        except Exception as e:
            return {
                'execution_time': None,
                'rows_returned': 0,
                'status': 'error',
                'error': str(e)
            }
    
    def run_sequential_benchmark(self, num_records=10000, callback=None):
        """Executa benchmark sequencial em todos os databases"""
        print(f"🚀 Iniciando benchmark sequencial com {num_records:,} registros")
        
        # Gerar dados uma vez
        df = self.generate_test_data(num_records)
        
        all_results = {}
        total_databases = len(self.database_configs)
        
        for i, (db_key, db_config) in enumerate(self.database_configs.items(), 1):
            print(f"\n{'='*60}")
            print(f"🔄 Testando {db_config['name']} ({i}/{total_databases})")
            print(f"{'='*60}")
            
            # Callback para progresso
            if callback:
                callback({
                    'status': 'testing',
                    'current_db': db_config['name'],
                    'progress': i,
                    'total': total_databases
                })
            
            # Configurar ambiente para este database
            if db_config['requires_docker']:
                print(f"📦 Iniciando container {db_config['service']}...")
                if not self.start_specific_container(db_config['service']):
                    print(f"❌ Falha ao iniciar {db_config['name']}")
                    continue
                
                # Verificar conexão
                if not self.check_database_connection(db_config):
                    print(f"❌ Falha na conexão com {db_config['name']}")
                    continue
                
                # Migrar
                if not self.migrate_database(db_config):
                    print(f"❌ Falha ao migrar {db_config['name']}")
                    continue
            
            # Executar benchmarks
            print(f"⚡ Executando benchmarks para {db_config['name']}...")
            db_results = self.run_database_benchmarks(db_key, db_config, df)
            
            if db_results:
                all_results[db_key] = {
                    'config': db_config,
                    'results': db_results
                }
                print(f"✅ {db_config['name']} concluído com sucesso!")
            else:
                print(f"❌ {db_config['name']} falhou nos testes")
            
            # Parar container após teste
            if db_config['requires_docker']:
                print(f"🛑 Parando container {db_config['service']}...")
                self.stop_all_containers()
                time.sleep(2)
        
        print(f"\n🎉 Benchmark sequencial concluído!")
        return all_results

# Manter compatibilidade
BenchmarkService = SequentialBenchmarkService
AdvancedBenchmarkService = SequentialBenchmarkService