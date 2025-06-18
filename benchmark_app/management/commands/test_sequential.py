from django.core.management.base import BaseCommand
from benchmark_app.benchmark_service import SequentialBenchmarkService
import json

class Command(BaseCommand):
    help = 'Executa benchmark sequencial via linha de comando'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--records',
            type=int,
            default=10000,
            help='Número de registros para teste (padrão: 10000)'
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Arquivo para salvar resultados JSON'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Exibir logs detalhados'
        )
    
    def handle(self, *args, **options):
        num_records = options['records']
        verbose = options['verbose']
        
        self.stdout.write(
            self.style.SUCCESS(f' Iniciando benchmark sequencial com {num_records:,} registros')
        )
        
        try:
            service = SequentialBenchmarkService()
            results = service.run_sequential_benchmark(num_records=num_records)
            
            # Exibir resumo
            self.stdout.write('\n' + '='*60)
            self.stdout.write(self.style.SUCCESS(' RESUMO DOS RESULTADOS'))
            self.stdout.write('='*60)
            
            for db_key, db_data in results.items():
                config = db_data['config']
                db_results = db_data['results']
                
                self.stdout.write(f"\n{config['icon']} {config['name']}:")
                
                if 'aggregation' in db_results:
                    agg = db_results['aggregation']
                    if agg['status'] == 'success':
                        self.stdout.write(f"   Agregação: {agg['execution_time']:.4f}s")
                    else:
                        self.stdout.write(f"   Agregação: {agg.get('error', 'Erro')}")
                
                if 'filter' in db_results:
                    filt = db_results['filter']
                    if filt['status'] == 'success':
                        self.stdout.write(f"   Filtros: {filt['execution_time']:.4f}s")
                    else:
                        self.stdout.write(f"   Filtros: {filt.get('error', 'Erro')}")
            
            self.stdout.write('\n' + self.style.SUCCESS(' Benchmark concluído!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f' Erro: {str(e)}'))
            raise
