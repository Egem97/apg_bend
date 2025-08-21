#!/bin/bash

# Script de despliegue rápido para Agro Backend
set -e

echo "🚀 Iniciando despliegue de Agro Backend con Docker..."

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor instala Docker primero."
    exit 1
fi

# Verificar si Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado. Por favor instala Docker Compose primero."
    exit 1
fi

# Verificar si el archivo .env existe, si no, crear desde el ejemplo
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env desde env.example..."
    cp env.example .env
    echo "✅ Archivo .env creado. Puedes editarlo si necesitas personalizar la configuración."
fi

# Detener contenedores existentes si los hay
echo "🛑 Deteniendo contenedores existentes..."
docker-compose down 2>/dev/null || true

# Limpiar imágenes antiguas (opcional)
read -p "¿Quieres limpiar imágenes Docker antiguas? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 Limpiando imágenes antiguas..."
    docker system prune -f
fi

# Construir y ejecutar
echo "🔨 Construyendo y ejecutando contenedores..."
docker-compose up --build -d

# Esperar a que el contenedor esté listo
echo "⏳ Esperando a que la aplicación esté lista..."
sleep 10

# Verificar el estado del contenedor
if docker-compose ps | grep -q "Up"; then
    echo "✅ ¡Despliegue exitoso!"
    echo ""
    echo "🌐 URLs de acceso:"
    echo "   - API REST: http://localhost:8000/api/"
    echo "   - Admin Django: http://localhost:8000/admin/"
    echo "   - Documentación API: http://localhost:8000/api/docs/"
    echo ""
    echo "🔑 Credenciales por defecto:"
    echo "   - Usuario: admin"
    echo "   - Contraseña: admin123"
    echo ""
    echo "📋 Comandos útiles:"
    echo "   - Ver logs: docker-compose logs -f web"
    echo "   - Detener: docker-compose down"
    echo "   - Reiniciar: docker-compose restart"
    echo ""
    echo "📊 Estado del contenedor:"
    docker-compose ps
else
    echo "❌ Error en el despliegue. Revisa los logs:"
    docker-compose logs web
    exit 1
fi
