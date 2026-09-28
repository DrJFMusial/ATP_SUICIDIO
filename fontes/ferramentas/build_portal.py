#!/usr/bin/env python3
"""build_portal.py - gera a pagina de entrada do site do modulo.

E o endereco que o aluno abre. Traz a tese, o aviso de conteudo com o CVV e as
portas para tudo o que e publico: o caderno dos seis dossies, a prelecao em PDF
e os dois cartoes de bolso. Nada do material docente e linkado aqui, e nada dele
vai para o repositorio publico.

Uso:
    python3 ferramentas/build_portal.py caminho/index.html
"""
from __future__ import annotations

import base64
import io
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent


def arte(nome: str) -> str:
    p = RAIZ / "caderno" / f"_{nome}.b64"
    return f"data:image/jpeg;base64,{p.read_text().strip()}" if p.exists() else ""


CSS = """
:root{
  --azul:#003366; --azul-8:#eef3f8; --amarelo:#FFD700; --vinho:#7A0019;
  --verde:#1B8A5A; --ambar:#BF7A00; --grafite:#3A3F45; --roxo:#662D91;
  --papel:#faf9f7; --carta:#fffefb; --linha:#dfdbd4; --tinta:#1b1b1b;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--papel);color:var(--tinta);
  font:16.5px/1.64 "Libertinus Serif","Linux Libertine O",Georgia,"Times New Roman",serif;}
.wrap{max-width:900px;margin:0 auto;padding-left:18px;padding-right:18px}

.barra{background:var(--azul);color:#fff}
.barra .wrap{display:flex;align-items:center;min-height:46px;
  padding-top:6px;padding-bottom:6px}
.barra .marca{font:700 12.5px/1 Roboto,"Helvetica Neue",system-ui,sans-serif;
  letter-spacing:.09em;text-transform:uppercase}

header.capa{position:relative;isolation:isolate;border-bottom:1px solid var(--linha);
  background:var(--carta) center top/cover no-repeat;background-image:var(--arte-topo)}
header.capa::before{content:"";position:absolute;inset:0;z-index:0;
  background:linear-gradient(90deg,
    rgba(255,254,251,.50) 0%, rgba(255,254,251,.93) 20%,
    rgba(255,254,251,.93) 74%, rgba(255,254,251,.50) 100%)}
header.capa .wrap{padding-block:60px;position:relative;z-index:1}
.capa .kicker{font:700 12px/1.4 Roboto,system-ui,sans-serif;letter-spacing:.13em;
  text-transform:uppercase;color:var(--vinho)}
.capa h1{font:700 clamp(27px,5.6vw,40px)/1.14 Roboto,system-ui,sans-serif;
  color:var(--azul);margin:9px 0 8px;letter-spacing:-.01em}
.capa .sub{font-size:18px;color:var(--grafite);margin:0;max-width:44ch}
.capa .creditos{font:400 14px/1.5 Roboto,system-ui,sans-serif;color:var(--grafite);
  border-top:1px solid var(--linha);padding-top:14px;margin-top:20px}
.capa .creditos b{color:var(--azul);font-weight:600}

.aviso{background:#fdf7e6;border:1px solid #e8d38a;border-left:5px solid var(--amarelo);
  border-radius:0 6px 6px 0;padding:16px 20px;margin:30px 0 26px}
.aviso h2{font:700 13px/1.3 Roboto,system-ui,sans-serif;letter-spacing:.09em;
  text-transform:uppercase;color:#7a5c00;margin:0 0 8px}
.aviso p{margin:0 0 8px;font-size:15.6px}
.aviso p:last-child{margin:0}
.aviso .cvv{font:600 16px/1.4 Roboto,system-ui,sans-serif;color:var(--vinho)}

.tese{background:var(--azul-8);border-left:5px solid var(--azul);border-radius:0 6px 6px 0;
  padding:16px 20px;margin:0 0 34px}
.tese .rotulo{font:700 12px/1.3 Roboto,system-ui,sans-serif;letter-spacing:.1em;
  text-transform:uppercase;color:var(--azul);margin-bottom:7px}
.tese p{margin:0 0 9px}
.tese p:last-child{margin:0}
.tese .refrao{font-weight:600;color:var(--azul)}

h2.sec{font:700 20px/1.3 Roboto,system-ui,sans-serif;color:var(--azul);margin:0 0 3px}
p.seclead{color:var(--grafite);font-size:15.3px;margin:0 0 16px}

.grade{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:13px;
  margin:0 0 34px}
.cartao{display:flex;flex-direction:column;text-decoration:none;background:var(--carta);
  border:1px solid var(--linha);border-top:3px solid var(--azul);border-radius:6px;
  padding:16px 18px;transition:box-shadow .15s,transform .15s}
.cartao:hover{box-shadow:0 4px 14px rgba(0,51,102,.14);transform:translateY(-1px)}
.cartao.destaque{border-top-color:var(--amarelo)}
.cartao .n{font:700 11.5px/1 Roboto,system-ui,sans-serif;letter-spacing:.1em;
  text-transform:uppercase;color:var(--vinho)}
.cartao .t{font:600 18px/1.3 Roboto,system-ui,sans-serif;color:var(--azul);margin-top:6px}
.cartao .p{font-size:14.6px;color:var(--grafite);margin-top:6px;flex:1}
.cartao .acao{font:600 13px/1 Roboto,system-ui,sans-serif;color:var(--azul);margin-top:12px}

.nota{border:1px dashed #c4bfb6;background:#f6f6f4;border-radius:6px;
  padding:14px 18px;margin:0 0 6px;font-size:15px;color:var(--grafite)}

.faixa-arte{height:140px;margin-top:34px;border-top:1px solid var(--linha);
  background:var(--carta) center bottom/cover no-repeat;background-image:var(--arte-base)}
footer.rodape{background:var(--azul);color:#c9dcee}
footer.rodape .wrap{padding-block:22px;font:400 13.5px/1.6 Roboto,system-ui,sans-serif}
footer.rodape b{color:#fff;font-weight:600}
footer.rodape a{color:#ffe98a}

@media (max-width:560px){
  body{font-size:16px}
  header.capa .wrap{padding-block:38px}
}
"""

PAGINA = """<!doctype html>
<html lang="pt-BR"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<meta name="description" content="ATP Risco de suicidio: avaliacao e conduta. Modulo E3M40, Medicina, Centro Universitario Campo Real.">
<title>ATP Risco de suic&iacute;dio | E3M40 | Medicina Campo Real</title>
<style>:root{{--arte-topo:url("{arte_topo}");--arte-base:url("{arte_base}")}}
{css}</style>
</head><body>

<div class="barra"><div class="wrap">
  <div class="marca">Medicina | Campo Real</div>
</div></div>

<header class="capa"><div class="wrap">
  <div class="kicker">ATP &middot; M&oacute;dulo E3M40 &middot; Funcionalidade III, Cogni&ccedil;&atilde;o e Humor</div>
  <h1>Risco de suic&iacute;dio: avalia&ccedil;&atilde;o e conduta</h1>
  <p class="sub">Seis pacientes, seis grupos. A tarefa n&atilde;o &eacute;
     classific&aacute;-los em baixo, moderado ou alto.</p>
  <div class="creditos"><b>Prof. Jo&atilde;o Frederico Musial</b> &middot; Medicina,
     Centro Universit&aacute;rio Campo Real &middot; 2026</div>
</div></header>

<div class="wrap">

  <div class="aviso">
    <h2>Antes de come&ccedil;ar</h2>
    <p>Este material trata de suic&iacute;dio de forma direta, com falas de
       pacientes. Se em algum momento voc&ecirc; precisar se afastar, feche a
       p&aacute;gina ou saia da sala. N&atilde;o &eacute; preciso justificar, e isso
       n&atilde;o ser&aacute; registrado de nenhuma forma.</p>
    <p class="cvv">CVV, liga&ccedil;&atilde;o gratuita, 188, 24 horas.</p>
    <p>O apoio ao estudante do Centro Universit&aacute;rio Campo Real est&aacute;
       dispon&iacute;vel para quem quiser conversar depois da aula, e o docente
       tamb&eacute;m est&aacute;.</p>
  </div>

  <div class="tese">
    <div class="rotulo">A tese da aula</div>
    <p>O risco suicida &eacute; formula&ccedil;&atilde;o cl&iacute;nica
       din&acirc;mica, constru&iacute;da pela intera&ccedil;&atilde;o entre
       vulnerabilidades basais e modificadores proximais. N&atilde;o se reduz a
       escore nem a categoria. A conduta deve produzir seguran&ccedil;a agora e
       continuidade depois.</p>
    <p class="refrao">&Eacute; poss&iacute;vel construir seguran&ccedil;a suficiente
       fora de um ambiente protegido neste momento?</p>
    <p>Avaliar, formular, decidir, construir seguran&ccedil;a, garantir
       continuidade. Ao final, voc&ecirc; deve saber responder: o que, neste
       paciente, muda o que voc&ecirc; far&aacute; nos pr&oacute;ximos 30 minutos?</p>
  </div>

  <h2 class="sec">Materiais da atividade</h2>
  <p class="seclead">Leia o caderno antes da sess&atilde;o. Os seis dossi&ecirc;s
     s&atilde;o lidos por todos, e n&atilde;o s&oacute; pelo pr&oacute;prio grupo.</p>

  <div class="grade">
    <a class="cartao destaque" href="caderno/">
      <div class="n">Leitura obrigat&oacute;ria</div>
      <div class="t">Caderno do estudante</div>
      <div class="p">Os seis dossi&ecirc;s de caso e a folha de trabalho de sete
         campos, preench&iacute;vel no navegador.</div>
      <div class="acao">Abrir o caderno &rarr;</div>
    </a>

    <a class="cartao" href="pdf/prelecao.pdf">
      <div class="n">Depois da aula</div>
      <div class="t">Prele&ccedil;&atilde;o completa</div>
      <div class="p">Os 40 frames da prele&ccedil;&atilde;o, em PDF, para revisar o
         que foi dito no primeiro tempo.</div>
      <div class="acao">Baixar o PDF &rarr;</div>
    </a>

    <a class="cartao" href="pdf/algoritmo.pdf">
      <div class="n">Cart&atilde;o de bolso</div>
      <div class="t">O algoritmo</div>
      <div class="p">Perguntar, caracterizar, identificar o que mudou, formular,
         decidir o ambiente, construir seguran&ccedil;a, definir continuidade.</div>
      <div class="acao">Baixar o PDF &rarr;</div>
    </a>

    <a class="cartao" href="pdf/frases.pdf">
      <div class="n">Cart&atilde;o de bolso</div>
      <div class="t">Frases que n&atilde;o encerram uma decis&atilde;o</div>
      <div class="p">As oito frases que parecem conclus&atilde;o e n&atilde;o
         s&atilde;o, com o que cada uma deixa sem resposta.</div>
      <div class="acao">Baixar o PDF &rarr;</div>
    </a>
  </div>

  <div class="nota">
    Os casos s&atilde;o fict&iacute;cios e foram escritos para esta atividade.
    Nenhum descreve m&eacute;todo, letalidade comparada ou cena. Material
    did&aacute;tico de gradua&ccedil;&atilde;o: n&atilde;o substitui protocolo
    institucional nem avalia&ccedil;&atilde;o cl&iacute;nica presencial.
  </div>

</div>

<div class="faixa-arte" role="presentation"></div>

<footer class="rodape"><div class="wrap">
  <b>ATP Risco de suic&iacute;dio: avalia&ccedil;&atilde;o e conduta</b> &middot;
  M&oacute;dulo E3M40, Funcionalidade III &middot; Medicina, Centro
  Universit&aacute;rio Campo Real &middot; 2026.<br>
  Prof. Jo&atilde;o Frederico Musial. Conte&uacute;do sob licen&ccedil;a
  <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.pt-br">CC BY-NC-SA 4.0</a>.
</div></footer>

</body></html>"""


def main() -> int:
    saida = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "build" / "index.html"
    saida.parent.mkdir(parents=True, exist_ok=True)
    doc = PAGINA.format(css=CSS, arte_topo=arte("faixa"), arte_base=arte("rodape"))
    saida.write_text(doc, encoding="utf-8")
    print(f"escrito: {saida}  ({len(doc)/1024:.1f} kB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
