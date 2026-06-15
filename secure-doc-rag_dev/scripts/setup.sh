#!/usr/bin/env bash
# ============================================================
# setup.sh — First-run setup for Secure Document Intelligence
# ============================================================
set -e

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
RESET="\033[0m"

echo -e "${BOLD}${CYAN}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║     Secure Document Intelligence — Setup Script     ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${RESET}"

# ── Prerequisites ──────────────────────────────────────────
echo -e "${BOLD}Checking prerequisites...${RESET}"

command -v docker >/dev/null 2>&1 || { echo "❌ Docker not found. Install Docker first."; exit 1; }
command -v docker compose >/dev/null 2>&1 || docker-compose --version >/dev/null 2>&1 || { echo "❌ Docker Compose not found."; exit 1; }

echo -e "${GREEN}✅ Docker found${RESET}"

# ── Start infrastructure ───────────────────────────────────
echo -e "\n${BOLD}Starting Qdrant and Ollama...${RESET}"
docker compose up -d qdrant ollama

echo -e "${YELLOW}Waiting for Ollama to be ready (up to 60s)...${RESET}"
for i in $(seq 1 30); do
    if curl -sf http://localhost:11434/ >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Ollama is ready${RESET}"
        break
    fi
    sleep 2
done

# ── Pull models ────────────────────────────────────────────
echo -e "\n${BOLD}Pulling Phi-3 (LLM)...${RESET}"
echo -e "${YELLOW}⏳ This may take several minutes depending on your connection.${RESET}"
docker exec rag_ollama ollama pull phi3

echo -e "\n${BOLD}Pulling nomic-embed-text (Embeddings)...${RESET}"
docker exec rag_ollama ollama pull nomic-embed-text

echo -e "${GREEN}✅ Models ready${RESET}"

# ── Start full stack ───────────────────────────────────────
echo -e "\n${BOLD}Starting backend and frontend...${RESET}"
docker compose up -d backend frontend

echo -e "\n${GREEN}${BOLD}✅ All services started!${RESET}"
echo ""
echo -e "  ${CYAN}Frontend:${RESET}  http://localhost:8501"
echo -e "  ${CYAN}Backend:${RESET}   http://localhost:8000"
echo -e "  ${CYAN}API Docs:${RESET}  http://localhost:8000/docs"
echo -e "  ${CYAN}Qdrant UI:${RESET} http://localhost:6333/dashboard"
echo ""
echo -e "${YELLOW}💡 First Q&A may be slow as the LLM warms up.${RESET}"
