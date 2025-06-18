from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
import json
import time
from .benchmark_service import SequentialBenchmarkService

class BenchmarkView(TemplateView):
    template_name = 'benchmark_app/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'DuckDB Sequential Multi-Database Benchmark'
        return context

@csrf_exempt
@require_POST
def run_sequential_benchmark(request):
    """API endpoint para executar benchmark sequencial"""
    try:
        data = json.loads(request.body)
        num_records = data.get('num_records', 10000)
        
        if num_records < 1000 or num_records > 1000000:
            return JsonResponse({
                'success': False,
                'error': 'Número de registros deve estar entre 1.000 e 1.000.000'
            })
        
        service = SequentialBenchmarkService()
        results = service.run_sequential_benchmark(num_records)
        
        # Transformar resultados para o formato esperado pelo frontend
        formatted_results = {}
        
        for db_key, db_data in results.items():
            config = db_data['config']
            
            # Agregação
            if 'aggregation' in db_data['results']:
                agg_result = db_data['results']['aggregation']
                
                if not 'aggregation' in formatted_results:
                    formatted_results['aggregation'] = {}
                
                formatted_results['aggregation'][db_key] = {
                    'execution_time': agg_result.get('execution_time'),
                    'rows_returned': agg_result.get('rows_returned', 0),
                    'query_type': 'aggregation',
                    'status': agg_result.get('status', 'error'),
                    'db_name': config['name'],
                    'db_icon': config['icon'],
                    'error': agg_result.get('error', None)
                }
            
            # Filtros
            if 'filter' in db_data['results']:
                filter_result = db_data['results']['filter']
                
                if not 'filter' in formatted_results:
                    formatted_results['filter'] = {}
                
                formatted_results['filter'][db_key] = {
                    'execution_time': filter_result.get('execution_time'),
                    'rows_returned': filter_result.get('rows_returned', 0),
                    'query_type': 'filter',
                    'status': filter_result.get('status', 'error'),
                    'db_name': config['name'],
                    'db_icon': config['icon'],
                    'error': filter_result.get('error', None)
                }
        
        return JsonResponse({
            'success': True,
            'results': formatted_results,
            'num_records': num_records,
            'test_type': 'sequential',
            'databases_tested': len(results)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        })

@csrf_exempt
def benchmark_progress_stream(request):
    """Endpoint para streaming de progresso em tempo real"""
    def event_stream():
        try:
            data = json.loads(request.body)
            num_records = data.get('num_records', 10000)
            
            service = SequentialBenchmarkService()
            
            def progress_callback(progress_data):
                yield f"data: {json.dumps(progress_data)}\n\n"
            
            # Iniciar benchmark com callback
            results = service.run_sequential_benchmark(
                num_records, 
                callback=progress_callback
            )
            
            # Enviar resultado final
            yield f"data: {json.dumps({'status': 'completed', 'results': results})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'error': str(e)})}\n\n"
    
    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['Connection'] = 'keep-alive'
    return response

# Manter compatibilidade com endpoint antigo
@csrf_exempt
@require_POST
def run_benchmark(request):
    """Endpoint compatível com versão anterior - agora usa sistema sequencial"""
    return run_sequential_benchmark(request)