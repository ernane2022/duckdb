# Criar stop-all-databases.ps1
Set-Content -Path "stop-all-databases.ps1" -Encoding UTF8 -Value @"
Write-Host "Parando todos os databases..." -ForegroundColor Red
docker-compose -f docker-compose-databases.yml down
"@

