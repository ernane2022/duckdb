# Criar check-databases.ps1
Set-Content -Path "check-databases.ps1" -Encoding UTF8 -Value @"
Write-Host "Verificando status dos databases..." -ForegroundColor Cyan
docker-compose -f docker-compose-databases.yml ps

Write-Host "Testando conectividade..." -ForegroundColor Yellow
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'benchmark_project.settings')
django.setup()

from benchmark_app.benchmark_service import AdvancedBenchmarkService
service = AdvancedBenchmarkService()
print('Databases disponiveis:', service.available_databases)
"
"@