#!/usr/bin/env python3
"""md2tex.py - converte os documentos de fonte/ em corpo LaTeX para os A4 docentes.

Mantem fonte/*.md como unica fonte de verdade: o gabarito e o handout sao escritos
uma vez, em texto, e daqui saem tanto o HTML quanto o PDF A4.

Reconhece: titulos de 1 a 3 niveis, paragrafos, listas com hifen, citacoes em
bloco, regua horizontal e negrito. Escapa os especiais do TeX.

Uso:
    python3 ferramentas/md2tex.py fonte/gabarito.md docente/corpo-gabarito.tex
"""
from __future__ import annotations

import pathlib
import re
import sys

ESCAPES = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
    "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
    "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
}


def escapa(txt: str) -> str:
    saida = []
    for ch in txt:
        saida.append(ESCAPES.get(ch, ch))
    return "".join(saida)


def inline(txt: str) -> str:
    partes = re.split(r"(\*\*[^*]+\*\*)", txt)
    fora = []
    for p in partes:
        if p.startswith("**") and p.endswith("**"):
            fora.append(r"\textbf{" + escapa(p[2:-2]) + "}")
        else:
            fora.append(escapa(p))
    s = "".join(fora)
    # aspas tipograficas das falas literais
    s = s.replace('"', "''")
    return s


def converte(md: str, pular_titulo: bool = False) -> str:
    linhas = md.split("\n")
    saida: list[str] = []
    buffer: list[str] = []
    modo: str | None = None

    def libera():
        nonlocal buffer, modo
        if not buffer:
            modo = None
            return
        if modo == "lista":
            saida.append(r"\begin{itemize}[leftmargin=1.1em, itemsep=0.18em, topsep=0.30em]")
            for item in buffer:
                saida.append(r"  \item " + inline(item))
            saida.append(r"\end{itemize}")
        elif modo == "quote":
            saida.append(r"\begin{fala}")
            for f in buffer:
                if f:
                    saida.append(inline(f) + r"\par")
            saida.append(r"\end{fala}")
        else:
            saida.append(inline(" ".join(buffer)))
        saida.append("")
        buffer, modo = [], None

    for bruta in linhas:
        linha = bruta.rstrip()
        if not linha.strip():
            libera()
            continue
        if linha.startswith("### "):
            libera()
            saida.append(r"\subsubsection*{" + inline(linha[4:]) + "}")
            saida.append("")
        elif linha.startswith("## "):
            libera()
            saida.append(r"\subsection*{" + inline(linha[3:]) + "}")
            saida.append("")
        elif linha.startswith("# "):
            libera()
            if not pular_titulo:
                saida.append(r"\section*{" + inline(linha[2:]) + "}")
                saida.append("")
        elif linha.strip() == "---":
            libera()
            saida.append(r"\CRregua@filete")
            saida.append("")
        elif linha.startswith("- "):
            if modo != "lista":
                libera()
                modo = "lista"
            buffer.append(linha[2:].strip())
        elif linha.startswith("> "):
            if modo != "quote":
                libera()
                modo = "quote"
            buffer.append(linha[2:].strip())
        elif linha.startswith(">"):
            if modo == "quote":
                buffer.append("")
        else:
            if modo == "lista":
                buffer[-1] += " " + linha.strip()
            elif modo == "quote":
                buffer[-1] += " " + linha.strip()
            else:
                if modo != "para":
                    libera()
                    modo = "para"
                buffer.append(linha.strip())
    libera()
    texto = "\n".join(saida)
    texto = texto.replace(r"\CRregua@filete", r"\filete")
    return texto


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pular = "--sem-titulo" in sys.argv
    if len(args) != 2:
        print(__doc__)
        return 1
    entrada, saida = pathlib.Path(args[0]), pathlib.Path(args[1])
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(converte(entrada.read_text(encoding="utf-8"), pular),
                     encoding="utf-8")
    print(f"{entrada} -> {saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
