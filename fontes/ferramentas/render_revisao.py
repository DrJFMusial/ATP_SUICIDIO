#!/usr/bin/env python3
"""Gera o HTML de revisao da etapa 1: seis dossies + gabarito.

Uso: python3 ferramentas/render_revisao.py
Saida: build/REVISAO_ETAPA1.html
"""
import pathlib
import markdown

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FONTE = RAIZ / "fonte"
SAIDA = RAIZ / "build" / "REVISAO_ETAPA1.html"

ORDEM = [
    ("caso-01.md", "Caso 1"),
    ("caso-02.md", "Caso 2"),
    ("caso-03.md", "Caso 3"),
    ("caso-04.md", "Caso 4"),
    ("caso-05.md", "Caso 5"),
    ("caso-06.md", "Caso 6"),
    ("gabarito.md", "Gabarito docente"),
    ("verificacao-fontes.md", "Verificacao de fontes"),
]

CSS = """
:root{
  --azul:#003366; --azul-claro:#e8eef5; --amarelo:#FFD700; --vinho:#7A0019;
  --verde:#1B8A5A; --ambar:#BF7A00; --grafite:#3A3F45; --roxo:#662D91;
  --papel:#fbfaf8; --linha:#dcd8d1;
}
*{box-sizing:border-box}
body{margin:0;background:var(--papel);color:#1b1b1b;
  font:16px/1.62 "Libertinus Serif","Linux Libertine",Georgia,serif;}
.wrap{max-width:920px;margin:0 auto;padding-block:32px;padding-left:20px;padding-right:20px}
header.top{border-bottom:3px solid var(--azul);padding-bottom:14px;margin-bottom:26px}
header.top .kicker{font:600 12px/1.3 Roboto,system-ui,sans-serif;letter-spacing:.12em;
  text-transform:uppercase;color:var(--vinho)}
header.top h1{font:700 27px/1.22 Roboto,system-ui,sans-serif;color:var(--azul);margin:6px 0 4px}
header.top p{margin:0;color:var(--grafite);font-size:14.5px}
nav.toc{background:var(--azul-claro);border-left:4px solid var(--azul);
  padding:14px 18px;margin:0 0 30px;border-radius:0 5px 5px 0}
nav.toc strong{font:600 12px/1 Roboto,sans-serif;letter-spacing:.1em;text-transform:uppercase;
  color:var(--azul);display:block;margin-bottom:8px}
nav.toc a{color:var(--azul);text-decoration:none;border-bottom:1px solid rgba(0,51,102,.3)}
nav.toc a:hover{border-bottom-color:var(--azul)}
nav.toc li{margin:3px 0}
section.doc{background:#fff;border:1px solid var(--linha);border-radius:6px;
  padding:26px 30px;margin:0 0 26px;box-shadow:0 1px 3px rgba(0,0,0,.05)}
h1.doc-h1{font:700 22px/1.3 Roboto,sans-serif;color:var(--azul);margin:0 0 4px;
  padding-bottom:8px;border-bottom:2px solid var(--amarelo)}
h2{font:600 17px/1.3 Roboto,sans-serif;color:var(--azul);margin:26px 0 8px}
h3{font:600 14.5px/1.3 Roboto,sans-serif;color:var(--vinho);margin:20px 0 5px;
  letter-spacing:.01em}
p{margin:0 0 11px}
ul{margin:6px 0 12px;padding-left:22px}
li{margin:3px 0}
blockquote{margin:10px 0;padding:9px 16px;background:#f4f7fa;
  border-left:3px solid var(--azul);border-radius:0 4px 4px 0;font-size:15.3px}
blockquote p{margin:0 0 6px}
blockquote p:last-child{margin:0}
strong{color:var(--azul)}
blockquote strong{color:var(--vinho)}
hr{border:0;border-top:1px solid var(--linha);margin:30px 0}
code{background:#f0efec;padding:1px 5px;border-radius:3px;font-size:.9em}
footer.end{color:var(--grafite);font-size:13px;text-align:center;
  border-top:1px solid var(--linha);padding-top:16px;margin-top:8px}
@media (max-width:520px){
  section.doc{padding:20px 17px}
  body{font-size:15.5px}
  header.top h1{font-size:22px}
}
"""

def slug(name: str) -> str:
    return name.replace(".md", "").replace(".", "-")


def main() -> None:
    md = markdown.Markdown(extensions=["extra", "sane_lists"])
    corpos, toc = [], []
    for arquivo, rotulo in ORDEM:
        caminho = FONTE / arquivo
        if not caminho.exists():
            continue
        md.reset()
        html = md.convert(caminho.read_text(encoding="utf-8"))
        html = html.replace("<h1>", '<h1 class="doc-h1">', 1)
        corpos.append(f'<section class="doc" id="{slug(arquivo)}">{html}</section>')
        toc.append(f'<li><a href="#{slug(arquivo)}">{rotulo}</a></li>')

    doc = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ATP Risco de Suicidio | Etapa 1</title>
<style>{CSS}</style></head><body>
<div class="wrap">
<header class="top">
  <div class="kicker">Medicina | Campo Real &middot; E3M40 &middot; Etapa 1 para revisao</div>
  <h1>Risco de Suic&iacute;dio: avalia&ccedil;&atilde;o e conduta</h1>
  <p>Seis dossi&ecirc;s de caso, gabarito docente e registro de verifica&ccedil;&atilde;o
     das fontes. Prof. Jo&atilde;o Frederico Musial.</p>
</header>
<nav class="toc"><strong>Nesta p&aacute;gina</strong><ul>{''.join(toc)}</ul></nav>
{''.join(corpos)}
<footer class="end">Documento de trabalho da etapa 1. N&atilde;o &eacute; o caderno do
estudante nem material de distribui&ccedil;&atilde;o.</footer>
</div></body></html>"""

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(doc, encoding="utf-8")
    print(f"escrito: {SAIDA}  ({len(doc)/1024:.1f} kB)")


if __name__ == "__main__":
    main()
