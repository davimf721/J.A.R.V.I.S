#!/bin/bash

# INÍCIO RÁPIDO - Comece por aqui!

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     JARVIS - Sistema de Podcast Inteligente para macOS        ║"
echo "║     Bem-vindo! Vamos começar...                               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Verificação de prerequisites
echo "🔍 Verificando prerequisites..."
echo ""

# 1. macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Este script é apenas para macOS"
    exit 1
fi
echo "✓ macOS detectado"

# 2. Set executável permission
echo ""
echo "⚙️  Configurando permissões..."
chmod +x setup-mac.sh 2>/dev/null
chmod +x manage.sh 2>/dev/null
chmod +x run-podcast.sh 2>/dev/null
chmod +x quick-podcast.sh 2>/dev/null
echo "✓ Scripts preparados"

# 3. Show next steps
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📚 PRÓXIMOS PASSOS:"
echo ""
echo "  1️⃣  INSTALAR TUDO:"
echo "     ./setup-mac.sh"
echo ""
echo "     (Isso vai:"
echo "     - Instalar Homebrew (se necessário)"
echo "     - Instalar Docker Desktop (se necessário)"
echo "     - Construir e iniciar os contêineres"
echo "     - Esperar todos os serviços ficarem prontos)"
echo ""
echo "  2️⃣  GERAR UM PODCAST:"
echo "     ./quick-podcast.sh"
echo ""
echo "     Ou para mais opções:"
echo "     ./run-podcast.sh"
echo ""
echo "  3️⃣  GERENCIAR SERVIÇOS:"
echo "     ./manage.sh status     # Ver status"
echo "     ./manage.sh logs       # Ver logs"
echo "     ./manage.sh stop       # Parar tudo"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📖 DOCUMENTAÇÃO:"
echo ""
echo "  - GETTING_STARTED.md  → Guia completo"
echo "  - API_GUIDE.md        → Documentação da API"
echo "  - README.md           → Visão geral do projeto"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "🚀 VAMOS LÁ!"
echo ""
echo "Execute: ./setup-mac.sh"
echo ""
