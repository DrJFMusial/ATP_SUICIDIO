#!/usr/bin/env python3
"""simbolos.py - confere cada simbolo usado na aula contra duas fontes.

Um simbolo so entra no deck se passar nos dois testes:

  1. estar documentado na Comprehensive LaTeX Symbol List, o anexo de
     referencia, que diz qual pacote fornece cada simbolo;
  2. existir de fato nesta instalacao de TeX, o que e verificado compilando um
     \\ifcsname para cada nome.

O primeiro teste sozinho nao basta: a lista documenta a familia inteira do
fontawesome5, e versoes diferentes do pacote definem conjuntos diferentes de
macros. O segundo sozinho tambem nao basta, porque uma macro pode existir aqui
e nao na maquina em que o deck for recompilado.

Uso:
    python3 ferramentas/simbolos.py --anexo /caminho/symbols-a4.pdf
    python3 ferramentas/simbolos.py            # so o teste de instalacao
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent


def usados() -> list[str]:
    """Todo \\faXxx que aparece no tema e no conteudo."""
    alvos = list((RAIZ / "conteudo").glob("*.tex"))
    alvos += list((RAIZ / "tema").glob("*.tex"))
    alvos += [RAIZ / "preamble.tex"]
    nomes: set[str] = set()
    for p in alvos:
        if p.exists():
            nomes |= set(re.findall(r"\\(fa[A-Z][A-Za-z0-9]*)", p.read_text(encoding="utf-8")))
    return sorted(nomes)


def no_anexo(pdf: pathlib.Path) -> set[str]:
    texto = subprocess.run(["pdftotext", str(pdf), "-"],
                           capture_output=True, text=True, errors="replace").stdout
    return set(re.findall(r"\b(fa[A-Z][A-Za-z0-9]{2,})\b", texto))


def na_instalacao(nomes: list[str]) -> set[str]:
    with tempfile.TemporaryDirectory() as tmp:
        d = pathlib.Path(tmp)
        corpo = "".join(r"\v{%s}" % n for n in nomes)
        (d / "t.tex").write_text(
            "\\documentclass{article}\\usepackage{fontspec}\\usepackage{fontawesome5}\n"
            "\\newwrite\\r \\immediate\\openout\\r=faltam.txt\n"
            "\\newcommand{\\v}[1]{\\ifcsname #1\\endcsname\\else"
            "\\immediate\\write\\r{#1}\\fi}\n"
            "\\begin{document}" + corpo + "ok\\immediate\\closeout\\r\\end{document}\n",
            encoding="utf-8")
        subprocess.run(["lualatex", "-interaction=nonstopmode", "t.tex"],
                       cwd=d, capture_output=True)
        faltam = (d / "faltam.txt")
        ausentes = set(faltam.read_text(encoding="utf-8").split()) if faltam.exists() else set()
    return set(nomes) - ausentes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--anexo", default="")
    args = ap.parse_args()

    nomes = usados()
    print(f"{len(nomes)} simbolos usados no projeto\n")

    instalados = na_instalacao(nomes)
    documentados = no_anexo(pathlib.Path(args.anexo)) if args.anexo else None

    print(f"{'simbolo':<26} {'instalacao':<12} {'anexo'}")
    print("-" * 52)
    falhas = []
    for n in nomes:
        i = "ok" if n in instalados else "AUSENTE"
        if documentados is None:
            d = "nao conferido"
        else:
            d = "ok" if n in documentados else "NAO CONSTA"
        if i != "ok" or d == "NAO CONSTA":
            falhas.append(n)
        print(f"{n:<26} {i:<12} {d}")

    print("-" * 52)
    if falhas:
        print(f"REPROVADOS: {', '.join(falhas)}")
        print("Trocar cada um por simbolo que passe nos dois testes.")
        return 2
    print("todos os simbolos passaram nos testes disponiveis")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
