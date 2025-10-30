# PowerShell script to reset and populate the database with sample data
Write-Host "=" -NoNewline; Write-Host ("=" * 59)
Write-Host "CHAPTER 6: A PLOT TWIST - DATABASE RESET & SETUP"
Write-Host "=" -NoNewline; Write-Host ("=" * 59)

$projectRoot = Split-Path -Parent $PSScriptRoot

# Change to project directory
Set-Location $projectRoot

Write-Host "Resetting database and setting up sample data..."
Write-Host ""

# Remove existing database
$dbPath = Join-Path $projectRoot "instance\inventory.db"
if (Test-Path $dbPath) {
    Write-Host "Removing existing database..." -ForegroundColor Yellow
    Remove-Item $dbPath -Force
}

# Run the setup script
Write-Host "Creating new database with sample data..." -ForegroundColor Green
python scripts/setup_database.py

Write-Host ""
Write-Host "=" -NoNewline; Write-Host ("=" * 59)
Write-Host "DATABASE RESET COMPLETE!" -ForegroundColor Green
Write-Host "=" -NoNewline; Write-Host ("=" * 59)
Write-Host ""
Write-Host "To start your bookstore:" -ForegroundColor Cyan
Write-Host "  1. Run: python app/app.py" -ForegroundColor White
Write-Host "  2. Visit: http://127.0.0.1:5000" -ForegroundColor White
Write-Host "  3. Login with: admin / admin123" -ForegroundColor White
Write-Host ""