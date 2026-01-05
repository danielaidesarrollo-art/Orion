# Script para copiar el archivo Excel de triage al proyecto Orion Core
# Ejecutar desde PowerShell

$origenCarpeta = "$env:USERPROFILE\Desktop\triage de urgencias"
$destinoProyecto = "C:\Users\johan\.gemini\antigravity\scratch\orion-core\data"

Write-Host "🔍 Buscando archivos Excel en: $origenCarpeta" -ForegroundColor Cyan

# Buscar archivos Excel
$archivosExcel = Get-ChildItem -Path $origenCarpeta -Filter "*.xlsx" -ErrorAction SilentlyContinue

if ($archivosExcel) {
    Write-Host "✅ Archivos encontrados:" -ForegroundColor Green
    $archivosExcel | ForEach-Object {
        Write-Host "  - $($_.Name)" -ForegroundColor Yellow
    }
    
    # Copiar el primer archivo Excel encontrado
    $archivoOrigen = $archivosExcel[0].FullName
    $archivoDestino = Join-Path $destinoProyecto "triage_urgencias.xlsx"
    
    Write-Host "`n📋 Copiando archivo..." -ForegroundColor Cyan
    Copy-Item -Path $archivoOrigen -Destination $archivoDestino -Force
    
    Write-Host "✅ Archivo copiado exitosamente a:" -ForegroundColor Green
    Write-Host "   $archivoDestino" -ForegroundColor Yellow
    
    # Mostrar información del archivo
    $info = Get-Item $archivoDestino
    Write-Host "`n📊 Información del archivo:" -ForegroundColor Cyan
    Write-Host "   Tamaño: $([math]::Round($info.Length / 1KB, 2)) KB" -ForegroundColor White
    Write-Host "   Modificado: $($info.LastWriteTime)" -ForegroundColor White
    
} else {
    Write-Host "❌ No se encontraron archivos Excel en la carpeta" -ForegroundColor Red
    Write-Host "   Ruta buscada: $origenCarpeta" -ForegroundColor Yellow
    Write-Host "`n💡 Verifica que:" -ForegroundColor Cyan
    Write-Host "   1. La carpeta existe en el Desktop" -ForegroundColor White
    Write-Host "   2. Contiene archivos .xlsx" -ForegroundColor White
}
