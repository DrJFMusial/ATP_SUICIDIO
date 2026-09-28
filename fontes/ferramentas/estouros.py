#!/usr/bin/env python3
"""estouros.py - transbordo por frame, lido no log do TeX.

O medidor de tinta nao enxerga transbordo: a barra de rodape do tema e
desenhada depois do conteudo e cobre o que passou do limite. Quem denuncia o
transbordo e o log. Por isso os dois instrumentos rodam JUNTOS, sempre.

Este script le main.log, separa Overfull \\vbox e Overfull \\hbox, e amarra
cada ocorrencia ao arquivo de conteudo e ao frame em que ela aconteceu,
seguindo a pilha de arquivos abertos que o TeX escreve no proprio log.

Uso:
    python3 ferramentas/estouros.py [main.log] [--conteudo conteudo]
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

RE_OVER = re.compile(
    r"Overfull \\(?P<tipo>vbox|hbox) \((?P<pt>[0-9.]+)pt too (?:high|wide)\)"
    r"(?: in paragraph at lines (?P<l1>\d+)--(?P<l2>\d+)| detected at line (?P<l3>\d+))?")
RE_ABRE = re.compile(r"\((\.?/?[-\w./]+\.tex)")
RE_PAG = re.compile(r"\[(\d+)")


def paginas_do_log(log: str) -> list[tuple[int, int]]:
    """Posicao no log -> numero da pagina que acabou de ser escrita."""
    saida = []
    for m in RE_PAG.finditer(log):
        n = int(m.group(1))
        if not saida or n == saida[-1][1] + 1:
            saida.append((m.start(), n))
    return saida


def pagina_em(marcas: list[tuple[int, int]], pos: int) -> int:
    """A pagina em composicao e a seguinte a ultima ja escrita."""
    atual = 0
    for p, n in marcas:
        if p > pos:
            break
        atual = n
    return atual + 1


def pilha_de_arquivos(log: str) -> list[tuple[int, str]]:
    """Devolve, para cada posicao do log, qual arquivo .tex estava aberto."""
    eventos: list[tuple[int, str]] = []
    pilha: list[str] = []
    i = 0
    while i < len(log):
        c = log[i]
        if c == "(":
            m = RE_ABRE.match(log, i)
            if m:
                pilha.append(m.group(1))
                eventos.append((i, pilha[-1]))
                i = m.end()
                continue
        elif c == ")":
            if pilha:
                pilha.pop()
                eventos.append((i, pilha[-1] if pilha else ""))
        i += 1
    return eventos


def arquivo_em(eventos: list[tuple[int, str]], pos: int) -> str:
    atual = ""
    for p, nome in eventos:
        if p > pos:
            break
        atual = nome
    return atual


def frames_do_arquivo(caminho: pathlib.Path) -> list[tuple[int, str]]:
    """Lista (linha do \\begin{frame}, titulo) de um arquivo de conteudo."""
    saida = []
    for n, linha in enumerate(caminho.read_text(encoding="utf-8").split("\n"), 1):
        m = re.match(r"\s*\\begin\{frame\}(?:\[[^\]]*\])?\{(.*?)\}\s*$", linha)
        if m:
            saida.append((n, m.group(1)))
        elif re.match(r"\s*\\begin\{frame\}", linha):
            saida.append((n, "(sem titulo)"))
    return saida


def frame_da_linha(frames: list[tuple[int, str]], linha: int) -> str:
    achado = "(antes do primeiro frame)"
    for n, titulo in frames:
        if n <= linha:
            achado = f"linha {n}: {titulo}"
        else:
            break
    return achado


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("log", nargs="?", default="build/medicao.log")
    ap.add_argument("--conteudo", default="conteudo")
    args = ap.parse_args()

    caminho_log = pathlib.Path(args.log)
    if not caminho_log.exists():
        print(f"nao encontrei {caminho_log}", file=sys.stderr)
        return 1

    texto = caminho_log.read_text(encoding="utf-8", errors="replace")
    eventos = pilha_de_arquivos(texto)
    marcas = paginas_do_log(texto)

    cache: dict[str, list[tuple[int, str]]] = {}
    achados = []
    for m in RE_OVER.finditer(texto):
        linha = int(m.group("l3") or m.group("l1") or 0)
        arq = arquivo_em(eventos, m.start())
        nome = pathlib.Path(arq).name if arq else "?"
        origem = "?"
        p = pathlib.Path(args.conteudo) / nome
        if p.exists():
            if nome not in cache:
                cache[nome] = frames_do_arquivo(p)
            origem = frame_da_linha(cache[nome], linha)
        achados.append({
            "tipo": m.group("tipo"),
            "pt": float(m.group("pt")),
            "arquivo": nome,
            "linha": linha,
            "frame": origem,
            "pagina": pagina_em(marcas, m.start()),
        })

    vbox = [a for a in achados if a["tipo"] == "vbox"]
    hbox = [a for a in achados if a["tipo"] == "hbox"]

    def imprime(titulo: str, lista: list[dict]) -> None:
        print(f"\n{titulo} ({len(lista)})")
        print("-" * 74)
        for a in sorted(lista, key=lambda x: -x["pt"]):
            print(f"  {a['pt']:>7.2f}pt  pag {a['pagina']:>3}  "
                  f"{a['arquivo']:<24} {a['frame']}")

    imprime("Overfull \\vbox  (altura: o frame nao cabe)", vbox)
    imprime("Overfull \\hbox  (largura: a linha ou o desenho passou da margem)", hbox)

    print("\n" + "=" * 74)
    graves = [a for a in hbox if a["pt"] >= 1.0]
    print(f"criterio de aceitacao: zero vbox e zero hbox acima de 1pt")
    print(f"estado: vbox = {len(vbox)}, hbox acima de 1pt = {len(graves)}")
    return 0 if not vbox and not graves else 2


if __name__ == "__main__":
    raise SystemExit(main())
