from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView
from .benchmark_service import BenchmarkService
import json

class BenchmarkView(TemplateView):
    template_name = 'benchmark/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'DuckDB Performance Benchmark'
        return context

def run_benchmark(request):
    """API endpoint para executar benchmark"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            num_records = data.get('num_records', 10000)
            
            # Validar número de registros
            if num_records > 100000:
                return JsonResponse({
                    'success': False,
                    'error': 'Número máximo de registros: 100.000'
                })
            
            service = BenchmarkService()
            results = service.run_full_benchmark(num_records)
            
            return JsonResponse({
                'success': True,
                'results': results,
                'summary': generate_summary(results)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def generate_summary(results):
    """Gera resumo dos resultados"""
    summary = {}
    
    # Converter para lista para evitar modificação durante iteração
    results_items = list(results.items())
    
    for test_name, test_results in results_items:
        if isinstance(test_results, dict) and 'duckdb' in test_results:
            # Encontrar tempos de execução
            duckdb_time = test_results['duckdb'].get('execution_time', 0)
            
            # Coletar outros databases
            other_dbs = {}
            test_items = list(test_results.items())
            
            for db_name, db_result in test_items:
                if (db_name != 'duckdb' and 
                    isinstance(db_result, dict) and 
                    'execution_time' in db_result):
                    other_dbs[db_name] = db_result['execution_time']
            
            if other_dbs and duckdb_time > 0:
                # Encontrar o mais lento
                slowest_db = max(other_dbs.items(), key=lambda x: x[1])
                fastest_db = min(other_dbs.items(), key=lambda x: x[1])
                
                summary[test_name] = {
                    'duckdb_time': duckdb_time,
                    'fastest_other': {
                        'database': fastest_db[0],
                        'time': fastest_db[1]
                    },
                    'slowest_other': {
                        'database': slowest_db[0], 
                        'time': slowest_db[1]
                    },
                    'speedup_vs_fastest': fastest_db[1] / duckdb_time if duckdb_time > 0 else 1,
                    'speedup_vs_slowest': slowest_db[1] / duckdb_time if duckdb_time > 0 else 1
                }
    
    return summary