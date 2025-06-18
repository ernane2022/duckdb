# setup-all-databases.ps1
Write-Host "Configurando ambiente completo de benchmark" -ForegroundColor Green

# 1. Instalar dependencias
Write-Host "Instalando dependencias..." -ForegroundColor Cyan
pip install -r requirements.txt

# 2. Iniciar todos os databases
Write-Host "Iniciando containers dos databases..." -ForegroundColor Blue
docker-compose -f docker-compose-databases.yml up -d

# 3. Aguardar databases iniciarem
Write-Host "Aguardando databases iniciarem (60 segundos)..." -ForegroundColor Yellow
Start-Sleep 60

# 4. Verificar health dos containers
Write-Host "Verificando status dos databases..." -ForegroundColor Magenta
docker-compose -f docker-compose-databases.yml ps

# 5. Executar migracoes para todos os databases
Write-Host "Executando migracoes..." -ForegroundColor Cyan

$databases = @("default", "postgresql", "mysql", "mariadb")

foreach ($db in $databases) {
    Write-Host "  Migrando $db..." -ForegroundColor White
    try {
        python manage.py migrate --database=$db
        Write-Host "  Sucesso: $db migrado" -ForegroundColor Green
    }
    catch {
        Write-Host "  Erro ao migrar $db" -ForegroundColor Red
    }
}

# 6. Testar conectividade
Write-Host "Testando conectividade dos databases..." -ForegroundColor Green
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'benchmark_project.settings')
django.setup()

from benchmark_app.benchmark_service import AdvancedBenchmarkService
service = AdvancedBenchmarkService()
print('Databases disponiveis:', service.available_databases)
"

# 7. Executar teste rapido
Write-Host "Executando teste rapido..." -ForegroundColor Yellow
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'benchmark_project.settings')
django.setup()

from benchmark_app.benchmark_service import AdvancedBenchmarkService
service = AdvancedBenchmarkService()
results = service.run_full_benchmark(1000)
print('Teste rapido concluido!')
"

Write-Host "Setup completo! Execute 'python manage.py runserver' para iniciar." -ForegroundColor Green
