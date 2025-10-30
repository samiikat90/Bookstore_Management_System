# PowerShell script to quickly start the bookstore application
Write-Host "=" -NoNewline; Write-Host ("=" * 59)
Write-Host "CHAPTER 6: A PLOT TWIST - QUICK START" -ForegroundColor Green
Write-Host "=" -NoNewline; Write-Host ("=" * 59)

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

# Check database status
Write-Host "Checking database status..." -ForegroundColor Cyan
python scripts/db_status.py

Write-Host ""
Write-Host "Starting Flask application..." -ForegroundColor Green
Write-Host "Visit: http://127.0.0.1:5000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Login credentials:" -ForegroundColor Cyan
Write-Host "  Username: admin  | Password: admin123" -ForegroundColor White
Write-Host "  Username: manager1 | Password: manager123" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Red
Write-Host ""

# Start the Flask app
python app/app.py