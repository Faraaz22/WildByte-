# Quick Start Script for AI Data Dictionary Backend
# This script helps you get started quickly

Write-Host "🚀 AI Data Dictionary - Quick Start" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
    Write-Host ""
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"
Write-Host ""

# Check if requirements are installed
Write-Host "📚 Checking dependencies..." -ForegroundColor Yellow
$pipList = pip list
if ($pipList -notmatch "fastapi") {
    Write-Host "📥 Installing dependencies (this may take a few minutes)..." -ForegroundColor Yellow
    pip install -r requirements.txt
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✅ Dependencies already installed" -ForegroundColor Green
}
Write-Host ""

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  No .env file found!" -ForegroundColor Red
    Write-Host "📝 Creating .env from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    
    Write-Host ""
    Write-Host "🔑 Generating secure keys..." -ForegroundColor Yellow
    python scripts/generate_keys.py
    Write-Host ""
    
    Write-Host "⚠️  IMPORTANT: Edit .env file and update:" -ForegroundColor Yellow
    Write-Host "   - ENCRYPTION_KEY (copy from output above)" -ForegroundColor Yellow
    Write-Host "   - JWT_SECRET_KEY (copy from output above)" -ForegroundColor Yellow
    Write-Host "   - OPENAI_API_KEY (your OpenAI API key)" -ForegroundColor Yellow
    Write-Host "   - DATABASE_URL (if different from default)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press Enter after you've updated the .env file..." -ForegroundColor Cyan
    Read-Host
}

# Check if database is initialized
Write-Host "🗄️  Checking database..." -ForegroundColor Yellow
$dbInitPrompt = Read-Host "Do you want to initialize the database? (y/N)"
if ($dbInitPrompt -eq "y" -or $dbInitPrompt -eq "Y") {
    Write-Host "📊 Initializing database..." -ForegroundColor Yellow
    python scripts/init_db.py
    Write-Host ""
}

# Start the application
Write-Host ""
Write-Host "🎉 Starting the application..." -ForegroundColor Green
Write-Host ""
Write-Host "📍 API will be available at:" -ForegroundColor Cyan
Write-Host "   - Main API: http://localhost:8000" -ForegroundColor White
Write-Host "   - Interactive Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   - Alternative Docs: http://localhost:8000/redoc" -ForegroundColor White
Write-Host ""
Write-Host "🔐 Default credentials:" -ForegroundColor Cyan
Write-Host "   - Email: admin@example.com" -ForegroundColor White
Write-Host "   - Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python src/main.py
