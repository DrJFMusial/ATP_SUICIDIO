#!/usr/bin/env python3
"""Monta o caderno do estudante em HTML autocontido.

Le os seis dossies de fonte/ e monta um unico arquivo, sem dependencia externa,
para publicacao no site do modulo. A folha de trabalho de sete campos e
preenchivel no navegador, com rascunho salvo no proprio aparelho do aluno.

Uso: python3 ferramentas/build_caderno.py
Saida: caderno/caderno-do-estudante.html
"""
import html as _html
import json
import pathlib
import re

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FONTE = RAIZ / "fonte"
SAIDA = RAIZ / "caderno" / "caderno-do-estudante.html"

def arte(nome: str) -> str:
    """Faixa de aquarela embutida como data URI, para o caderno continuar
    sendo um arquivo unico publicavel no site do modulo."""
    p = RAIZ / "caderno" / f"_{nome}.b64"
    return f"data:image/jpeg;base64,{p.read_text().strip()}" if p.exists() else ""


CASOS = [
    ("caso-01.md", 1, "Depressão maior"),
    ("caso-02.md", 2, "Depressão maior"),
    ("caso-03.md", 3, "Transtorno bipolar, episódio misto"),
    ("caso-04.md", 4, "Transtorno de personalidade borderline"),
    ("caso-05.md", 5, "Intoxicação aguda por álcool"),
    ("caso-06.md", 6, "Quadro psicótico"),
]

CAMPOS = [
    (1, "Suicidalidade atual", 4,
     "O que existe agora, com que frequência, quanto dura, se é possível afastar, "
     "se há intenção, plano, preparação e acesso. Descrever, não classificar."),
    (2, "Modificadores relevantes agora", 4,
     "O que mudou nas últimas horas e nos últimos dias, e o que nesse paciente eleva "
     "ou reduz o risco neste momento. Nomear apenas os que mudam a conduta de vocês."),
    (3, "Segurança e suporte disponíveis", 3,
     "Quem está disponível, o que essa pessoa consegue sustentar de fato, e o que é "
     "possível restringir de acesso hoje."),
    (4, "Conduta imediata", 5,
     "O que vocês fazem nos próximos trinta minutos e nas próximas horas, incluindo "
     "a decisão sobre o ambiente e quem participa dela."),
    (5, "Continuidade do cuidado", 4,
     "Data, local, responsável, via de contato e o que o paciente faz se piorar. A "
     "expressão retorno se piorar não conta como resposta."),
    (6, "Que informação ainda falta", 3,
     "Apenas as ausências que mudariam a conduta de vocês, não a lista de tudo o que "
     "não foi perguntado."),
    (7, "Qual conclusão seria tentadora, mas os dados não permitem", 2,
     "A inferência que o caso convida a fazer e que vocês recusaram, e por quê."),
]

# ---------------------------------------------------------------- parsing ----

def carrega_caso(arquivo: str) -> dict:
    texto = (FONTE / arquivo).read_text(encoding="utf-8")
    blocos = re.split(r"\n## ", texto)
    cabecalho = blocos[0]
    secoes = {}
    for bloco in blocos[1:]:
        linhas = bloco.split("\n")
        secoes[linhas[0].strip()] = "\n".join(linhas[1:]).strip()
    return {"cabecalho": cabecalho, "secoes": secoes}


def inline(txt: str) -> str:
    """Negrito markdown para HTML, com escape de tudo o mais."""
    partes = re.split(r"(\*\*[^*]+\*\*)", txt)
    saida = []
    for p in partes:
        if p.startswith("**") and p.endswith("**"):
            saida.append("<strong>" + _html.escape(p[2:-2]) + "</strong>")
        else:
            saida.append(_html.escape(p))
    return "".join(saida)


def paragrafos(txt: str) -> str:
    """Converte prosa, citacoes e listas simples em HTML."""
    saida, buffer, modo = [], [], None

    def libera():
        nonlocal buffer, modo
        if not buffer:
            modo = None
            return
        if modo == "quote":
            falas = []
            atual = []
            for ln in buffer:
                if ln == "":
                    if atual:
                        falas.append(" ".join(atual))
                        atual = []
                else:
                    atual.append(ln)
            if atual:
                falas.append(" ".join(atual))
            corpo = "".join(f"<p>{inline(f)}</p>" for f in falas)
            saida.append(f"<blockquote>{corpo}</blockquote>")
        elif modo == "list":
            itens = "".join(f"<li>{inline(i)}</li>" for i in buffer)
            saida.append(f"<ul>{itens}</ul>")
        else:
            saida.append(f"<p>{inline(' '.join(buffer))}</p>")
        buffer, modo = [], None

    for linha in txt.split("\n"):
        bruta = linha.rstrip()
        if not bruta.strip():
            # Linha em branco encerra o bloco. Dentro de uma citacao, a separacao
            # entre as falas do mesmo turno e feita pela linha ">" solitaria.
            libera()
            continue
        if bruta.startswith("> "):
            if modo != "quote":
                libera()
                modo = "quote"
            buffer.append(bruta[2:].strip())
        elif bruta.startswith(">"):
            if modo == "quote":
                buffer.append("")
        elif bruta.startswith("- "):
            if modo != "list":
                libera()
                modo = "list"
            buffer.append(bruta[2:].strip())
        elif bruta.startswith("*(") and bruta.endswith(")*"):
            libera()
            saida.append(f'<p class="rubrica">{inline(bruta[2:-2])}</p>')
        else:
            if modo == "list":
                buffer[-1] += " " + bruta.strip()
            else:
                if modo != "para":
                    libera()
                    modo = "para"
                buffer.append(bruta.strip())
    libera()
    return "".join(saida)

# -------------------------------------------------------------------- css ----

CSS = """
:root{
  --azul:#003366; --azul-8:#eef3f8; --azul-16:#dde7f1;
  --amarelo:#FFD700; --vinho:#7A0019; --verde:#1B8A5A; --ambar:#BF7A00;
  --grafite:#3A3F45; --roxo:#662D91;
  --papel:#faf9f7; --carta:#fffefb; --linha:#dfdbd4; --tinta:#1b1b1b;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:70px}
body{margin:0;background:var(--papel);color:var(--tinta);
  font:16.5px/1.64 "Libertinus Serif","Linux Libertine O",Georgia,"Times New Roman",serif;}
.wrap{max-width:880px;margin:0 auto;padding-block:0;padding-left:18px;padding-right:18px}

/* ------------------------------------------------------------- topo ----- */
.barra{position:sticky;top:0;z-index:40;background:var(--azul);color:#fff;
  box-shadow:0 1px 8px rgba(0,0,0,.18)}
.barra .wrap{display:flex;align-items:center;gap:14px;min-height:46px;
  padding-top:6px;padding-bottom:6px;flex-wrap:wrap}
.barra .marca{font:700 12.5px/1 Roboto,"Helvetica Neue",system-ui,sans-serif;
  letter-spacing:.09em;text-transform:uppercase;white-space:nowrap}
.barra nav{display:flex;gap:3px;flex-wrap:wrap;margin-left:auto}
.barra nav a{color:#cfe0f0;text-decoration:none;font:600 12.5px/1 Roboto,system-ui,sans-serif;
  padding:6px 8px;border-radius:4px}
.barra nav a:hover{background:rgba(255,255,255,.13);color:#fff}
.barra nav a.destaque{background:var(--amarelo);color:#2b2000}
.barra nav a.destaque:hover{background:#ffe34d;color:#2b2000}

header.capa{position:relative;isolation:isolate;border-bottom:1px solid var(--linha);
  background:var(--carta) center top/cover no-repeat;
  background-image:var(--arte-topo)}
header.capa::before{content:"";position:absolute;inset:0;z-index:0;
  background:linear-gradient(90deg,
    rgba(255,254,251,.50) 0%, rgba(255,254,251,.93) 20%,
    rgba(255,254,251,.93) 74%, rgba(255,254,251,.50) 100%)}
header.capa .wrap{padding-block:52px;position:relative;z-index:1}
.capa .kicker{font:700 12px/1.4 Roboto,system-ui,sans-serif;letter-spacing:.13em;
  text-transform:uppercase;color:var(--vinho)}
.capa h1{font:700 clamp(25px,5.2vw,36px)/1.16 Roboto,system-ui,sans-serif;
  color:var(--azul);margin:8px 0 6px;letter-spacing:-.01em}
.capa .sub{font-size:17.5px;color:var(--grafite);margin:0 0 16px;max-width:46ch}
.capa .creditos{font:400 14px/1.5 Roboto,system-ui,sans-serif;color:var(--grafite);
  border-top:1px solid var(--linha);padding-top:13px}
.capa .creditos b{color:var(--azul);font-weight:600}

/* ------------------------------------------------------------ avisos ---- */
.aviso{background:#fdf7e6;border:1px solid #e8d38a;border-left:5px solid var(--amarelo);
  border-radius:0 6px 6px 0;padding:16px 20px;margin:26px 0}
.aviso h2{font:700 13px/1.3 Roboto,system-ui,sans-serif;letter-spacing:.09em;
  text-transform:uppercase;color:#7a5c00;margin:0 0 8px}
.aviso p{margin:0 0 8px;font-size:15.6px}
.aviso p:last-child{margin:0}
.aviso .cvv{font:600 16px/1.4 Roboto,system-ui,sans-serif;color:var(--vinho)}

.tese{background:var(--azul-8);border-left:5px solid var(--azul);border-radius:0 6px 6px 0;
  padding:16px 20px;margin:22px 0 30px}
.tese .rotulo{font:700 12px/1.3 Roboto,system-ui,sans-serif;letter-spacing:.1em;
  text-transform:uppercase;color:var(--azul);margin-bottom:7px}
.tese p{margin:0 0 9px}
.tese p:last-child{margin:0}
.tese .refrao{font-weight:600;color:var(--azul)}

/* ------------------------------------------------------------- casos ---- */
.grade{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:11px;
  margin:18px 0 34px}
.cartao{display:block;text-decoration:none;background:var(--carta);
  border:1px solid var(--linha);border-top:3px solid var(--azul);border-radius:5px;
  padding:13px 15px;transition:box-shadow .15s,transform .15s}
.cartao:hover{box-shadow:0 3px 12px rgba(0,51,102,.13);transform:translateY(-1px)}
.cartao .n{font:700 11.5px/1 Roboto,system-ui,sans-serif;letter-spacing:.1em;
  text-transform:uppercase;color:var(--vinho)}
.cartao .t{font:600 16.5px/1.3 Roboto,system-ui,sans-serif;color:var(--azul);margin-top:5px}
.cartao .p{font-size:13.5px;color:var(--grafite);margin-top:3px}

section.caso{background:var(--carta);border:1px solid var(--linha);border-radius:7px;
  padding:28px 32px;margin:0 0 24px;box-shadow:0 1px 3px rgba(0,0,0,.045)}
section.caso > .id{font:700 11.5px/1 Roboto,system-ui,sans-serif;letter-spacing:.12em;
  text-transform:uppercase;color:var(--vinho)}
section.caso > h2{font:700 23px/1.24 Roboto,system-ui,sans-serif;color:var(--azul);
  margin:7px 0 3px}
section.caso > .par{font-size:14.5px;color:var(--grafite);margin:0 0 4px;
  padding-bottom:11px;border-bottom:2px solid var(--amarelo)}
section.caso h3{font:600 14px/1.3 Roboto,system-ui,sans-serif;color:var(--vinho);
  letter-spacing:.02em;margin:24px 0 7px;text-transform:uppercase;font-size:12.5px}
p{margin:0 0 11px}
ul{margin:7px 0 12px;padding-left:21px}
li{margin:4px 0}
blockquote{margin:12px 0;padding:11px 17px;background:var(--azul-8);
  border-left:3px solid var(--azul);border-radius:0 5px 5px 0;font-size:15.8px}
blockquote p{margin:0 0 7px}
blockquote p:last-child{margin:0}
blockquote strong{color:var(--vinho);font-weight:600}
p.rubrica{font-style:italic;color:var(--grafite);font-size:14.5px;margin:12px 0 6px}
.ausencia{background:#f6f6f4;border:1px dashed #c4bfb6;border-radius:5px;
  padding:11px 16px;margin-top:6px}
.ausencia ul{margin:0;padding-left:20px}
.ausencia li{font-size:15.3px}

/* ------------------------------------------------------------- folha ---- */
section.folha{background:var(--carta);border:1px solid var(--linha);border-radius:7px;
  padding:28px 32px;margin:0 0 24px;box-shadow:0 1px 3px rgba(0,0,0,.045)}
section.folha > h2{font:700 23px/1.24 Roboto,system-ui,sans-serif;color:var(--azul);
  margin:0 0 4px;padding-bottom:11px;border-bottom:2px solid var(--amarelo)}
.regra{background:#fbeced;border-left:4px solid var(--vinho);border-radius:0 5px 5px 0;
  padding:12px 17px;margin:16px 0 6px;font-size:15.6px}
.regra b{color:var(--vinho)}
.identifica{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0 4px}
.identifica label{flex:1 1 150px;font:600 12px/1.5 Roboto,system-ui,sans-serif;
  letter-spacing:.06em;text-transform:uppercase;color:var(--grafite)}
.identifica input{width:100%;margin-top:4px;padding:8px 10px;border:1px solid var(--linha);
  border-radius:4px;font:400 15px/1.4 inherit;background:#fcfcfb;color:var(--tinta)}
.campo{margin:22px 0 0;border-top:1px solid var(--linha);padding-top:16px}
.campo .cab{display:flex;align-items:baseline;gap:9px;flex-wrap:wrap}
.campo .num{flex:0 0 auto;width:25px;height:25px;border-radius:50%;background:var(--azul);
  color:#fff;font:700 13px/25px Roboto,system-ui,sans-serif;text-align:center}
.campo .nome{font:600 17px/1.3 Roboto,system-ui,sans-serif;color:var(--azul)}
.campo .limite{margin-left:auto;font:600 11.5px/1 Roboto,system-ui,sans-serif;
  letter-spacing:.06em;text-transform:uppercase;color:var(--ambar);white-space:nowrap}
.campo .dica{font-size:14.7px;color:var(--grafite);margin:6px 0 8px}
.campo textarea{width:100%;padding:10px 12px;border:1px solid var(--linha);border-radius:5px;
  font:400 15.6px/1.55 inherit;background:#fcfcfb;color:var(--tinta);resize:vertical}
.campo textarea:focus{outline:2px solid var(--azul);outline-offset:-1px;background:#fff}
.campo .contador{font:600 12px/1 Roboto,system-ui,sans-serif;color:var(--grafite);
  margin-top:5px;text-align:right}
.campo .contador.excedeu{color:var(--vinho)}
.acoes{display:flex;gap:10px;flex-wrap:wrap;margin:26px 0 0;
  border-top:1px solid var(--linha);padding-top:18px}
button{font:600 14px/1 Roboto,system-ui,sans-serif;padding:11px 17px;border-radius:5px;
  border:1px solid var(--azul);background:var(--azul);color:#fff;cursor:pointer}
button:hover{background:#00284f}
button.sec{background:#fff;color:var(--azul)}
button.sec:hover{background:var(--azul-8)}
button.risco{border-color:var(--vinho);background:#fff;color:var(--vinho)}
button.risco:hover{background:#fbeced}
.recado{font:600 13.5px/1.5 Roboto,system-ui,sans-serif;color:var(--verde);
  margin:10px 0 0;min-height:20px}

.defesa{background:var(--azul-8);border-left:5px solid var(--azul);border-radius:0 6px 6px 0;
  padding:16px 20px;margin:26px 0 0}
.defesa h3{font:700 12.5px/1.3 Roboto,system-ui,sans-serif;letter-spacing:.09em;
  text-transform:uppercase;color:var(--azul);margin:0 0 8px}
.defesa p{margin:0 0 8px;font-size:15.6px}
.defesa p:last-child{margin:0}

.faixa-arte{height:132px;margin-top:30px;border-top:1px solid var(--linha);
  background:var(--carta) center bottom/cover no-repeat;background-image:var(--arte-base)}
footer.rodape{background:var(--azul);color:#c9dcee}
footer.rodape .wrap{padding-block:22px;font:400 13.5px/1.6 Roboto,system-ui,sans-serif}
footer.rodape b{color:#fff;font-weight:600}
.voltar{display:inline-block;margin-top:16px;font:600 13px/1 Roboto,system-ui,sans-serif;
  color:var(--azul);text-decoration:none}
.voltar:hover{text-decoration:underline}

@media (max-width:560px){
  body{font-size:16px}
  section.caso,section.folha{padding:20px 17px;border-radius:5px}
  .barra nav{width:100%;margin-left:0}
  .capa .wrap{padding-block:26px}
}
@media print{
  .barra,.acoes,.grade{display:none}
  body{background:#fff}
}
"""

# --------------------------------------------------------------------- js ---

JS = """
(function(){
  var CHAVE='atp-e3m40-risco-suicidio-v1';
  var campos=[].slice.call(document.querySelectorAll('[data-campo]'));
  var ident=[].slice.call(document.querySelectorAll('[data-ident]'));
  var recado=document.getElementById('recado');
  function guarda(){
    try{
      var d={};
      campos.concat(ident).forEach(function(e){d[e.id]=e.value;});
      localStorage.setItem(CHAVE,JSON.stringify(d));
    }catch(e){}
  }
  function carrega(){
    try{
      var bruto=localStorage.getItem(CHAVE); if(!bruto)return;
      var d=JSON.parse(bruto);
      campos.concat(ident).forEach(function(e){ if(typeof d[e.id]==='string') e.value=d[e.id]; });
    }catch(e){}
  }
  function conta(e){
    var alvo=document.getElementById(e.id+'-contador');
    if(!alvo)return;
    var max=parseInt(e.getAttribute('data-linhas'),10);
    var linhas=e.value.split('\\n').length;
    var chars=e.value.trim().length;
    var teto=max*78;
    alvo.textContent=linhas+' de '+max+' linhas, '+chars+' caracteres';
    var estourou=(linhas>max)||(chars>teto);
    alvo.className='contador'+(estourou?' excedeu':'');
  }
  campos.forEach(function(e){
    e.addEventListener('input',function(){conta(e);guarda();});
  });
  ident.forEach(function(e){e.addEventListener('input',guarda);});
  carrega();
  campos.forEach(conta);

  function texto(){
    var l=[];
    l.push('ATP Risco de Suicidio | E3M40 | Medicina | Campo Real');
    ident.forEach(function(e){ l.push(e.getAttribute('data-rotulo')+': '+e.value); });
    l.push('');
    campos.forEach(function(e){
      l.push(e.getAttribute('data-rotulo'));
      l.push(e.value.trim()||'(em branco)');
      l.push('');
    });
    return l.join('\\n');
  }
  function fala(msg){ recado.textContent=msg; setTimeout(function(){recado.textContent='';},3500); }

  document.getElementById('copiar').addEventListener('click',function(){
    var t=texto();
    if(navigator.clipboard&&navigator.clipboard.writeText){
      navigator.clipboard.writeText(t).then(function(){fala('Folha copiada para a area de transferencia.');},
        function(){fala('Nao foi possivel copiar. Use o botao de baixar.');});
    } else { fala('Nao foi possivel copiar. Use o botao de baixar.'); }
  });
  document.getElementById('baixar').addEventListener('click',function(){
    var grupo=(document.getElementById('id-grupo').value||'grupo').replace(/[^0-9A-Za-z]/g,'');
    var blob=new Blob([texto()],{type:'text/plain;charset=utf-8'});
    var a=document.createElement('a');
    a.href=URL.createObjectURL(blob);
    a.download='folha-'+(grupo||'grupo')+'.txt';
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function(){URL.revokeObjectURL(a.href);},1000);
    fala('Arquivo gerado.');
  });
  document.getElementById('limpar').addEventListener('click',function(){
    if(!confirm('Apagar tudo o que foi escrito nesta folha?'))return;
    campos.concat(ident).forEach(function(e){e.value='';});
    try{localStorage.removeItem(CHAVE);}catch(e){}
    campos.forEach(conta); fala('Folha limpa.');
  });
})();
"""

# ------------------------------------------------------------------ build ---

def bloco_caso(arquivo: str, numero: int, rotulo: str) -> str:
    dados = carrega_caso(arquivo)
    cab = dados["cabecalho"]
    m = re.search(r"\*\*(Par [^*]+)\*\*", cab)
    par = m.group(1).rstrip(".") if m else ""
    secoes = dados["secoes"]
    partes = [
        f'<section class="caso" id="caso-{numero}">',
        f'<div class="id">Grupo {numero}</div>',
        f"<h2>Caso {numero}. {rotulo}</h2>",
        f'<p class="par">{_html.escape(par)}. Leia o caso inteiro antes de abrir a folha '
        f"de trabalho.</p>",
    ]
    for titulo, corpo in secoes.items():
        nome = re.sub(r"^[A-F]\.\s*", "", titulo)
        classe = ' class="ausencia"' if titulo.startswith("F.") else ""
        partes.append(f"<h3>{_html.escape(nome)}</h3>")
        if classe:
            partes.append(f"<div{classe}>{paragrafos(corpo)}</div>")
        else:
            partes.append(paragrafos(corpo))
    partes.append('<a class="voltar" href="#casos">Voltar aos seis casos</a>')
    partes.append("</section>")
    return "".join(partes)


def bloco_folha() -> str:
    p = ['<section class="folha" id="folha">',
         "<h2>Folha de trabalho</h2>",
         '<div class="regra"><b>Regra principal.</b> Nenhuma decis&atilde;o vale apenas '
         "por diagn&oacute;stico, por fator de risco ou por resultado de escala. O que "
         "voc&ecirc;s escrevem aqui &eacute; exatamente o que voc&ecirc;s v&atilde;o "
         "defender.</div>",
         '<div class="tese"><div class="rotulo">A pergunta que fecha toda '
         "avalia&ccedil;&atilde;o</div><p class=\"refrao\">&Eacute; poss&iacute;vel "
         "construir seguran&ccedil;a suficiente fora de um ambiente protegido neste "
         "momento?</p></div>",
         '<div class="identifica">',
         '<label>Grupo<input id="id-grupo" data-ident data-rotulo="Grupo" type="text" '
         'inputmode="numeric" placeholder="1 a 6"></label>',
         '<label>Caso<input id="id-caso" data-ident data-rotulo="Caso" type="text" '
         'placeholder="numero do dossie"></label>',
         '<label>Integrantes<input id="id-nomes" data-ident data-rotulo="Integrantes" '
         'type="text" placeholder="nomes"></label>',
         "</div>"]
    for n, nome, linhas, dica in CAMPOS:
        idc = f"campo-{n}"
        p.append(
            f'<div class="campo"><div class="cab"><span class="num">{n}</span>'
            f'<span class="nome">{nome}</span>'
            f'<span class="limite">at&eacute; {linhas} linhas</span></div>'
            f'<p class="dica">{dica}</p>'
            f'<textarea id="{idc}" data-campo data-linhas="{linhas}" '
            f'data-rotulo="Campo {n}. {nome}" rows="{linhas}" '
            f'placeholder="escreva aqui"></textarea>'
            f'<div class="contador" id="{idc}-contador"></div></div>'
        )
    p.append(
        '<div class="acoes">'
        '<button id="copiar" type="button">Copiar a folha</button>'
        '<button id="baixar" type="button" class="sec">Baixar como texto</button>'
        '<button id="limpar" type="button" class="risco">Limpar</button>'
        "</div>"
        '<p class="recado" id="recado"></p>'
    )
    p.append(
        '<div class="defesa"><h3>Defesa, at&eacute; 4 minutos</h3>'
        "<p>Proibido apresentar o caso. A turma j&aacute; leu todos.</p>"
        "<p>S&iacute;ntese do problema, de 30 a 45 segundos. O que modifica a "
        "preocupa&ccedil;&atilde;o, 60 segundos. Conduta, 60 segundos. Seguran&ccedil;a e "
        "continuidade, de 30 a 45 segundos. O que restar, em limita&ccedil;&atilde;o e "
        "informa&ccedil;&atilde;o faltante.</p>"
        "<p><strong>Pergunta da defesa:</strong> qual &eacute; a formula&ccedil;&atilde;o "
        "de voc&ecirc;s e o que fariam agora?</p></div>"
    )
    p.append(
        '<p style="font-size:14px;color:var(--grafite);margin-top:16px">O que voc&ecirc;s '
        "escrevem fica guardado apenas neste aparelho e neste navegador. Nada &eacute; "
        "enviado a lugar nenhum. Use o bot&atilde;o de copiar ou de baixar para entregar.</p>"
    )
    p.append("</section>")
    return "".join(p)


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--portal", action="store_true",
                    help="acrescenta o link de volta ao portal e grava em caderno/index.html")
    ap.add_argument("--saida", default="")
    args = ap.parse_args()
    volta = ('<a href="../">In\u00edcio</a>' if args.portal else "")

    cartoes = "".join(
        f'<a class="cartao" href="#caso-{n}"><div class="n">Grupo {n}</div>'
        f'<div class="t">Caso {n}</div><div class="p">{rot}</div></a>'
        for _, n, rot in CASOS
    )
    casos_html = "".join(bloco_caso(a, n, r) for a, n, r in CASOS)

    arte_topo, arte_base = arte("faixa"), arte("rodape")
    doc = f"""<!doctype html>
<html lang="pt-BR"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<meta name="description" content="Caderno do estudante da ATP Risco de Suicidio, modulo E3M40, Medicina, Centro Universitario Campo Real.">
<title>ATP Risco de Suic&iacute;dio | Caderno do estudante</title>
<style>:root{{--arte-topo:url("{arte_topo}");--arte-base:url("{arte_base}")}}
{CSS}</style>
</head><body>

<div class="barra"><div class="wrap">
  <div class="marca">Medicina | Campo Real</div>
  <nav>
    {volta}<a href="#casos">Casos</a>
    <a href="#caso-1">1</a><a href="#caso-2">2</a><a href="#caso-3">3</a>
    <a href="#caso-4">4</a><a href="#caso-5">5</a><a href="#caso-6">6</a>
    <a href="#folha" class="destaque">Folha de trabalho</a>
  </nav>
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
    <p>Este material trata de suic&iacute;dio de forma direta, com falas de pacientes.
       Se em algum momento voc&ecirc; precisar se afastar, saia da sala ou feche a
       p&aacute;gina. N&atilde;o &eacute; preciso justificar, e isso n&atilde;o ser&aacute;
       registrado de nenhuma forma.</p>
    <p class="cvv">CVV, liga&ccedil;&atilde;o gratuita, 188, 24 horas.</p>
    <p>O apoio ao estudante do Centro Universit&aacute;rio Campo Real est&aacute;
       dispon&iacute;vel para quem quiser conversar depois da aula, e o docente
       tamb&eacute;m est&aacute;.</p>
  </div>

  <div class="tese">
    <div class="rotulo">A tese da aula</div>
    <p>O risco suicida &eacute; formula&ccedil;&atilde;o cl&iacute;nica din&acirc;mica,
       constru&iacute;da pela intera&ccedil;&atilde;o entre vulnerabilidades basais e
       modificadores proximais. N&atilde;o se reduz a escore nem a categoria. A conduta
       deve produzir seguran&ccedil;a agora e continuidade depois.</p>
    <p class="refrao">&Eacute; poss&iacute;vel construir seguran&ccedil;a suficiente fora
       de um ambiente protegido neste momento?</p>
    <p>Avaliar, formular, decidir, construir seguran&ccedil;a, garantir continuidade. Ao
       final, voc&ecirc; deve saber responder: o que, neste paciente, muda o que
       voc&ecirc; far&aacute; nos pr&oacute;ximos 30 minutos?</p>
  </div>

  <h2 id="casos" style="font:700 20px/1.3 Roboto,system-ui,sans-serif;color:var(--azul);
      margin:34px 0 2px">Os seis casos</h2>
  <p style="color:var(--grafite);font-size:15.3px;margin:0">Cada grupo defende o seu, mas
     todos leem todos. A plen&aacute;ria &eacute; feita por pares de casos.</p>
  <div class="grade">{cartoes}</div>

  {casos_html}

  {bloco_folha()}

</div>

<div class="faixa-arte" role="presentation"></div>

<footer class="rodape"><div class="wrap">
  <b>ATP Risco de suic&iacute;dio: avalia&ccedil;&atilde;o e conduta</b> &middot;
  M&oacute;dulo E3M40, Funcionalidade III &middot; Medicina, Centro Universit&aacute;rio
  Campo Real &middot; 2026. Material did&aacute;tico de uso interno. Os casos s&atilde;o
  fict&iacute;cios e foram escritos para esta atividade.
</div></footer>

<script>{JS}</script>
</body></html>"""

    saida = pathlib.Path(args.saida) if args.saida else SAIDA
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(doc, encoding="utf-8")
    print(f"escrito: {saida}  ({len(doc)/1024:.1f} kB)")


if __name__ == "__main__":
    main()
