# ============================================================
#  dev_setup.ps1 — Virtual Environment Setup for Windows
#  RAM needed : ~500 MB
#  Disk needed: ~2 GB
# ============================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║    Secure Doc RAG — Dev Environment (Windows)       ║" -ForegroundColor Cyan
Write-Host "║    Mode: LOCAL  (no Ollama · no Docker · no GPU)    ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$ProjectRoot = $PSScriptRoot
$VenvDir = Join-Path $ProjectRoot "venv"

# ── Python check ──────────────────────────────────────────────────────────
$PythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3\.(9|10|11|12)") {
            $PythonCmd = $cmd
            Write-Host "✅ Using: $ver" -ForegroundColor Green
            break
        }
    } catch {}
}

if (-not $PythonCmd) {
    Write-Host "❌ Python 3.9+ not found. Download from https://python.org" -ForegroundColor Red
    exit 1
}

# ── Create venv ───────────────────────────────────────────────────────────
if (Test-Path $VenvDir) {
    Write-Host "⚠️  venv already exists — skipping creation." -ForegroundColor Yellow
} else {
    Write-Host "`nCreating virtual environment..." -ForegroundColor White
    & $PythonCmd -m venv $VenvDir
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# ── Activate & install ────────────────────────────────────────────────────
$ActivateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
& $ActivateScript

Write-Host "`nInstalling packages (3–5 minutes, ~2 GB download)..." -ForegroundColor White
Write-Host "  torch CPU-only: ~500 MB" -ForegroundColor Yellow
Write-Host "  sentence-transformers model: ~80 MB on first run`n" -ForegroundColor Yellow

pip install --upgrade pip --quiet
pip install torch==2.3.1 --index-url https://download.pytorch.org/whl/cpu --quiet
pip install -r (Join-Path $ProjectRoot "requirements-dev.txt") --quiet

New-Item -ItemType Directory -Force -Path (Join-Path $ProjectRoot "uploads") | Out-Null

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              Setup Complete! 🎉                     ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Open TWO PowerShell windows:" -ForegroundColor White
Write-Host ""
Write-Host "  Window 1 (Backend):" -ForegroundColor Cyan
Write-Host "    .\venv\Scripts\Activate.ps1"
Write-Host "    `$env:PYTHONPATH = '$(Join-Path $ProjectRoot 'backend')'"
Write-Host "    cd backend"
Write-Host "    uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
Write-Host ""
Write-Host "  Window 2 (Frontend):" -ForegroundColor Cyan
Write-Host "    .\venv\Scripts\Activate.ps1"
Write-Host "    `$env:BACKEND_URL = 'http://localhost:8000'"
Write-Host "    streamlit run frontend\app.py --server.port 8501"
Write-Host ""
Write-Host "  Then open: http://localhost:8501" -ForegroundColor Cyan
