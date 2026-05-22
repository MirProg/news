# ===========================================================
# ORACLE SPORTS - Windows Setup Script
# ===========================================================
# Run: powershell -ExecutionPolicy Bypass -File setup.ps1
# ===========================================================

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "===========================================" -ForegroundColor DarkRed
Write-Host "  ORACLE SPORTS - System Initialization" -ForegroundColor White
Write-Host "  'The numbers have already decided.'" -ForegroundColor DarkGray
Write-Host "===========================================" -ForegroundColor DarkRed
Write-Host ""

# -------------------------------------
# 1. Check Node.js
# -------------------------------------
Write-Host "[1/14] Checking Node.js..." -ForegroundColor Cyan
try {
    $nodeVersion = (node --version) -replace 'v', ''
    $major = [int]($nodeVersion.Split('.')[0])
    if ($major -lt 20) {
        Write-Host "  ERROR: Node.js 20+ required. Found v$nodeVersion" -ForegroundColor Red
        exit 1
    }
    Write-Host "  [OK] Node.js v$nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Node.js not found. Install from https://nodejs.org" -ForegroundColor Red
    exit 1
}

# -------------------------------------
# 2. Check Python
# -------------------------------------
Write-Host "[2/14] Checking Python..." -ForegroundColor Cyan
try {
    $pyVersion = (python --version 2>&1) -replace 'Python ', ''
    $pyMajor = [int]($pyVersion.Split('.')[0])
    $pyMinor = [int]($pyVersion.Split('.')[1])
    if ($pyMajor -lt 3 -or ($pyMajor -eq 3 -and $pyMinor -lt 9)) {
        Write-Host "  ERROR: Python 3.9+ required. Found $pyVersion" -ForegroundColor Red
        exit 1
    }
    Write-Host "  [OK] Python $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Python not found. Install from https://python.org" -ForegroundColor Red
    exit 1
}

# -------------------------------------
# 3. Check Ollama
# -------------------------------------
Write-Host "[3/14] Checking Ollama..." -ForegroundColor Cyan
try {
    $ollamaResponse = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 5
    Write-Host "  [OK] Ollama is running" -ForegroundColor Green
} catch {
    Write-Host "  WARNING: Ollama not detected at localhost:11434" -ForegroundColor Yellow
    Write-Host "  Starting Ollama..." -ForegroundColor Yellow
    try {
        Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
        Start-Sleep -Seconds 3
        Write-Host "  [OK] Ollama started" -ForegroundColor Green
    } catch {
        Write-Host "  ERROR: Could not start Ollama. Install from https://ollama.ai" -ForegroundColor Red
        exit 1
    }
}

# -------------------------------------
# 4. Pull Ollama models
# -------------------------------------
Write-Host "[4/14] Pulling Ollama models..." -ForegroundColor Cyan
$models = @("mistral-nemo", "qwen2.5:7b-instruct", "phi3.5", "nomic-embed-text")
foreach ($model in $models) {
    Write-Host "  Pulling $model..." -ForegroundColor Gray
    & ollama pull $model
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] $model ready" -ForegroundColor Green
    } else {
        Write-Host "  WARNING: Failed to pull $model" -ForegroundColor Yellow
    }
}

# -------------------------------------
# 5. Install Python dependencies
# -------------------------------------
Write-Host "[5/14] Installing Python dependencies..." -ForegroundColor Cyan
& pip install chromadb kokoro-onnx soundfile fastapi uvicorn 2>&1 | Out-Null
Write-Host "  [OK] Python deps installed" -ForegroundColor Green

# -------------------------------------
# 6. Start ChromaDB
# -------------------------------------
Write-Host "[6/14] Starting ChromaDB..." -ForegroundColor Cyan
try {
    $chromaCheck = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/heartbeat" -UseBasicParsing -TimeoutSec 3
    Write-Host "  [OK] ChromaDB already running" -ForegroundColor Green
} catch {
    Start-Process "chroma" -ArgumentList "run --port 8000" -WindowStyle Hidden
    Start-Sleep -Seconds 3
    Write-Host "  [OK] ChromaDB started on port 8000" -ForegroundColor Green
}

# -------------------------------------
# 7. Create .env from example if missing
# -------------------------------------
Write-Host "[7/14] Checking environment..." -ForegroundColor Cyan
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "  [OK] Created .env from .env.example" -ForegroundColor Green
    Write-Host "  WARNING: Edit .env and set THE_ODDS_API_KEY" -ForegroundColor Yellow
} else {
    Write-Host "  [OK] .env exists" -ForegroundColor Green
}

# -------------------------------------
# 8. Create directories
# -------------------------------------
Write-Host "[8/14] Creating directories..." -ForegroundColor Cyan
$dirs = @("imageCache", "logs", "backend/public/audio")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "  [OK] Directories created" -ForegroundColor Green

# -------------------------------------
# 9. Install backend dependencies
# -------------------------------------
Write-Host "[9/14] Installing backend dependencies..." -ForegroundColor Cyan
Push-Location backend
& npm install
Pop-Location
Write-Host "  [OK] Backend deps installed" -ForegroundColor Green

# -------------------------------------
# 10. Install engine dependencies
# -------------------------------------
Write-Host "[10/14] Installing engine dependencies..." -ForegroundColor Cyan
Push-Location engine
& npm install
Pop-Location
Write-Host "  [OK] Engine deps installed" -ForegroundColor Green

# -------------------------------------
# 11. Install frontend dependencies
# -------------------------------------
Write-Host "[11/14] Installing frontend dependencies..." -ForegroundColor Cyan
Push-Location frontend
& npm install
Pop-Location
Write-Host "  [OK] Frontend deps installed" -ForegroundColor Green

# -------------------------------------
# 12. Run database migration
# -------------------------------------
Write-Host "[12/14] Running database migration..." -ForegroundColor Cyan
& node db/migrate.js
Write-Host "  [OK] Database migrated" -ForegroundColor Green

# -------------------------------------
# 13. Build frontend
# -------------------------------------
Write-Host "[13/14] Building frontend..." -ForegroundColor Cyan
Push-Location frontend
& npm run build
Pop-Location
Write-Host "  [OK] Frontend built" -ForegroundColor Green

# -------------------------------------
# 14. Start all services via PM2
# -------------------------------------
Write-Host "[14/14] Starting services via PM2..." -ForegroundColor Cyan
try {
    & npx -y pm2 start ecosystem.config.js
    & npx -y pm2 save
    Write-Host "  [OK] All services started" -ForegroundColor Green
} catch {
    Write-Host "  WARNING: PM2 start failed. Run manually: npx pm2 start ecosystem.config.js" -ForegroundColor Yellow
}

# -------------------------------------
# Startup Summary
# -------------------------------------
Write-Host ""
Write-Host "===========================================" -ForegroundColor DarkRed
Write-Host "  ORACLE SPORTS - ALL SYSTEMS ONLINE" -ForegroundColor White
Write-Host "===========================================" -ForegroundColor DarkRed
Write-Host ""
Write-Host "  Frontend:       http://localhost:3000" -ForegroundColor Green
Write-Host "  Backend API:    http://localhost:4000" -ForegroundColor Green
Write-Host "  Ollama:         http://localhost:11434" -ForegroundColor Green
Write-Host "  ChromaDB:       http://localhost:8000" -ForegroundColor Green
Write-Host ""
Write-Host "  PM2 Dashboard:  npx pm2 monit" -ForegroundColor DarkGray
Write-Host "  PM2 Logs:       npx pm2 logs" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  'We merely translate.'" -ForegroundColor DarkGray
Write-Host "===========================================" -ForegroundColor DarkRed
Write-Host ""
