#!/usr/bin/env python3
"""arte43.py - converte a arte 16:9 nas duas telas 4:3 do projeto.

Recortar o 16:9 para 4:3 perderia os motivos das laterais, e esticar deformaria
as figuras. Em vez disso, este script separa a faixa de cima e a faixa de baixo
da arte, encosta cada uma na borda correspondente da tela 4:3 e preenche o miolo
com o proprio tom de papel da imagem, esfumando a costura. Os quatro motivos
continuam nos quatro cantos, que e o que a composicao usa.

Uso:
    python3 ferramentas/arte43.py ARTE_FORTE.png ARTE_SUAVE.png
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
from PIL import Image

LARG, ALT = 2560, 1920
CORTE_SUP, CORTE_INF = 0.56, 0.44
PENA = 90
VEU_FUNDO = 0.55          # marca d'agua precisa ficar abaixo do limiar de leitura

DEST = pathlib.Path(__file__).resolve().parent.parent / "ilustracoes"


def papel(im: Image.Image) -> tuple[int, int, int]:
    a = np.asarray(im.convert("RGB"))
    h, w, _ = a.shape
    reg = a[int(h * .45):int(h * .55), int(w * .40):int(w * .60)]
    return tuple(int(v) for v in reg.reshape(-1, 3).mean(axis=0))


def mascara(altura: int, borda_baixo: bool) -> Image.Image:
    g = np.full((altura, LARG), 255, np.uint8)
    rampa = np.linspace(255, 0, PENA).astype(np.uint8)
    if borda_baixo:
        g[-PENA:, :] = rampa[:, None]
    else:
        g[:PENA, :] = rampa[::-1][:, None]
    return Image.fromarray(g)


def para43(origem: pathlib.Path, destino: pathlib.Path, veu: float = 0.0) -> None:
    im = Image.open(origem).convert("RGB")
    cor = papel(im)
    tela = Image.new("RGB", (LARG, ALT), cor)
    esc = im.resize((LARG, round(LARG * im.height / im.width)), Image.LANCZOS)
    h = esc.height
    topo = esc.crop((0, 0, LARG, int(h * CORTE_SUP)))
    base = esc.crop((0, h - int(h * CORTE_INF), LARG, h))
    tela.paste(topo, (0, 0), mascara(topo.height, True))
    tela.paste(base, (0, ALT - base.height), mascara(base.height, False))
    if veu:
        tela = Image.blend(tela, Image.new("RGB", (LARG, ALT), cor), veu)
    # JPEG de 1920 x 1440: a 128 mm de largura isso da cerca de 380 dpi, mais do
    # que qualquer projetor usa, e derruba o PDF de 5,6 MB para menos de 1 MB.
    tela = tela.resize((1920, 1440), Image.LANCZOS)
    tela.save(destino, "JPEG", quality=88, optimize=True, progressive=True,
              subsampling=0)
    print(f"{destino}  {tela.size}  papel {cor}  veu {veu}")


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 1
    para43(pathlib.Path(sys.argv[1]), DEST / "CAPA.jpg", 0.0)
    para43(pathlib.Path(sys.argv[2]), DEST / "BACKGROUND.jpg", VEU_FUNDO)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
