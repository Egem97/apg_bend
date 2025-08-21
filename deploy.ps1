# Script de despliegue rápido para Agro Backend (Windows PowerShell)
param(
    [switch]$Clean
)

Write-Host "🚀 Iniciando despliegue de Agro Backend con Docker..." -ForegroundColor Green

# Verificar si Docker está instalado
try {
    docker --version | Out-Null
    Write-Host "✅ Docker encontrado" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker no está instalado. Por favor instala Docker Desktop primero." -ForegroundColor Red
    exit 1
}

# Verificar si Docker Compose está instalado
try {
    docker-compose --version | Out-Null
    Write-Host "✅ Docker Compose encontrado" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose no está instalado. Por favor instala Docker Compose primero." -ForegroundColor Red
    exit 1
}

# Verificar si el archivo .env existe, si no, crear desde el ejemplo
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creando archivo .env desde env.example..." -ForegroundColor Yellow
    Copy-Item "env.example" ".env"
    Write-Host "✅ Archivo .env creado. Puedes editarlo si necesitas personalizar la configuración." -ForegroundColor Green
}

# Detener contenedores existentes si los hay
Write-Host "🛑 Deteniendo contenedores existentes..." -ForegroundColor Yellow
try {
    docker-compose down 2>$null
} catch {
    # Ignorar errores si no hay contenedores ejecutándose
}

# Limpiar imágenes antiguas si se solicita
if ($Clean) {
    Write-Host "🧹 Limpiando imágenes antiguas..." -ForegroundColor Yellow
    docker system prune -f
}

# Construir y ejecutar
Write-Host "🔨 Construyendo y ejecutando contenedores..." -ForegroundColor Yellow
docker-compose up --build -d

# Esperar a que el contenedor esté listo
Write-Host "⏳ Esperando a que la aplicación esté lista..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Verificar el estado del contenedor
$containerStatus = docker-compose ps --format "table {{.Name}}\t{{.Status}}"
if ($containerStatus -match "Up") {
    Write-Host "✅ ¡Despliegue exitoso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 URLs de acceso:" -ForegroundColor Cyan
    Write-Host "   - API REST: http://localhost:8000/api/" -ForegroundColor White
    Write-Host "   - Admin Django: http://localhost:8000/admin/" -ForegroundColor White
    Write-Host "   - Documentación API: http://localhost:8000/api/docs/" -ForegroundColor White
    Write-Host ""
    Write-Host "🔑 Credenciales por defecto:" -ForegroundColor Cyan
    Write-Host "   - Usuario: admin" -ForegroundColor White
    Write-Host "   - Contraseña: admin123" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 Comandos útiles:" -ForegroundColor Cyan
    Write-Host "   - Ver logs: docker-compose logs -f web" -ForegroundColor White
    Write-Host "   - Detener: docker-compose down" -ForegroundColor White
    Write-Host "   - Reiniciar: docker-compose restart" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 Estado del contenedor:" -ForegroundColor Cyan
    docker-compose ps
} else {
    Write-Host "❌ Error en el despliegue. Revisa los logs:" -ForegroundColor Red
    docker-compose logs web
    exit 1
}
