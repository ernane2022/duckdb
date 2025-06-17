# setup-all-databases.ps1
Write-Host "🚀 Configurando ambiente completo de benchmark" -ForegroundColor Green

# 1. Instalar dependências
Write-Host "📦 Instalando dependências..." -ForegroundColor Cyan
pip install -r requirements.txt

# 2. Iniciar todos os databases
Write-Host "🐳 Iniciando containers dos databases..." -ForegroundColor Blue
docker-compose -f docker-compose-databases.yml up -d

# 3. Aguardar databases iniciarem
Write-Host "⏳ Aguardando databases iniciarem (60 segundos)..." -ForegroundColor Yellow
Start-Sleep 60

# 4. Verificar health dos containers
Write-Host "🔍 Verificando status dos databases..." -ForegroundColor Magenta
docker-compose -f docker-compose-databases.yml ps

# 5. Executar migrações para todos os databases
Write-Host "🗃️ Executando migrações..." -ForegroundColor Cyan

$databases = @("default", "postgresql", "mysql", "mariadb")

foreach ($db in $databases) {
    Write-Host "  Migrando $db..." -ForegroundColor White
    try {
        python manage.py migrate --database=$db
        Write-Host "  ✅ $db migrado com sucesso" -ForegroundColor Green
    }
    catch {
        Write-Host "  ❌ Erro ao migrar $db" -ForegroundColor Red
    }
}

# 6. Testar conectividade
Write-Host "🧪 Testando conectividade dos databases..." -ForegroundColor Green
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'benchmark_project.settings')
django.setup()

from benchmark_app.benchmark_service import AdvancedBenchmarkService
service = AdvancedBenchmarkService()
print('Databases disponíveis:', service.available_databases)
"

# 7. Executar teste rápido
Write-Host "⚡ Executando teste rápido..." -ForegroundColor Yellow
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'benchmark_project.settings')
django.setup()

from benchmark_app.benchmark_service import AdvancedBenchmarkService
service = AdvancedBenchmarkService()
results = service.run_full_benchmark(1000)
print('✅ Teste rápido concluído!')
"

Write-Host "🎉 Setup completo! Execute 'python manage.py runserver' para iniciar." -ForegroundColor Green

# stop-all-databases.ps1
Write-Host "🛑 Parando todos os databases..." -ForegroundColor Red
docker-compose -f docker-compose-databases.yml down

# start-databases.ps1
Write-Host "▶️ Iniciando databases..." -ForegroundColor Green
docker-compose -f docker-compose-databases.yml up -d
Write-Host "⏳ Aguardando inicialização..." -ForegroundColor Yellow
Start-Sleep 30
Write-Host "✅ Databases iniciados!" -ForegroundColor Green

# check-databases.ps1
Write-Host "🔍 Verificando status dos databases..." -ForegroundColor Cyan
docker-compose -f docker-compose-databases.yml ps

Write-Host "`n📊 Testando conectividade..." -ForegroundColor Yellow
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'benchmark_project.settings')
django.setup()

from benchmark_app.benchmark_service import AdvancedBenchmarkService
service = AdvancedBenchmarkService()
print('Databases disponíveis:', service.available_databases)
"