# Script de PowerShell para probar endpoints de Quality Data
param(
    [string]$BaseUrl = "http://localhost:8000/api",
    [string]$Username = "admin",
    [string]$Password = "admin123"
)

# Credenciales específicas para el API
$EMAIL = "eenriquez@alzaperu.com"  # El sistema usa email, no username
$PASSWORD = "Dream7."

Write-Host "🚀 Iniciando pruebas de endpoints Quality Data" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan

# Función para obtener token de autenticación
function Get-AuthToken {
    try {
        $loginData = @{
            email = $EMAIL
            password = $PASSWORD
        } | ConvertTo-Json
        
        $headers = @{
            'Content-Type' = 'application/json'
        }
        
        $response = Invoke-RestMethod -Uri "$BaseUrl/auth/login/" -Method Post -Body $loginData -Headers $headers
        # El sistema devuelve tokens en response.tokens.access
        return $response.tokens.access
    }
    catch {
        Write-Host "❌ Error al obtener token: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Función para hacer peticiones autenticadas
function Invoke-AuthenticatedRequest {
    param(
        [string]$Method,
        [string]$Url,
        [object]$Data = $null,
        [hashtable]$Params = @{}
    )
    
    $token = Get-AuthToken
    if (-not $token) {
        return $null
    }
    
    $headers = @{
        'Authorization' = "Bearer $token"
        'Content-Type' = 'application/json'
    }
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            Headers = $headers
        }
        
        if ($Data) {
            $params.Body = $Data | ConvertTo-Json -Depth 10
        }
        
        if ($Params.Count -gt 0) {
            $params.Uri += "?" + ($Params.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join "&"
        }
        
        return Invoke-RestMethod @params
    }
    catch {
        Write-Host "❌ Error en petición $Method a $Url : $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Probar autenticación
Write-Host "🔐 Probando autenticación..." -ForegroundColor Yellow
$token = Get-AuthToken
if ($token) {
    Write-Host "✅ Autenticación exitosa" -ForegroundColor Green
} else {
    Write-Host "❌ Fallo en autenticación" -ForegroundColor Red
    exit 1
}

# Probar listar datos de calidad
Write-Host "`n📋 Probando listar datos de calidad..." -ForegroundColor Yellow
$qualityDataUrl = "$BaseUrl/quality-data"
$response = Invoke-AuthenticatedRequest -Method "GET" -Url $qualityDataUrl

if ($response) {
    Write-Host "✅ Datos obtenidos: $($response.results.Count) registros" -ForegroundColor Green
    if ($response.results.Count -gt 0) {
        Write-Host "Primer registro: $($response.results[0].empresa)" -ForegroundColor Cyan
    }
} else {
    Write-Host "❌ Error al obtener datos" -ForegroundColor Red
}

# Probar crear datos de calidad
Write-Host "`n➕ Probando crear datos de calidad..." -ForegroundColor Yellow
$testData = @{
    empresa = "Empresa de Prueba PowerShell"
    fecha_registro = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
    temperatura = 25.5
    humedad = 65.2
    ph = 6.8
    firmeza = 85.0
    solidos_solubles = 12.5
    acidez_titulable = 0.8
    defectos_porcentaje = 2.5
    defectos_descripcion = "Defectos menores en la superficie"
    calibre = "18-20mm"
    color = "Azul intenso"
    calidad_general = "excelente"
    aprobado = $true
    observaciones = "Muestra de prueba creada desde PowerShell"
}

$newRecord = Invoke-AuthenticatedRequest -Method "POST" -Url $qualityDataUrl -Data $testData

if ($newRecord) {
    Write-Host "✅ Datos creados exitosamente" -ForegroundColor Green
    Write-Host "ID: $($newRecord.id)" -ForegroundColor Cyan
    Write-Host "Empresa: $($newRecord.empresa)" -ForegroundColor Cyan
    
    $newId = $newRecord.id
    
    # Probar obtener detalle
    Write-Host "`n🔍 Probando obtener detalle del registro $newId..." -ForegroundColor Yellow
    $detail = Invoke-AuthenticatedRequest -Method "GET" -Url "$qualityDataUrl/$newId/"
    
    if ($detail) {
        Write-Host "✅ Detalle obtenido" -ForegroundColor Green
        Write-Host "Empresa: $($detail.empresa)" -ForegroundColor Cyan
        Write-Host "Temperatura: $($detail.temperatura)°C" -ForegroundColor Cyan
        Write-Host "Calidad: $($detail.calidad_general)" -ForegroundColor Cyan
    }
    
    # Probar actualizar datos
    Write-Host "`n✏️ Probando actualizar registro $newId..." -ForegroundColor Yellow
    $updateData = @{
        temperatura = 26.0
        humedad = 68.0
        observaciones = "Datos actualizados desde PowerShell"
    }
    
    $updated = Invoke-AuthenticatedRequest -Method "PUT" -Url "$qualityDataUrl/$newId/" -Data $updateData
    
    if ($updated) {
        Write-Host "✅ Datos actualizados" -ForegroundColor Green
        Write-Host "Nueva temperatura: $($updated.temperatura)°C" -ForegroundColor Cyan
    }
} else {
    Write-Host "❌ Error al crear datos" -ForegroundColor Red
}

# Probar filtros
Write-Host "`n🔍 Probando filtros..." -ForegroundColor Yellow

# Filtro por empresa
$filterParams = @{ empresa = "Empresa de Prueba PowerShell" }
$filtered = Invoke-AuthenticatedRequest -Method "GET" -Url $qualityDataUrl -Params $filterParams

if ($filtered) {
    Write-Host "✅ Filtro por empresa: $($filtered.results.Count) resultados" -ForegroundColor Green
}

# Filtro por calidad
$filterParams = @{ calidad_general = "excelente" }
$filtered = Invoke-AuthenticatedRequest -Method "GET" -Url $qualityDataUrl -Params $filterParams

if ($filtered) {
    Write-Host "✅ Filtro por calidad: $($filtered.results.Count) resultados" -ForegroundColor Green
}

# Probar estadísticas
Write-Host "`n📊 Probando estadísticas..." -ForegroundColor Yellow
$stats = Invoke-AuthenticatedRequest -Method "GET" -Url "$qualityDataUrl/stats/"

if ($stats) {
    Write-Host "✅ Estadísticas obtenidas" -ForegroundColor Green
    Write-Host "Total registros: $($stats.total_records)" -ForegroundColor Cyan
    Write-Host "Promedio temperatura: $($stats.avg_temperature)°C" -ForegroundColor Cyan
}

# Probar dashboard
Write-Host "`n📈 Probando dashboard..." -ForegroundColor Yellow
$dashboard = Invoke-AuthenticatedRequest -Method "GET" -Url "$qualityDataUrl/dashboard/"

if ($dashboard) {
    Write-Host "✅ Dashboard obtenido" -ForegroundColor Green
    Write-Host "Datos del dashboard: $($dashboard.Count) elementos" -ForegroundColor Cyan
}

# Probar sincronización
Write-Host "`n🔄 Probando sincronización con API externa..." -ForegroundColor Yellow
$sync = Invoke-AuthenticatedRequest -Method "POST" -Url "$qualityDataUrl/sync/"

if ($sync) {
    Write-Host "✅ Sincronización exitosa" -ForegroundColor Green
    Write-Host "Mensaje: $($sync.message)" -ForegroundColor Cyan
}

# Probar exportación
Write-Host "`n📤 Probando exportación..." -ForegroundColor Yellow
try {
    $export = Invoke-RestMethod -Uri "$qualityDataUrl/export/" -Method "GET" -Headers @{ 'Authorization' = "Bearer $token" }
    Write-Host "✅ Exportación exitosa" -ForegroundColor Green
} catch {
    Write-Host "❌ Error en exportación: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n" + ("=" * 50) -ForegroundColor Cyan
Write-Host "✅ Pruebas completadas" -ForegroundColor Green
Write-Host "🌐 Puedes ver los datos en: $qualityDataUrl" -ForegroundColor Cyan
Write-Host "🔧 Admin panel: $($BaseUrl.Replace('/api', ''))/admin/" -ForegroundColor Cyan
