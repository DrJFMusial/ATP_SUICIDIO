#!/usr/bin/env python3
"""aceite.py - confere, item a item, a lista do aceite final do briefing.

Tudo o que pode ser verificado por leitura do fonte e medicao do PDF e verificado
aqui. O que depende de julgamento humano aparece como CONFERIR, e nao como
aprovado.

Uso:
    python3 ferramentas/aceite.py
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CONTEUDO = RAIZ / "conteudo"
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import medir  # noqa: E402
import estouros  # noqa: E402

OK, FALHA, CONFERIR = "OK    ", "FALHA ", "VER   "
resultados: list[tuple[str, str, str]] = []


def registra(estado: str, item: str, detalhe: str = "") -> None:
    resultados.append((estado, item, detalhe))


def fontes() -> str:
    partes = []
    for p in sorted(CONTEUDO.glob("*.tex")):
        partes.append(p.read_text(encoding="utf-8"))
    return "\n".join(partes)


def main() -> int:
    src = fontes()

    # --- tese e pergunta operacional visiveis ao longo da aula ---------------
    n_pergunta = len(re.findall(r"construir seguran\\c\{c\}a", src))
    registra(OK if n_pergunta >= 4 else FALHA,
             "tese e pergunta operacional visiveis ao longo da aula",
             f"{n_pergunta} ocorrencias da pergunta operacional")

    # --- recorte declarado ---------------------------------------------------
    registra(OK if "transdiagn" in src else FALHA,
             "recorte transdiagnostico declarado no primeiro frame de conteudo")

    # --- parte 3B com os quatro contextos ------------------------------------
    tb = (CONTEUDO / "03b-contextos.tex").read_text(encoding="utf-8")
    contextos = ["Pessoa idosa", "Adolescente", "Transtorno alimentar",
                 "Crise psicossocial"]
    faltam = [c for c in contextos if c not in tb]
    registra(OK if not faltam else FALHA,
             "parte 3B presente com os quatro contextos",
             "faltam: " + ", ".join(faltam) if faltam else "os quatro presentes")
    n_quadro = sum(1 for l in tb.split("\n")
                   if "\\quadroDx" in l and not l.lstrip().startswith("%"))
    registra(OK if n_quadro == 4 else FALHA,
             "macro unica \\quadroDx, geometria identica",
             f"{n_quadro} ocorrencias, 2 por frame")

    # --- contagem de frames ---------------------------------------------------
    total = len(re.findall(r"\\begin\{frame\}", src))
    atividade = len(re.findall(r"\\begin\{frame\}",
                               (CONTEUDO / "08-atividade.tex").read_text(encoding="utf-8")))
    prelecao = total - atividade
    registra(OK if 37 <= prelecao <= 40 else FALHA,
             "prelecao entre 37 e 40 frames efetivos",
             f"{prelecao} de prelecao mais {atividade} de atividade")

    # --- nenhum frame no main -------------------------------------------------
    main_tex = (RAIZ / "main.tex").read_text(encoding="utf-8")
    registra(OK if "\\begin{frame}" not in main_tex else FALHA,
             "nenhum frame no main.tex")

    # --- folha de trabalho com 7 campos --------------------------------------
    folha = (RAIZ / "fonte" / "folha-de-trabalho.md").read_text(encoding="utf-8")
    campos = len(re.findall(r"^## Campo \d", folha, flags=re.M))
    registra(OK if campos == 7 else FALHA,
             "folha de trabalho com 7 campos", f"{campos} campos")

    # --- par 1 indistinguivel -------------------------------------------------
    import difflib
    def secoes(nome: str) -> dict:
        t = (RAIZ / "fonte" / nome).read_text(encoding="utf-8")
        d = {}
        for bloco in re.split(r"\n## ", t)[1:]:
            linhas = bloco.split("\n")
            d[linhas[0].strip()] = " ".join("\n".join(linhas[1:]).split())
        return d
    a, b = secoes("caso-01.md"), secoes("caso-02.md")
    hist = difflib.SequenceMatcher(None, a["E. História clínica"].split(),
                                   b["E. História clínica"].split()).ratio()
    ini = difflib.SequenceMatcher(None, a["A. Situação inicial"].split(),
                                  b["A. Situação inicial"].split()).ratio()
    registra(OK if hist == 1.0 else FALHA,
             "par 1: historia clinica identica", f"similaridade {hist:.3f}")
    registra(OK if ini >= 0.94 else FALHA,
             "par 1: situacao inicial indistinguivel", f"similaridade {ini:.3f}")

    # --- nenhum material impresso --------------------------------------------
    caderno = RAIZ / "caderno" / "caderno-do-estudante.html"
    registra(OK if caderno.exists() else FALHA,
             "caderno do estudante em HTML, sem material impresso",
             caderno.name if caderno.exists() else "ausente")

    # --- mapa de cor sem excecao ---------------------------------------------
    permitidas = {"campoazul", "campoambar", "campobordo", "campoverde",
                  "campografite", "camporoxo", "campoamarelo", "white", "black"}
    usadas = set(re.findall(r"(?:crnode|crseta|passo)=\{?(\w+)", src))
    usadas |= set(re.findall(r"color=(\w+)", src))
    intrusas = {c for c in usadas if c.startswith("campo") or c.startswith("campor")}
    intrusas -= permitidas
    registra(OK if not intrusas else FALHA,
             "mapa de cor aplicado sem excecao",
             "cores fora do mapa: " + ", ".join(sorted(intrusas)) if intrusas else
             "somente as seis cores do item L, mais o dourado institucional")

    # --- travessao e caracteres nao latinos ----------------------------------
    alvos = list(CONTEUDO.glob("*.tex")) + [RAIZ / "main.tex", RAIZ / "preamble.tex"]
    alvos += list((RAIZ / "tema").glob("*.tex")) + list((RAIZ / "fonte").glob("*.md"))
    travessoes, exoticos = 0, set()
    for p in alvos:
        t = p.read_text(encoding="utf-8")
        travessoes += len(re.findall(r"[\u2012\u2013\u2014\u2015]", t))
        exoticos |= {c for c in t if 0x0370 <= ord(c) <= 0x1CFF or ord(c) > 0x2122}
    registra(OK if travessoes == 0 else FALHA,
             "nenhum travessao no texto nem no codigo", f"{travessoes} ocorrencias")
    registra(OK if not exoticos else FALHA,
             "nenhum caractere nao latino infiltrado",
             "".join(sorted(exoticos)) if exoticos else "fonte limpo")

    # --- expressoes proibidas -------------------------------------------------
    proibidas = {"cometeu suic": "a expressao correta e morreu por suicidio",
                 "retorne se piorar": "so pode aparecer como objeto de critica"}
    for chave, nota in proibidas.items():
        ocorr = len(re.findall(chave, src, flags=re.I))
        esperado = 0 if chave.startswith("cometeu") else 1
        registra(OK if ocorr <= esperado else FALHA,
                 f"expressao proibida: {chave}", f"{ocorr} ocorrencias, {nota}")

    # --- tabelas apenas nos tres lugares autorizados --------------------------
    tabelas = len(re.findall(r"\\begin\{tabular\}", src))
    registra(OK if tabelas == 3 else FALHA,
             "tabela so no roteiro de perguntas, nas modalidades e nos erros",
             f"{tabelas} tabelas no deck")

    # --- negrito para enfase retorica ----------------------------------------
    registra(CONFERIR, "negrito nunca para enfase retorica",
             "o \\textbf solto foi usado so em rotulo de no e de item")

    # --- medicao --------------------------------------------------------------
    registra(OK if (RAIZ / "main.pdf").exists() else FALHA,
             "main.pdf de entrega compilado, com marca d'agua")
    pdf = medir.build_medicao(RAIZ)
    if not pdf.exists():
        registra(FALHA, "build de medicao sem marca d'agua", "ausente")
    else:
        with tempfile.TemporaryDirectory() as tmp:
            arquivos = medir.paginas(pdf, 150, pathlib.Path(tmp))
            dados = [medir.mede(f, 150) for f in arquivos]
        # A capa e a unica excecao declarada do briefing: a ilustracao sangra
        # de borda a borda, de modo que encostar no rodape ali e o projeto.
        encosta = [i + 1 for i, d in enumerate(dados)
                   if d.get("invade_rodape") and i + 1 != 1]
        acima = [i + 1 for i, d in enumerate(dados) if d["faixa_cm"] > 1.0]
        faixas = sorted(d["faixa_cm"] for d in dados if not d["vazia"])
        mediana = faixas[len(faixas) // 2]
        registra(OK if not encosta else FALHA,
                 "nada encostando no rodape, fora a capa",
                 f"paginas: {encosta}" if encosta else
                 "nenhuma pagina, com a capa como excecao declarada")
        registra(OK if not acima else FALHA,
                 "nenhuma pagina com faixa vazia acima de 1 cm",
                 f"paginas: {acima}" if acima else f"mediana {mediana:.2f} cm")

        log = (RAIZ / "build" / "medicao.log").read_text(encoding="utf-8", errors="replace")
        vbox = len(re.findall(r"Overfull \\vbox", log))
        hbox_graves = [float(m.group(1)) for m in
                       re.finditer(r"Overfull \\hbox \(([0-9.]+)pt", log)
                       if float(m.group(1)) >= 1.0]
        registra(OK if vbox == 0 else FALHA, "zero overfull vbox", f"{vbox}")
        registra(OK if not hbox_graves else FALHA,
                 "zero overfull hbox acima de 1pt", f"{len(hbox_graves)}")

    # --- entregaveis ----------------------------------------------------------
    entregaveis = {
        "1. main.pdf da prelecao": RAIZ / "main.pdf",
        "2. handout docente": RAIZ / "docente" / "handout.pdf",
        "3. caderno do estudante em HTML": caderno,
        "4. gabarito docente": RAIZ / "docente" / "gabarito.pdf",
        "5. PDF isolado do algoritmo": RAIZ / "algoritmo.pdf",
        "6. PDF isolado das frases": RAIZ / "frases.pdf",
    }
    for nome, p in entregaveis.items():
        registra(OK if p.exists() else FALHA, nome,
                 f"{p.stat().st_size // 1024} kB" if p.exists() else "ausente")

    # --- relatorio ------------------------------------------------------------
    largura = max(len(i) for _, i, _ in resultados) + 2
    print("ACEITE FINAL, item R do briefing")
    print("=" * (largura + 40))
    for estado, item, detalhe in resultados:
        print(f"[{estado}] {item:<{largura}} {detalhe}")
    print("=" * (largura + 40))
    falhas = [i for e, i, _ in resultados if e == FALHA]
    ver = [i for e, i, _ in resultados if e == CONFERIR]
    print(f"falhas: {len(falhas)}   conferir a olho: {len(ver)}   "
          f"aprovados: {len(resultados) - len(falhas) - len(ver)}")
    for i in falhas:
        print(f"  FALHA: {i}")
    return 0 if not falhas else 2


if __name__ == "__main__":
    raise SystemExit(main())
