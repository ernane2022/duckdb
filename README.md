# Django DuckDB Benchmark

Um projeto de benchmark para comparar performance entre Django ORM tradicional e DuckDB em operações analíticas e consultas complexas.

## 📋 Sobre o Projeto

Este benchmark foi desenvolvido para avaliar e comparar o desempenho entre:
- **Django ORM** com PostgreSQL/SQLite
- **DuckDB** como banco de dados analítico
- Operações híbridas Django + DuckDB

## 🎯 Objetivos

- Comparar tempos de execução em consultas analíticas
- Avaliar performance em agregações complexas
- Medir eficiência no processamento de grandes datasets
- Identificar casos de uso ideais para cada abordagem

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+**
- **Django 4.2+**
- **DuckDB** - Banco de dados analítico em memória
- **PostgreSQL** - Para comparação com Django ORM
- **Pandas** - Para manipulação de dados
- **Matplotlib/Plotly** - Para visualização dos resultados

## 📊 Tipos de Benchmark

### 1. Operações de Agregação
- COUNT, SUM, AVG, MAX, MIN
- GROUP BY com múltiplas dimensões
- Consultas com HAVING

### 2. Consultas Analíticas
- Window functions
- CTEs (Common Table Expressions)
- Subconsultas complexas

### 3. Operações de JOIN
- INNER JOIN
- LEFT/RIGHT JOIN
- Múltiplos JOINs

### 4. Processamento de Grandes Volumes
- Datasets de 100K+ registros
- Operações de ETL
- Análises temporais

## 🚀 Como Executar

### Pré-requisitos

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar banco de dados
python manage.py migrate

# Gerar dados de teste
python manage.py generate_test_data
```

### Executando os Benchmarks

```bash
# Executar todos os benchmarks
python manage.py run_benchmark

# Executar benchmark específico
python manage.py run_benchmark --test=aggregation

# Gerar relatório
python manage.py generate_report
```

## 📈 Estrutura dos Dados

```python
# Exemplo de modelo para benchmark
class SalesRecord(models.Model):
    date = models.DateField()
    product_id = models.IntegerField()
    category = models.CharField(max_length=50)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    region = models.CharField(max_length=50)
```

## 📋 Comandos Disponíveis

```bash
# Gerar dados de teste
python manage.py generate_test_data --size=100000

# Executar benchmark de agregação
python manage.py benchmark_aggregation

# Executar benchmark de joins
python manage.py benchmark_joins

# Limpar dados de teste
python manage.py cleanup_test_data

# Exportar resultados
python manage.py export_results --format=json
```

## 📊 Resultados Esperados

O benchmark irá gerar métricas como:
- **Tempo de execução** (ms)
- **Uso de memória** (MB)
- **Throughput** (registros/segundo)
- **Escalabilidade** por tamanho do dataset

## 🔧 Configuração

### settings.py
```python
# Configurações específicas do benchmark
BENCHMARK_SETTINGS = {
    'DUCKDB_PATH': ':memory:',  # ou caminho para arquivo
    'TEST_DATA_SIZE': 100000,
    'REPEAT_COUNT': 5,
    'EXPORT_FORMAT': 'json'
}
```

### requirements.txt
```txt
Django>=4.2.0
duckdb>=0.8.0
pandas>=1.5.0
psycopg2-binary>=2.9.0
matplotlib>=3.6.0
plotly>=5.11.0
```

## 📁 Estrutura do Projeto

```
django-duckdb-benchmark/
├── benchmark/
│   ├── management/
│   │   └── commands/
│   ├── models.py
│   ├── duckdb_queries.py
│   └── django_queries.py
├── data/
│   └── test_datasets/
├── results/
│   ├── reports/
│   └── charts/
├── static/
├── templates/
├── manage.py
├── requirements.txt
└── README.md
```

## 🎯 Casos de Uso Testados

### 1. E-commerce Analytics
- Análise de vendas por período
- Top produtos por categoria
- Análise de comportamento do cliente

### 2. Financial Data Processing
- Cálculos de métricas financeiras
- Análise de séries temporais
- Agregações por período

### 3. Log Analysis
- Processamento de logs de aplicação
- Análise de performance
- Detecção de padrões

## 📈 Monitoramento de Performance

O projeto inclui:
- Profiling detalhado de consultas
- Medição de uso de CPU e memória
- Análise de planos de execução
- Comparação de índices

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 To-Do

- [ ] Implementar benchmark com Apache Arrow
- [ ] Adicionar suporte a ClickHouse
- [ ] Criar dashboard web interativo
- [ ] Implementar testes automatizados
- [ ] Adicionar mais tipos de consultas analíticas

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Autor

**Ernane** - [@ernane2022](https://github.com/ernane2022)

## 🔗 Links Úteis

- [DuckDB Documentation](https://duckdb.org/docs/)
- [Django ORM Documentation](https://docs.djangoproject.com/en/stable/topics/db/)
- [DB Benchmark Project](https://duckdblabs.github.io/db-benchmark/)

---

⭐ Se este projeto foi útil para você, considere dar uma estrela no repositório!