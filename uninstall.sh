#!/bin/bash

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Sales Analysis — Desinstalação                             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

SKILL_DIR="$HOME/.claude/skills/sales-analysis"
AGENTS_DIR="$HOME/.claude/agents"

echo "Removendo skill principal..."
if [ -d "$SKILL_DIR" ]; then
    rm -rf "$SKILL_DIR" && echo "  ✓ sales-analysis/ removido"
else
    echo "  - sales-analysis/ não encontrado (já removido)"
fi

echo ""
echo "Removendo agentes..."
for agent in cadence-template cadence-timing cadence-copy cadence-lead cadence-correlation; do
    if [ -f "$AGENTS_DIR/$agent.md" ]; then
        rm "$AGENTS_DIR/$agent.md" && echo "  ✓ $agent.md removido"
    else
        echo "  - $agent.md não encontrado (já removido)"
    fi
done

echo ""
echo "Desinstalação concluída."
echo "Os diretórios input/ e output/ no projeto NÃO foram removidos."
echo ""
