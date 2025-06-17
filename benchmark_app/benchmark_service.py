import time
import duckdb
import pandas as pd
from django.db import models, connections
from django.conf import settings
from .models import SalesRecord
import random
from faker import Faker
import logging

logger = logging.getLogger(__name__)

class AdvancedBenchmarkService:
    def __init__(self):
        self.fake = Faker('pt_BR')
        self.duckdb_conn = duckdb.connect(':memory:')
        self.available_databases = self.check_all_databases()
    
    def check_all_databases(self):
        """Verifica todos os databases disponíveis com timeout"""
        available = ['default']  # SQLite sempre disponível
        
        databases_to_test = {
            'postgresql': '🐘 PostgreSQL',
            'mysql': '🐬 MySQL',
            'mariadb': '🗃️ MariaDB',
            'cockroachdb': '🪳 CockroachDB'
        }
        
        for db_name, display_name in databases_to_test.items():
            if db_name in settings.DATABASES:
                try:
                    # Configurar timeout
                    connection = connections[db_name]
                    connection.ensure_connection()
                    
                    # Teste simples
                    cursor = connection.cursor()
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                    
                    available.append(db_name)
                    print(f"✅ {display_name} disponível")
                    
                except Exception as e:
                    print(f"❌ {display_name} não disponível: {str(e)[:100]}...")
        
        return available
    
    def generate_test_data(self, num_records=10000):
        """Gera dados de teste para benchmark"""
        print(f"Gerando {num_records} registros de teste...")
        
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
        print("Configurando dados no DuckDB...")
        
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
            
            # Inserir dados do DataFrame
            self.duckdb_conn.execute("INSERT INTO sales_record SELECT * FROM df")
            
            # Verificar quantos registros foram inseridos
            count = self.duckdb_conn.execute("SELECT COUNT(*) FROM sales_record").fetchone()[0]
            print(f"DuckDB: {count} registros inseridos")
            return True
            
        except Exception as e:
            print(f"Erro no DuckDB: {e}")
            return False
    
    def setup_django_data(self, df, databases=None):
        """Insere dados no Django ORM para múltiplos databases"""
        if databases is None:
            databases = self.available_databases
        
        successful_dbs = []
        
        for db_name in databases:
            if db_name in self.available_databases:
                print(f"Inserindo dados no {db_name}...")
                
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
                    
                    # Inserir registros restantes
                    if records:
                        SalesRecord.objects.using(db_name).bulk_create(records, ignore_conflicts=True)
                    
                    # Verificar quantos registros foram inseridos
                    count = SalesRecord.objects.using(db_name).count()
                    print(f"{db_name}: {count} registros inseridos")
                    successful_dbs.append(db_name)
                    
                except Exception as e:
                    print(f"Erro ao inserir dados no {db_name}: {e}")
        
        return successful_dbs
    
    def run_query_benchmark(self, query_name, query_sql, databases=None):
        """Executa benchmark genérico para uma query"""
        if databases is None:
            databases = self.available_databases
        
        results = {}
        
        # DuckDB
        try:
            start_time = time.time()
            duckdb_result = self.duckdb_conn.execute(query_sql['duckdb']).fetchall()
            duckdb_time = time.time() - start_time
            
            results['duckdb'] = {
                'execution_time': duckdb_time,
                'rows_returned': len(duckdb_result),
                'query_type': query_name,
                'status': 'success'
            }
        except Exception as e:
            results['duckdb'] = {
                'execution_time': None,
                'rows_returned': 0,
                'query_type': query_name,
                'status': 'error',
                'error': str(e)
            }
        
        # Outros databases
        for db_name in databases:
            if db_name == 'default':
                db_display = 'sqlite'
            else:
                db_display = db_name
            
            # ORM Query
            try:
                start_time = time.time()
                orm_result = list(query_sql['orm'](db_name))
                orm_time = time.time() - start_time
                
                results[f'{db_display}_orm'] = {
                    'execution_time': orm_time,
                    'rows_returned': len(orm_result),
                    'query_type': query_name,
                    'status': 'success'
                }
            except Exception as e:
                results[f'{db_display}_orm'] = {
                    'execution_time': None,
                    'rows_returned': 0,
                    'query_type': query_name,
                    'status': 'error',
                    'error': str(e)
                }
            
            # Raw SQL Query
            try:
                start_time = time.time()
                cursor = connections[db_name].cursor()
                cursor.execute(query_sql['raw_sql'])
                raw_result = cursor.fetchall()
                raw_time = time.time() - start_time
                
                results[f'{db_display}_raw'] = {
                    'execution_time': raw_time,
                    'rows_returned': len(raw_result),
                    'query_type': query_name,
                    'status': 'success'
                }
            except Exception as e:
                results[f'{db_display}_raw'] = {
                    'execution_time': None,
                    'rows_returned': 0,
                    'query_type': query_name,
                    'status': 'error',
                    'error': str(e)
                }
        
        return results
    
    def benchmark_aggregation_queries(self, databases=None):
        """Benchmark de queries de agregação"""
        query_sql = {
            'duckdb': """
                SELECT category, 
                       COUNT(*) as total_sales,
                       SUM(price * quantity) as total_revenue,
                       AVG(price) as avg_price,
                       MIN(price) as min_price,
                       MAX(price) as max_price
                FROM sales_record 
                GROUP BY category 
                ORDER BY total_revenue DESC
            """,
            'raw_sql': """
                SELECT category, 
                       COUNT(*) as total_sales,
                       SUM(price * quantity) as total_revenue,
                       AVG(price) as avg_price,
                       MIN(price) as min_price,
                       MAX(price) as max_price
                FROM benchmark_app_salesrecord 
                GROUP BY category 
                ORDER BY total_revenue DESC
            """,
            'orm': lambda db: SalesRecord.objects.using(db).values('category').annotate(
                total_sales=models.Count('id'),
                total_revenue=models.Sum(models.F('price') * models.F('quantity')),
                avg_price=models.Avg('price'),
                min_price=models.Min('price'),
                max_price=models.Max('price')
            ).order_by('-total_revenue')
        }
        
        return self.run_query_benchmark('aggregation', query_sql, databases)
    
    def benchmark_filter_queries(self, databases=None):
        """Benchmark de queries com filtros"""
        query_sql = {
            'duckdb': """
                SELECT category, region, salesperson, price, quantity, sale_date
                FROM sales_record 
                WHERE price > 1000 AND quantity > 5
                ORDER BY price DESC, sale_date DESC
                LIMIT 200
            """,
            'raw_sql': """
                SELECT category, region, salesperson, price, quantity, sale_date
                FROM benchmark_app_salesrecord 
                WHERE price > 1000 AND quantity > 5
                ORDER BY price DESC, sale_date DESC
                LIMIT 200
            """,
            'orm': lambda db: SalesRecord.objects.using(db).filter(
                price__gt=1000,
                quantity__gt=5
            ).order_by('-price', '-sale_date')[:200]
        }
        
        return self.run_query_benchmark('filter', query_sql, databases)
    
    def benchmark_complex_queries(self, databases=None):
        """Benchmark de queries complexas"""
        query_sql = {
            'duckdb': """
                SELECT 
                    region,
                    category,
                    COUNT(*) as sales_count,
                    SUM(price * quantity) as total_revenue,
                    AVG(price * quantity) as avg_order_value,
                    COUNT(DISTINCT customer_id) as unique_customers,
                    SUM(quantity) as total_quantity
                FROM sales_record 
                WHERE sale_date >= '2023-01-01'
                GROUP BY region, category
                HAVING COUNT(*) > 10
                ORDER BY total_revenue DESC
                LIMIT 50
            """,
            'raw_sql': """
                SELECT 
                    region,
                    category,
                    COUNT(*) as sales_count,
                    SUM(price * quantity) as total_revenue,
                    AVG(price * quantity) as avg_order_value,
                    COUNT(DISTINCT customer_id) as unique_customers,
                    SUM(quantity) as total_quantity
                FROM benchmark_app_salesrecord 
                WHERE sale_date >= '2023-01-01'
                GROUP BY region, category
                HAVING COUNT(*) > 10
                ORDER BY total_revenue DESC
                LIMIT 50
            """,
            'orm': lambda db: SalesRecord.objects.using(db).filter(
                sale_date__gte='2023-01-01'
            ).values('region', 'category').annotate(
                sales_count=models.Count('id'),
                total_revenue=models.Sum(models.F('price') * models.F('quantity')),
                avg_order_value=models.Avg(models.F('price') * models.F('quantity')),
                unique_customers=models.Count('customer_id', distinct=True),
                total_quantity=models.Sum('quantity')
            ).filter(sales_count__gt=10).order_by('-total_revenue')[:50]
        }
        
        return self.run_query_benchmark('complex', query_sql, databases)
    
    def run_full_benchmark(self, num_records=10000):
        """Executa benchmark completo"""
        print(f"Iniciando benchmark completo com {num_records} registros...")
        print(f"Databases disponíveis: {', '.join(self.available_databases)}")
        
        # Gerar dados de teste
        df = self.generate_test_data(num_records)
        
        # Setup databases
        duckdb_success = self.setup_duckdb_data(df)
        successful_dbs = self.setup_django_data(df)
        
        if not duckdb_success and not successful_dbs:
            raise Exception("Nenhum database foi configurado com sucesso")
        
        # Executar benchmarks
        results = {}
        
        print("Executando benchmark de agregação...")
        results['aggregation'] = self.benchmark_aggregation_queries(successful_dbs)
        
        print("Executando benchmark de filtros...")
        results['filter'] = self.benchmark_filter_queries(successful_dbs)
        
        print("Executando benchmark de queries complexas...")
        results['complex'] = self.benchmark_complex_queries(successful_dbs)
        
        # Calcular estatísticas
        self.calculate_performance_stats(results)
        
        return results
    
    def calculate_performance_stats(self, results):
        """Calcula estatísticas de performance"""
        for test_name, test_results in results.items():
            successful_results = {k: v for k, v in test_results.items() 
                                if v.get('status') == 'success' and v.get('execution_time') is not None}
            
            if successful_results:
                times = [v['execution_time'] for v in successful_results.values()]
                fastest = min(times)
                slowest = max(times)
                
                print(f"\n{test_name.upper()} - Estatísticas:")
                for db_name, result in successful_results.items():
                    if result['execution_time'] == fastest:
                        speedup = 1.0
                        status = "🏆 MAIS RÁPIDO"
                    else:
                        speedup = result['execution_time'] / fastest
                        status = f"{speedup:.2f}x mais lento"
                    
                    print(f"  {db_name}: {result['execution_time']:.4f}s ({status})")

# Manter compatibilidade com versão anterior
BenchmarkService = AdvancedBenchmarkService