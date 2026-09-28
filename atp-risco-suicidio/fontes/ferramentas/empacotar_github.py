#!/usr/bin/env python3
"""empacotar_github.py - monta os dois pacotes de publicacao.

Produz, em build/publicacao/:

  atp-risco-suicidio/     repositorio PUBLICO, pronto para subir ao GitHub e
                          servir pelo GitHub Pages
  MATERIAL-DOCENTE/       gabarito, handout e as fontes deles, que NAO vao para
                          o repositorio publico

A separacao e a razao de ser deste script. Em repositorio publico todo arquivo
versionado fica acessivel pela arvore, mesmo sem link em pagina nenhuma. O
gabarito traz as formulacoes defensaveis e os erros previsiveis dos seis casos,
de modo que versiona-lo junto entrega a atividade antes de ela acontecer.

Uso:
    python3 ferramentas/empacotar_github.py
"""
from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DEST = RAIZ / "build" / "publicacao"
PUB = DEST / "atp-risco-suicidio"
PRIV = DEST / "MATERIAL-DOCENTE"

# Fontes LaTeX que podem ir ao repositorio publico: e a prelecao, que o aluno
# assiste. Fica de fora tudo o que e do docente.
FONTE_PUBLICA = [
    "main.tex", "preamble.tex", "LEIA-ME.md",
]
DIR_PUBLICOS = ["tema", "conteudo", "ilustracoes", "isolados", "ferramentas"]
FONTE_TEXTO_PUBLICA = [
    "caso-01.md", "caso-02.md", "caso-03.md", "caso-04.md", "caso-05.md",
    "caso-06.md", "folha-de-trabalho.md", "verificacao-fontes.md",
]
FONTE_TEXTO_DOCENTE = ["gabarito.md", "handout-docente.md"]

IGNORA = shutil.ignore_patterns("__pycache__", "*.pyc", "*.aux", "*.log",
                                "*.nav", "*.out", "*.snm", "*.toc", "*.pdf",
                                "*.b64")


def limpa() -> None:
    if DEST.exists():
        shutil.rmtree(DEST)
    (PUB / "pdf").mkdir(parents=True)
    (PUB / "caderno").mkdir(parents=True)
    (PUB / "fontes").mkdir(parents=True)
    (PRIV / "fonte").mkdir(parents=True)
    (PRIV / "docente").mkdir(parents=True)


def exige(p: pathlib.Path) -> pathlib.Path:
    if not p.exists():
        print(f"faltando: {p}", file=sys.stderr)
        raise SystemExit(1)
    return p


def monta_publico() -> None:
    # --- paginas ------------------------------------------------------------
    subprocess.run([sys.executable, "ferramentas/build_portal.py",
                    str(PUB / "index.html")], cwd=RAIZ, check=True)
    subprocess.run([sys.executable, "ferramentas/build_caderno.py", "--portal",
                    "--saida", str(PUB / "caderno" / "index.html")],
                   cwd=RAIZ, check=True)

    # --- PDFs publicos ------------------------------------------------------
    for origem, destino in (("main.pdf", "prelecao.pdf"),
                            ("algoritmo.pdf", "algoritmo.pdf"),
                            ("frases.pdf", "frases.pdf")):
        shutil.copy2(exige(RAIZ / origem), PUB / "pdf" / destino)

    # --- fontes LaTeX da prelecao ------------------------------------------
    for nome in FONTE_PUBLICA:
        shutil.copy2(exige(RAIZ / nome), PUB / "fontes" / nome)
    for d in DIR_PUBLICOS:
        shutil.copytree(exige(RAIZ / d), PUB / "fontes" / d, ignore=IGNORA)
    (PUB / "fontes" / "fonte").mkdir()
    for nome in FONTE_TEXTO_PUBLICA:
        shutil.copy2(exige(RAIZ / "fonte" / nome), PUB / "fontes" / "fonte" / nome)

    # --- arquivos de repositorio -------------------------------------------
    rep = RAIZ / "repo-arquivos"
    for origem, destino in (("README.md", "README.md"),
                            ("LICENSE", "LICENSE"),
                            ("LICENSE-ferramentas", "LICENSE-ferramentas"),
                            ("CITATION.cff", "CITATION.cff"),
                            ("gitignore", ".gitignore"),
                            ("nojekyll", ".nojekyll")):
        shutil.copy2(exige(rep / origem), PUB / destino)


def monta_privado() -> None:
    for nome in ("gabarito.pdf", "handout.pdf", "gabarito.tex", "handout.tex",
                 "preamble-a4.tex", "corpo-gabarito.tex", "corpo-handout.tex"):
        p = RAIZ / "docente" / nome
        if p.exists():
            shutil.copy2(p, PRIV / "docente" / nome)
    for nome in FONTE_TEXTO_DOCENTE:
        shutil.copy2(exige(RAIZ / "fonte" / nome), PRIV / "fonte" / nome)
    shutil.copy2(exige(RAIZ / "repo-arquivos" / "LEIA-ME-DOCENTE.md"),
                 PRIV / "LEIA-ME.md")


def confere() -> None:
    """Nenhum arquivo do docente pode ter escapado para o lado publico."""
    proibidos = ["gabarito", "handout"]
    achados = [str(p.relative_to(PUB)) for p in PUB.rglob("*")
               if p.is_file() and any(x in p.name.lower() for x in proibidos)]
    if achados:
        print("ABORTADO: material docente dentro do pacote publico:", file=sys.stderr)
        for a in achados:
            print(f"   {a}", file=sys.stderr)
        raise SystemExit(2)

    # E o conteudo dos arquivos publicos tambem nao pode citar o gabarito.
    # As marcas sao montadas por partes de proposito: assim este proprio
    # arquivo nao contem as cadeias inteiras e nao se denuncia sozinho numa
    # busca feita sobre o repositorio publico.
    marcas = ["formulação defens" + "ável",
              "Erro previs" + "ível",
              "Condutas " + "inadequadas",
              "Ausências " + "plantadas"]
    vazou = []
    for p in PUB.rglob("*"):
        if p.is_file() and p.suffix in {".html", ".md", ".tex"}:
            texto = p.read_text(encoding="utf-8", errors="replace")
            if any(m in texto for m in marcas):
                vazou.append(str(p.relative_to(PUB)))
    if vazou:
        print("ABORTADO: texto de gabarito dentro do pacote publico:", file=sys.stderr)
        for a in vazou:
            print(f"   {a}", file=sys.stderr)
        raise SystemExit(2)
    print("conferencia: nenhum material docente no pacote publico")


def tamanho(p: pathlib.Path) -> str:
    total = sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
    n = sum(1 for f in p.rglob("*") if f.is_file())
    return f"{n} arquivos, {total/1024/1024:.1f} MB"


def leia_me_raiz() -> None:
    """O aviso que explica as duas pastas fica na raiz do pacote."""
    origem = RAIZ / "repo-arquivos" / "LEIA-ME-PRIMEIRO.md"
    if origem.exists():
        shutil.copy2(origem, DEST / "LEIA-ME-PRIMEIRO.md")


def main() -> int:
    limpa()
    monta_publico()
    monta_privado()
    leia_me_raiz()
    confere()
    print(f"\npublico   {PUB}   {tamanho(PUB)}")
    print(f"docente   {PRIV}   {tamanho(PRIV)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
