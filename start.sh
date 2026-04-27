#!/bin/bash
# AI LeadGen Agent - 快速啟動腳本 (Linux/macOS)

echo "============================================"
echo "  AI LeadGen Agent - Quick Start Script"
echo "============================================"
echo ""

cd "$(dirname "$0")"

echo "[1/4] Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker not found. Please install Docker Desktop."
    exit 1
fi
echo "    ✓ Docker ready"

echo ""
echo "[2/4] Checking .env configuration..."
if [ ! -f ".env" ]; then
    echo "    Creating .env file..."
    cp .env.example .env
    echo ""
    echo "    ⚠️  Please edit .env and add your API Keys:"
    echo "       - OPENAI_API_KEY"
    echo "       - SENDGRID_API_KEY"
    echo ""
    nano .env
fi

echo ""
echo "[3/4] Starting Docker services..."
docker-compose up -d

echo ""
echo "[4/4] Waiting for services to start..."
sleep 10

echo ""
echo "============================================"
echo "  Services Started!"
echo "============================================"
echo ""
echo "  Frontend:     http://localhost:5173"
echo "  API Docs:     http://localhost:8000/docs"
echo "  Task Monitor:  http://localhost:5555"
echo ""
echo "  View logs:    docker-compose logs -f"
echo "  Stop:         docker-compose down"
echo "============================================"
echo ""
echo "Opening browser..."
sleep 2
open http://localhost:5173 || xdg-open http://localhost:5173
