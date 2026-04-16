#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Sales Analysis — Análise de Cadência de Prospecção B2B     ║"
echo "║  1 Skill · 5 Agentes · 6 Sub-skills                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

SKILL_DIR="$HOME/.claude/skills/sales-analysis"
AGENTS_DIR="$HOME/.claude/agents"

echo "Instalando skill principal..."
mkdir -p "$SKILL_DIR/skills"
cp "$SCRIPT_DIR/SKILL.md" "$SKILL_DIR/SKILL.md" && echo "  ✓ SKILL.md (entry point)"
cp "$SCRIPT_DIR/CLAUDE.md" "$SKILL_DIR/CLAUDE.md" && echo "  ✓ CLAUDE.md (regras globais)"
cp "$SCRIPT_DIR/orchestrator.md" "$SKILL_DIR/orchestrator.md" && echo "  ✓ orchestrator.md (orquestrador)"

echo ""
echo "Instalando sub-skills..."
for skill in copywriter data-scorer pattern-detector timing-strategist lead-profiler hypothesis-generator; do
    if [ -f "$SCRIPT_DIR/skills/$skill.md" ]; then
        cp "$SCRIPT_DIR/skills/$skill.md" "$SKILL_DIR/skills/$skill.md" && echo "  ✓ $skill"
    else
        echo "  ✗ $skill (arquivo não encontrado)"
    fi
done

echo ""
echo "Instalando agentes..."
mkdir -p "$AGENTS_DIR"

declare -A AGENT_MAP
AGENT_MAP=(
    ["01-template-analyst.md"]="cadence-template.md"
    ["02-timing-analyst.md"]="cadence-timing.md"
    ["03-copy-analyst.md"]="cadence-copy.md"
    ["04-lead-analyst.md"]="cadence-lead.md"
    ["05-correlation-hunter.md"]="cadence-correlation.md"
)

for src in "${!AGENT_MAP[@]}"; do
    dst="${AGENT_MAP[$src]}"
    if [ -f "$SCRIPT_DIR/agents/$src" ]; then
        cp "$SCRIPT_DIR/agents/$src" "$AGENTS_DIR/$dst" && echo "  ✓ $dst"
    else
        echo "  ✗ $dst (arquivo fonte '$src' não encontrado)"
    fi
done

echo ""
echo "Criando diretórios de trabalho..."
mkdir -p "$SCRIPT_DIR/input/whatsapp-conversations" && echo "  ✓ input/whatsapp-conversations/"
mkdir -p "$SCRIPT_DIR/output/reports" && echo "  ✓ output/reports/"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Instalação concluída!                                      ║"
echo "║                                                              ║"
echo "║  Como usar:                                                  ║"
echo "║  1. Copie os JSONs do GS Engage para:                       ║"
echo "║     input/whatsapp-conversations/                            ║"
echo "║  2. No Claude Code, digite:                                  ║"
echo "║     /sales-analysis                                          ║"
echo "║  3. Os relatórios serão salvos em:                           ║"
echo "║     output/reports/                                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
