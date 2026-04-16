#!/usr/bin/env python3
"""
md2pdf.py — Converte relatórios Markdown em PDF.

Uso:
    python scripts/md2pdf.py output/reports/              # converte todos os .md da pasta
    python scripts/md2pdf.py relatorio.md                 # converte um arquivo específico
    python scripts/md2pdf.py relatorio.md -o saida.pdf    # nome customizado de saída

Dependências:
    pip install markdown weasyprint

Se weasyprint não estiver disponível, tenta usar mdpdf como fallback:
    pip install mdpdf
"""

import argparse
import sys
from pathlib import Path

CSS_STYLE = """
@page {
    size: A4;
    margin: 2cm;
}
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #1a1a1a;
    max-width: 100%;
}
h1 {
    font-size: 20pt;
    border-bottom: 2px solid #2563eb;
    padding-bottom: 8px;
    margin-top: 24px;
    color: #1e293b;
}
h2 {
    font-size: 15pt;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 6px;
    margin-top: 20px;
    color: #334155;
}
h3 {
    font-size: 12pt;
    margin-top: 16px;
    color: #475569;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin: 12px 0;
    font-size: 9.5pt;
}
th, td {
    border: 1px solid #cbd5e1;
    padding: 6px 10px;
    text-align: left;
}
th {
    background-color: #f1f5f9;
    font-weight: 600;
    color: #334155;
}
tr:nth-child(even) {
    background-color: #f8fafc;
}
code {
    background-color: #f1f5f9;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 9.5pt;
}
pre {
    background-color: #f1f5f9;
    padding: 12px;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 9pt;
    line-height: 1.4;
}
blockquote {
    border-left: 4px solid #2563eb;
    margin: 12px 0;
    padding: 8px 16px;
    background-color: #eff6ff;
    color: #1e40af;
}
hr {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 20px 0;
}
strong {
    color: #0f172a;
}
"""


def convert_with_weasyprint(md_path: Path, pdf_path: Path) -> bool:
    """Converte MD → PDF usando markdown + weasyprint."""
    try:
        import markdown
        from weasyprint import HTML
    except ImportError:
        return False

    md_text = md_path.read_text(encoding="utf-8")
    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "codehilite", "toc"],
    )
    full_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="utf-8"><style>{CSS_STYLE}</style></head>
<body>{html_body}</body>
</html>"""

    HTML(string=full_html).write_pdf(str(pdf_path))
    return True


def convert_with_mdpdf(md_path: Path, pdf_path: Path) -> bool:
    """Fallback: converte MD → PDF usando mdpdf via subprocess."""
    import subprocess

    try:
        result = subprocess.run(
            ["mdpdf", "-o", str(pdf_path), str(md_path)],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except FileNotFoundError:
        # tenta com caminho expandido (macOS pip install local)
        from pathlib import Path as P
        local_bin = P.home() / "Library/Python/3.9/bin/mdpdf"
        if local_bin.exists():
            result = subprocess.run(
                [str(local_bin), "-o", str(pdf_path), str(md_path)],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        return False


def convert_file(md_path: Path, pdf_path: Path | None = None) -> Path | None:
    """Converte um arquivo .md em .pdf. Retorna o path do PDF ou None se falhar."""
    if pdf_path is None:
        pdf_path = md_path.with_suffix(".pdf")

    if convert_with_weasyprint(md_path, pdf_path):
        return pdf_path

    if convert_with_mdpdf(md_path, pdf_path):
        return pdf_path

    return None


def main():
    parser = argparse.ArgumentParser(
        description="Converte relatórios Markdown em PDF"
    )
    parser.add_argument(
        "input",
        help="Arquivo .md ou diretório contendo .md files",
    )
    parser.add_argument(
        "-o", "--output",
        help="Caminho do PDF de saída (só para arquivo único)",
        default=None,
    )
    args = parser.parse_args()

    input_path = Path(args.input)

    if input_path.is_dir():
        md_files = sorted(input_path.glob("*.md"))
        if not md_files:
            print(f"Nenhum arquivo .md encontrado em {input_path}")
            sys.exit(1)

        print(f"Convertendo {len(md_files)} arquivo(s) em {input_path}/\n")
        ok, fail = 0, 0
        for md in md_files:
            result = convert_file(md)
            if result:
                print(f"  ✓ {md.name} → {result.name}")
                ok += 1
            else:
                print(f"  ✗ {md.name} — falhou")
                fail += 1

        print(f"\n{ok} convertido(s), {fail} falha(s)")
        if fail > 0:
            print("Instale as dependências: pip install markdown weasyprint")
            sys.exit(1)

    elif input_path.is_file() and input_path.suffix == ".md":
        output_path = Path(args.output) if args.output else None
        result = convert_file(input_path, output_path)
        if result:
            print(f"✓ {input_path.name} → {result.name}")
        else:
            print(f"✗ Falha ao converter {input_path.name}")
            print("Instale as dependências: pip install markdown weasyprint")
            sys.exit(1)

    else:
        print(f"Erro: {input_path} não é um arquivo .md nem um diretório")
        sys.exit(1)


if __name__ == "__main__":
    main()
