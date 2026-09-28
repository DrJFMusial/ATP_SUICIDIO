# ATP "Risco de Suicídio: avaliação e conduta"

Módulo E3M40, Funcionalidade III, Cognição e Humor. Medicina, Centro Universitário Campo
Real, 2026. Prof. João Frederico Musial. Turma de 62 alunos, docente conduzindo sozinho,
sessão das 13h30 às 17h00 em dois tempos.

## O que está aqui

```
main.tex                   preâmbulo e \input, nenhum frame
preamble.tex               tipografia, cores, \CRar, camadas do tema
tema/
  beamercolorthemecamporeal.sty   paleta institucional, com as duas correções declaradas
  boxes.tex                as seis caixas, ferramentas de tabela, \quadroDx
  tikz.tex                 conjunto musial*, atalhos crnode/crseta/passo, \bandaimg
conteudo/
  00-abertura.tex          frames 01 a 03
  01-fenomenologia.tex     frames 04 a 08
  02-entrevista.tex        frames 09 a 15
  03-formulacao.tex        frames 16 a 20
  03b-contextos.tex        frames 21 e 22
  04-conduta.tex           frames 23 a 29
  05-disposicao.tex        frames 30 a 35
  06-continuidade.tex      frames 36 a 38
  07-sintese.tex           chama os dois arquivos abaixo
  07a-algoritmo.tex        frame 39, compartilhado com o PDF isolado
  07b-frases.tex           frame 40, compartilhado com o PDF isolado
  08-atividade.tex         frames 41 e 42, a transição para a atividade
isolados/                  os dois PDFs de bolso, mesma fonte dos frames 39 e 40
docente/                   handout e gabarito em A4, LuaLaTeX
caderno/                   caderno do estudante em HTML, para o site do módulo
fonte/                     os textos, fonte única de verdade dos A4 e do HTML
ilustracoes/               CAPA.jpg, BACKGROUND.jpg e a nota da camada visual
ferramentas/               arte, símbolos, medição, calibração e aceite
```

## Como compilar

Tudo com LuaLaTeX, duas passadas.

```
lualatex main.tex && lualatex main.tex

cd docente && lualatex gabarito.tex && lualatex gabarito.tex
cd docente && lualatex handout.tex  && lualatex handout.tex

python3 ferramentas/md2tex.py --sem-titulo fonte/gabarito.md docente/corpo-gabarito.tex
python3 ferramentas/md2tex.py --sem-titulo fonte/handout-docente.md docente/corpo-handout.tex
python3 ferramentas/build_caderno.py
```

Os dois PDFs isolados compilam da raiz, para que os caminhos relativos de `tema/` e
`conteudo/` continuem valendo:

```
cp isolados/algoritmo.tex _iso_algoritmo.tex
lualatex -jobname=algoritmo _iso_algoritmo.tex
```

## Revisão estética medida

Os dois instrumentos rodam juntos, sempre, e sobre um build sem marca d'água. A barra de
rodapé do tema é desenhada depois do conteúdo e esconde o transbordo do medidor de tinta;
só o log denuncia.

```
python3 ferramentas/medir.py main.pdf --dpi 150
python3 ferramentas/estouros.py
python3 ferramentas/calibrar.py          # recalcula o k de cada frame
python3 ferramentas/aceite.py            # a lista do item R, item a item
```

O ar vertical de cada frame vem de um botão único, `\CRar{k}`, escrito em uma linha no
próprio arquivo do frame, porque o frame do Beamer é um grupo TeX. De k derivam a
distância entre caixas, o respiro interno, a entrelinha do corpo, a separação de itens e a
altura de linha de tabela. Incremento igual para todas as páginas não serve: a folga varia
de página para página.

As páginas sem caixa de texto não respondem ao ar. `calibrar.py` as marca como NÃO
RESPONDE, e elas se resolvem na geometria do desenho, em minimum height, node distance e
corpo de letra, nunca em caixa alta com uma linha dentro.

## Estado da última medição

Mediana da faixa vazia acima do rodapé em 0,12 cm. Nenhuma página acima de 1 cm. Nenhuma
página encostando no rodapé. Zero overfull vbox e zero overfull hbox acima de 1 pt.
Quarenta frames de preleção e dois de transição para a atividade.

## O que ainda depende de você

As três ilustrações, cujos prompts estão em `ilustracoes/PROMPTS.md`, com o slot já
posicionado e compilando vazio. E as quatro confirmações listadas no fim do handout
docente, que dependem da configuração local dos serviços de Guarapuava.
