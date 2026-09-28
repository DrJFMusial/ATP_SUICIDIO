# Camada visual: a aquarela e os símbolos

## Os dois arquivos

`CAPA.jpg` e `BACKGROUND.jpg` são as duas versões da mesma arte, ambas em 4:3,
2560 × 1920, derivadas por `ferramentas/arte43.py` das duas imagens 16:9 que você
enviou. A conversão não recorta nem deforma: ela separa a faixa de cima e a faixa
de baixo da arte original, encosta cada uma na borda correspondente da tela 4:3 e
preenche o miolo com o próprio tom de papel, esfumando a costura em 90 pixels. O
resultado preserva os quatro motivos nos quatro cantos, que é o que a composição
usa.

`CAPA.jpg` é a versão plena e sangra de borda a borda no frame 1. `BACKGROUND.jpg`
recebe ainda um véu de 55% sobre o tom de papel, porque entra como marca d'água
sob texto corrido e precisa ficar abaixo do limiar de disputa com a leitura.

## O que os quatro cantos dizem

Lidos em sentido horário a partir do alto e à esquerda, são a própria cadeia da
aula: o sofrimento isolado, o cuidado clínico, a rede que acolhe e o contato que
se oferece. Por isso a capa não é decorativa e o fundo, mesmo esmaecido, mantém
coerência com o conteúdo de cada parte.

## Build de medição

A aquarela é lida como tinta pelo `medir.py`. Todo build de medição roda sem ela:

```
lualatex "\def\CRsemfundo{}\input{main.tex}"
```

`ferramentas/medir.py` faz isso sozinho quando chamado sem argumento, e grava
`build/medicao.pdf`. `calibrar.py`, `estouros.py` e `aceite.py` leem esse build.

## Símbolos

O deck usa 38 símbolos, todos do fontawesome5. Cada um passou por dois testes, e
`ferramentas/simbolos.py` refaz os dois a qualquer momento:

```
python3 ferramentas/simbolos.py --anexo /caminho/symbols-a4.pdf
```

O primeiro teste é estar documentado na Comprehensive LaTeX Symbol List. O
segundo é existir nesta instalação, verificado por `\ifcsname` compilado. Os dois
são necessários: a lista documenta a família inteira do pacote, e versões
diferentes do fontawesome5 definem conjuntos diferentes de macros, de modo que
há nome documentado que não compila e nome que compila aqui e não compila na
máquina ao lado.

Nenhum símbolo é decorativo. Cada uma das seis caixas semânticas carrega sempre o
mesmo ícone, definido em `tema/boxes.tex`: comentários para avaliação e
entrevista, relógio para mudança recente e vigilância, ambulância para ação
imediata e disposição, mãos para suporte e continuidade, balança para norma e
registro, comprimidos para farmacologia. Cor e ícone andam juntos e nenhum dos
dois aparece sozinho. Nos títulos de frame o ícone é de orientação: diz em que
etapa da cadeia o aluno está sem que ele precise ler o título inteiro.
