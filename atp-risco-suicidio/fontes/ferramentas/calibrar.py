#!/usr/bin/env python3
"""calibrar.py - calcula o k de \\CRar de cada frame a partir de duas
compilacoes medidas, e itera.

Ideia: dentro de um frame, a altura ocupada cresce de forma quase linear com o
fator de ar k. Com duas compilacoes, uma com todos os frames em k = kA e outra
em k = kB, obtem-se para cada pagina a reta base(k) e, dela, o k que deixa a
faixa vazia acima do rodape no alvo.

A calibracao otimiza legibilidade, equilibrio, alinhamento e respiro. Nao
otimiza quantidade de tinta.

Paginas que nao respondem ao ar (figura isolada, divisor, diagrama de pagina
inteira, tabela sem texto corrido) aparecem no relatorio como NAO RESPONDE.
Essas nao se resolvem no k: resolvem-se na geometria do desenho, em minimum
height, node distance e corpo de letra. Nunca em caixa alta com uma linha
dentro, que e enchimento e nao composicao.

Uso:
    python3 ferramentas/calibrar.py               # calibra e escreve os k
    python3 ferramentas/calibrar.py --simular     # so relata, nao escreve
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import medir  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CONTEUDO = RAIZ / "conteudo"
PDF = RAIZ / "main.pdf"

ALVO_CM = 0.12          # faixa vazia desejada acima do rodape
AREA_UTIL_CM = medir.RODAPE_INI_CM - medir.TITULO_FIM_CM
K_MIN, K_MAX = 0.0, 6.0
K_A, K_B = 0.0, 3.0
RESPOSTA_MINIMA_CM = 0.06   # abaixo disso, a pagina nao responde ao ar

RE_CRAR = re.compile(r"^(\s*)\\CRar\{([-\d.]+)\}\s*$")
RE_FRAME = re.compile(r"^\s*\\begin\{frame\}")


def ordem_dos_arquivos() -> list[pathlib.Path]:
    """Ordem real dos arquivos de conteudo, seguindo \\input encadeado.

    07-sintese.tex nao tem frames: ele apenas chama 07a e 07b, que sao os dois
    frames compartilhados com os PDFs isolados. Sem expandir o encadeamento, a
    numeracao de frame sai deslocada e a calibracao escreve o k na pagina errada.
    """
    def expande(arq: pathlib.Path) -> list[pathlib.Path]:
        texto = arq.read_text(encoding="utf-8")
        filhos = re.findall(r"\\input\{conteudo/([-\w.]+\.tex)\}", texto)
        if not filhos:
            return [arq]
        fora = []
        for n in filhos:
            fora.extend(expande(CONTEUDO / n))
        return fora

    main = (RAIZ / "main.tex").read_text(encoding="utf-8")
    nomes = re.findall(r"\\input\{conteudo/([-\w.]+\.tex)\}", main)
    ordem = []
    for n in nomes:
        ordem.extend(expande(CONTEUDO / n))
    return ordem


def mapa_dos_frames() -> list[tuple[pathlib.Path, int]]:
    """Frame n (1-based) -> (arquivo, indice da linha do \\CRar)."""
    mapa = []
    for arq in ordem_dos_arquivos():
        linhas = arq.read_text(encoding="utf-8").split("\n")
        atual = None
        for i, linha in enumerate(linhas):
            if RE_FRAME.match(linha):
                atual = None
            m = RE_CRAR.match(linha)
            if m and atual is None:
                atual = i
                mapa.append((arq, i))
    return mapa


def escreve_k(mapa, valores: list[float]) -> None:
    por_arquivo: dict[pathlib.Path, dict[int, float]] = {}
    for (arq, i), k in zip(mapa, valores):
        por_arquivo.setdefault(arq, {})[i] = k
    for arq, edicoes in por_arquivo.items():
        linhas = arq.read_text(encoding="utf-8").split("\n")
        for i, k in edicoes.items():
            m = RE_CRAR.match(linhas[i])
            linhas[i] = f"{m.group(1)}\\CRar{{{k:g}}}"
        arq.write_text("\n".join(linhas), encoding="utf-8")


def compila() -> pathlib.Path:
    """Build SEM marca d'agua: e sobre ele que os dois instrumentos rodam."""
    return medir.build_medicao(RAIZ)


def mede() -> list[dict]:
    import tempfile
    pdf = RAIZ / "build" / "medicao.pdf"
    with tempfile.TemporaryDirectory() as tmp:
        arquivos = medir.paginas(pdf, 150, pathlib.Path(tmp))
        return [medir.mede(f, 150) for f in arquivos]


def estourou() -> set[int]:
    log = (RAIZ / "build" / "medicao.log").read_text(encoding="utf-8", errors="replace")
    import importlib
    est = importlib.import_module("estouros")
    marcas = est.paginas_do_log(log)
    ruins = set()
    for m in est.RE_OVER.finditer(log):
        ruins.add(est.pagina_em(marcas, m.start()))
    return ruins


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simular", action="store_true")
    ap.add_argument("--alvo", type=float, default=ALVO_CM)
    args = ap.parse_args()

    mapa = mapa_dos_frames()
    n = len(mapa)
    print(f"{n} frames com bot\u00e3o de ar.")

    originais = []
    for arq, i in mapa:
        linha = arq.read_text(encoding="utf-8").split("\n")[i]
        originais.append(float(RE_CRAR.match(linha).group(2)))

    # --- duas compilacoes medidas -------------------------------------------
    escreve_k(mapa, [K_A] * n)
    compila()
    a = mede()
    escreve_k(mapa, [K_B] * n)
    compila()
    b = mede()

    alvo_base = AREA_UTIL_CM - args.alvo
    ks, notas = [], []
    for i in range(n):
        ba = a[i]["base_cm"] if not a[i]["vazia"] else 0.0
        bb = b[i]["base_cm"] if not b[i]["vazia"] else 0.0
        resposta = bb - ba
        if resposta < RESPOSTA_MINIMA_CM:
            ks.append(originais[i])
            notas.append(f"NAO RESPONDE (varia {resposta:+.2f} cm de k=0 a k={K_B:g})")
            continue
        inclinacao = resposta / (K_B - K_A)
        k = K_A + (alvo_base - ba) / inclinacao
        k = max(K_MIN, min(K_MAX, round(k, 1)))
        ks.append(k)
        notas.append(f"base {ba:.2f} -> {bb:.2f} cm, {inclinacao:.3f} cm por k")

    print(f"\n{'frame':>5}  {'k':>4}  arquivo                    nota")
    print("-" * 78)
    for i, ((arq, linha), k) in enumerate(zip(mapa, ks), start=1):
        print(f"{i:>5}  {k:>4g}  {arq.name:<24}  {notas[i-1]}")

    if args.simular:
        escreve_k(mapa, originais)
        compila()
        print("\nsimulacao: os k originais foram restaurados.")
        return 0

    # --- aplica e recua onde estourou ---------------------------------------
    escreve_k(mapa, ks)
    compila()
    for tentativa in range(6):
        ruins = estourou()
        if not ruins:
            break
        print(f"recuo {tentativa + 1}: estouro nas paginas {sorted(ruins)}")
        for p in ruins:
            if 1 <= p <= n:
                ks[p - 1] = max(K_MIN, round(ks[p - 1] - 0.4, 1))
        escreve_k(mapa, ks)
        compila()

    final = mede()
    faixas = [d["faixa_cm"] for d in final if not d["vazia"]]
    faixas.sort()
    mediana = faixas[len(faixas) // 2] if faixas else 0.0
    acima = [i + 1 for i, d in enumerate(final) if d["faixa_cm"] > 1.0]
    print(f"\nmediana final da faixa vazia: {mediana:.2f} cm")
    print(f"paginas acima de 1 cm: {acima if acima else 'nenhuma'}")
    print(f"estouros restantes: {sorted(estourou()) or 'nenhum'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
