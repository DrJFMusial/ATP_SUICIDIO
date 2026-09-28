#!/usr/bin/env python3
"""medir.py - caixa de tinta por pagina, sobre build SEM marca d'agua.

Mede, pagina a pagina, onde a tinta do CONTEUDO comeca e termina dentro da
area util, e quanto sobra de faixa vazia acima do rodape.

Por que a area util e recortada antes de medir: a barra de rodape do tema
Madrid e desenhada DEPOIS do conteudo e ocupa toda a largura. Se a medicao
olhasse a pagina inteira, a barra seria lida como tinta e a faixa vazia acima
dela apareceria sempre como zero, escondendo exatamente o que se quer ver.
Pelo mesmo motivo este instrumento e sempre rodado junto com estouros.py: a
barra tambem cobre o transbordo, que so o log do TeX denuncia.

Geometria da serie, em 4:3 com margens de 0,45 cm:
    pagina      12,80 x 9,60 cm
    area util   11,90 x 8,27 cm
    titulo termina em 0,88 cm
    rodape comeca em 9,20 cm

Uso:
    python3 ferramentas/medir.py [main.pdf] [--dpi 150] [--json saida.json]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

PAG_L_CM, PAG_A_CM = 12.80, 9.60
MARGEM_CM = 0.45
TITULO_FIM_CM = 0.88
RODAPE_INI_CM = 9.20
LIMIAR = 246          # abaixo disso conta como tinta
MEDIANA_ALVO_CM = 0.12
TETO_PAGINA_CM = 1.00


def build_medicao(raiz: pathlib.Path | None = None) -> pathlib.Path:
    """Compila main.tex SEM a marca d'agua e devolve o PDF de medicao.

    A aquarela do fundo e lida como tinta pelo medidor, e a barra de rodape,
    desenhada depois do conteudo, esconde o transbordo. Por isso a medicao roda
    sempre sobre este build, e nunca sobre o PDF de entrega.
    """
    raiz = raiz or pathlib.Path(__file__).resolve().parent.parent
    saida = raiz / "build"
    saida.mkdir(exist_ok=True)
    for _ in range(2):
        subprocess.run(
            ["lualatex", "-interaction=nonstopmode", "-output-directory=build",
             "-jobname=medicao", r"\def\CRsemfundo{}\input{main.tex}"],
            cwd=raiz, capture_output=True)
    return saida / "medicao.pdf"


def paginas(pdf: pathlib.Path, dpi: int, destino: pathlib.Path) -> list[pathlib.Path]:
    subprocess.run(
        ["pdftoppm", "-png", "-r", str(dpi), str(pdf), str(destino / "p")],
        check=True, capture_output=True)
    return sorted(destino.glob("p-*.png"))


def mede(caminho: pathlib.Path, dpi: int) -> dict:
    img = np.asarray(Image.open(caminho).convert("L"))
    alt, larg = img.shape
    px_cm = alt / PAG_A_CM

    y0 = int(round(TITULO_FIM_CM * px_cm))
    y1 = int(round(RODAPE_INI_CM * px_cm))
    x0 = int(round(MARGEM_CM * (larg / PAG_L_CM)))
    x1 = int(round((PAG_L_CM - MARGEM_CM) * (larg / PAG_L_CM)))

    util = img[y0:y1, x0:x1]
    tinta = util < LIMIAR

    if not tinta.any():
        return {"vazia": True, "faixa_cm": round((y1 - y0) / px_cm, 2),
                "topo_cm": 0.0, "base_cm": 0.0, "ocupacao": 0.0,
                "invade_rodape": False, "invade_titulo": False}

    linhas = np.where(tinta.any(axis=1))[0]
    colunas = np.where(tinta.any(axis=0))[0]
    topo, base = int(linhas[0]), int(linhas[-1])

    # Invasao: tinta na primeira ou na ultima linha do recorte significa que o
    # conteudo encosta na faixa do titulo ou na do rodape.
    invade_titulo = topo <= 1
    invade_rodape = base >= (y1 - y0 - 2)

    faixa = (y1 - y0 - 1 - base) / px_cm

    return {
        "vazia": False,
        "topo_cm": round(topo / px_cm, 2),
        "base_cm": round((base + 1) / px_cm, 2),
        "faixa_cm": round(faixa, 2),
        "largura_usada_cm": round((colunas[-1] - colunas[0] + 1) / px_cm, 2),
        "ocupacao": round(float(tinta.mean()), 4),
        "invade_rodape": bool(invade_rodape),
        "invade_titulo": bool(invade_titulo),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", nargs="?", default="",
                    help="por omissao, compila e mede o build sem marca d'agua")
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    pdf = pathlib.Path(args.pdf) if args.pdf else build_medicao()
    if not pdf.exists():
        print(f"nao encontrei {pdf}", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory() as tmp:
        arquivos = paginas(pdf, args.dpi, pathlib.Path(tmp))
        dados = [dict(pagina=i + 1, **mede(f, args.dpi))
                 for i, f in enumerate(arquivos)]

    faixas = [d["faixa_cm"] for d in dados if not d["vazia"]]
    mediana = float(np.median(faixas)) if faixas else 0.0

    print(f"{'pag':>4}  {'topo':>6}  {'base':>6}  {'faixa':>6}  {'larg':>6}  {'tinta':>6}  nota")
    print("-" * 62)
    for d in dados:
        nota = []
        if d["vazia"]:
            nota.append("PAGINA SEM TINTA")
        if d.get("invade_rodape"):
            nota.append("ENCOSTA NO RODAPE")
        if d.get("invade_titulo"):
            nota.append("ENCOSTA NO TITULO")
        if d["faixa_cm"] > TETO_PAGINA_CM:
            nota.append(f"faixa vazia {d['faixa_cm']:.2f} cm")
        print(f"{d['pagina']:>4}  {d.get('topo_cm',0):>6.2f}  {d.get('base_cm',0):>6.2f}  "
              f"{d['faixa_cm']:>6.2f}  {d.get('largura_usada_cm',0):>6.2f}  "
              f"{d.get('ocupacao',0):>6.3f}  {'; '.join(nota)}")

    acima = [d["pagina"] for d in dados if d["faixa_cm"] > TETO_PAGINA_CM]
    encosta = [d["pagina"] for d in dados if d.get("invade_rodape")]
    print("-" * 62)
    print(f"mediana da faixa vazia: {mediana:.2f} cm  (alvo em torno de {MEDIANA_ALVO_CM:.2f})")
    print(f"paginas acima de {TETO_PAGINA_CM:.2f} cm de faixa: "
          f"{acima if acima else 'nenhuma'}")
    print(f"paginas encostando no rodape: {encosta if encosta else 'nenhuma'}")

    if args.json:
        pathlib.Path(args.json).write_text(
            json.dumps({"paginas": dados, "mediana_faixa_cm": mediana},
                       ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"json em {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
