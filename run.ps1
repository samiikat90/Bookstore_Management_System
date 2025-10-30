# Run.ps1 - helper to create venv, install deps, and run the app (Windows PowerShell)
param(
    [switch]$setup
)

if($setup){
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    Write-Host "Setup complete. Activate the venv with: .\venv\Scripts\Activate.ps1"
    return
}

if(-not (Test-Path ".\venv\Scripts\python.exe")){
    Write-Host "No virtualenv found. Run: .\run.ps1 -setup" -ForegroundColor Yellow
    exit 1
}

.\venv\Scripts\Activate.ps1
python -m app.app
