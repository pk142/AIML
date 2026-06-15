#!/usr/bin/env bash
# ============================================================
#  dev_setup.sh — Virtual Environment Setup (No Ollama/Docker)
#  RAM needed : ~500 MB
#  Disk needed: ~2 GB  (torch + sentence-transformers)
# ============================================================
set -e

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
RED="\033[0;31m"
RESET="\033[0m"

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_ROOT/venv"

echo -e "${BOLD}${CYAN}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║    Secure Doc RAG — Dev Environment Setup           ║"
echo "║    Mode: LOCAL  (no Ollama · no Docker · no GPU)    ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${RESET}"

# ── Python check ──────────────────────────────────────────────────────────
PY=""
for cmd in python3.11 python3.10 python3.9 python3 python; do
    if command -v "$cmd" &>/dev/null; then
        VER=$("$cmd" -c "import sys; print(sys.version_info[:2])")
        if [[ "$VER" > "(3, 8)" ]]; then
            PY="$cmd"
            break
        fi
    fi
done

if [ -z "$PY" ]; then
    echo -e "${RED}❌ Python 3.9+ not found. Install Python first.${RESET}"
    exit 1
fi
echo -e "${GREEN}✅ Using Python: $($PY --version)${RESET}"

# ── Create venv ───────────────────────────────────────────────────────────
if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}⚠️  venv already exists — skipping creation.${RESET}"
    echo "   Delete '$VENV_DIR' and re-run to recreate."
else
    echo -e "\n${BOLD}Creating virtual environment at ./venv …${RESET}"
    "$PY" -m venv "$VENV_DIR"
    echo -e "${GREEN}✅ Virtual environment created${RESET}"
fi

# ── Activate & install ────────────────────────────────────────────────────
echo -e "\n${BOLD}Installing packages (this may take 3–5 minutes first time)…${RESET}"
echo -e "${YELLOW}   torch CPU-only download: ~500 MB${RESET}"
echo -e "${YELLOW}   sentence-transformers model download on first run: ~80 MB${RESET}\n"

source "$VENV_DIR/bin/activate"

# Upgrade pip silently
pip install --upgrade pip --quiet

# Install CPU-only torch first to avoid downloading CUDA variant
pip install torch==2.3.1 --index-url https://download.pytorch.org/whl/cpu --quiet

# Install everything else
pip install -r "$PROJECT_ROOT/requirements-dev.txt" --quiet

echo -e "\n${GREEN}✅ All packages installed${RESET}"

# ── Create uploads dir ────────────────────────────────────────────────────
mkdir -p "$PROJECT_ROOT/uploads"

# ── Write run scripts ─────────────────────────────────────────────────────
cat > "$PROJECT_ROOT/run_backend.sh" << 'RUNEOF'
#!/usr/bin/env bash
cd "$(dirname "$0")"
source venv/bin/activate
export PYTHONPATH="$(pwd)/backend"
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
RUNEOF

cat > "$PROJECT_ROOT/run_frontend.sh" << 'RUNEOF'
#!/usr/bin/env bash
cd "$(dirname "$0")"
source venv/bin/activate
export BACKEND_URL=http://localhost:8000
streamlit run frontend/app.py --server.port 8501
RUNEOF

chmod +x "$PROJECT_ROOT/run_backend.sh" "$PROJECT_ROOT/run_frontend.sh"

# ── Summary ───────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════════════════╗"
echo -e "║              Setup Complete! 🎉                     ║"
echo -e "╚══════════════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "${BOLD}Next steps — open TWO terminal tabs:${RESET}"
echo ""
echo -e "  ${CYAN}Terminal 1 (Backend):${RESET}"
echo -e "    ./run_backend.sh"
echo ""
echo -e "  ${CYAN}Terminal 2 (Frontend):${RESET}"
echo -e "    ./run_frontend.sh"
echo ""
echo -e "  ${CYAN}Then open:${RESET}  http://localhost:8501"
echo ""
echo -e "${YELLOW}ℹ️  First Q&A: ~5 seconds to load the embedding model into RAM.${RESET}"
echo -e "${YELLOW}   After that each request takes 1–3 seconds.${RESET}"
echo ""
echo -e "${BOLD}To switch to real Phi-3 later:${RESET}"
echo "  1. Install Ollama + Docker"
echo "  2. Change DEV_MODE=false in .env"
echo "  3. Change EMBED_DIM=768 in .env"
echo "  4. Run: ./scripts/setup.sh"
