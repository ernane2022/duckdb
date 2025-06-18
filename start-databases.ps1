# Criar start-databases.ps1
Set-Content -Path "start-databases.ps1" -Encoding UTF8 -Value @"
Write-Host "Iniciando databases..." -ForegroundColor Green
docker-compose -f docker-compose-databases.yml up -d
Write-Host "Aguardando inicializacao..." -ForegroundColor Yellow
Start-Sleep 30
Write-Host "Databases iniciados!" -ForegroundColor Green
"@
