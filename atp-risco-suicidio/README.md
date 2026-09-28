# ATP Risco de suicídio: avaliação e conduta

Material da atividade teórico-prática do módulo **E3M40, Funcionalidade III,
Cognição e Humor**, do curso de Medicina do Centro Universitário Campo Real.

Prof. João Frederico Musial · 2026

> **Aviso de conteúdo.** Este repositório trata de suicídio de forma direta, com
> falas de pacientes. Se precisar se afastar da leitura, feche a página. CVV,
> ligação gratuita, **188**, 24 horas.

---

## A página publicada

A página é servida pelo GitHub Pages a partir da raiz deste repositório:

<!-- Troque USUARIO e REPOSITORIO pelos seus depois do primeiro push. -->
**https://USUARIO.github.io/REPOSITORIO/**

| Endereço | O que é |
| --- | --- |
| `/` | portal, com a tese, o aviso de conteúdo e as portas para o resto |
| `/caderno/` | caderno do estudante: os seis dossiês e a folha de trabalho |
| `/pdf/prelecao.pdf` | os 40 frames da preleção |
| `/pdf/algoritmo.pdf` | cartão de bolso do algoritmo clínico |
| `/pdf/frases.pdf` | cartão de bolso das frases que não encerram uma decisão |

O caderno é um arquivo HTML único, sem dependência externa: a folha de trabalho
é preenchível no navegador, o rascunho fica salvo apenas no aparelho do próprio
aluno e nada é enviado a lugar nenhum.

---

## Como publicar, passo a passo

1. Crie um repositório no GitHub. Ele precisa ser **público** para que o GitHub
   Pages funcione no plano gratuito.
2. Envie o conteúdo desta pasta para a raiz do repositório. Pela interface web,
   use *Add file → Upload files* e arraste tudo de uma vez; pela linha de
   comando:

   ```bash
   git init
   git add .
   git commit -m "ATP Risco de suicídio, E3M40, 2026"
   git branch -M main
   git remote add origin https://github.com/USUARIO/REPOSITORIO.git
   git push -u origin main
   ```

3. No repositório, vá em **Settings → Pages**. Em *Source*, escolha **Deploy from
   a branch**; em *Branch*, escolha **main** e a pasta **/ (root)**. Salve.
4. Espere de um a dois minutos e recarregue. O endereço aparece no alto da
   própria página de Settings → Pages.

O arquivo `.nojekyll` na raiz existe para que o GitHub sirva os arquivos como
estão, sem passar pelo Jekyll. Não o apague.

---

## O que NÃO está aqui, e por quê

O **gabarito docente** e o **handout de condução** ficaram deliberadamente fora
deste repositório, na pasta `MATERIAL-DOCENTE` que acompanha o pacote de
entrega. O motivo é simples e vale a pena repetir: em repositório público, todo
arquivo versionado fica acessível pela árvore do repositório, mesmo sem link em
página nenhuma. Versionar o gabarito aqui entregaria à turma, antes da
atividade, as formulações defensáveis, as condutas inadequadas e os erros
previsíveis de cada um dos seis casos, que é exatamente o que a plenária existe
para construir.

O `.gitignore` deste repositório já bloqueia os padrões `gabarito*`, `handout*` e
`docente/`, de modo que um `git add .` distraído não os sobe. Se um dia você
quiser versioná-los, use um repositório privado separado.

---

## Estrutura

```
index.html            portal do módulo
caderno/index.html    caderno do estudante, arquivo único e autocontido
pdf/                  preleção e os dois cartões de bolso
fontes/               fontes LuaLaTeX da preleção e as ferramentas de medição
  main.tex            preâmbulo e \input, nenhum frame
  preamble.tex        tipografia, cores, o botão de ar \CRar
  tema/               o .sty institucional, as caixas e o vocabulário TikZ
  conteudo/           os 42 frames, um arquivo por parte da aula
  ilustracoes/        a aquarela de capa e de fundo, e a nota da camada visual
  ferramentas/        medição, calibração, símbolos, aceite e empacotamento
  fonte/              os seis dossiês e a folha de trabalho, em texto
  isolados/           os dois PDFs de bolso, mesma fonte dos frames 39 e 40
```

## Como recompilar

LuaLaTeX, duas passadas. As dependências são o TeX Live com `beamer`,
`fontawesome5`, `pgfplots` e `tcolorbox`, mais as fontes Libertinus Serif e
Roboto instaladas no sistema.

```bash
cd fontes
lualatex main.tex && lualatex main.tex
```

Para reconstruir as páginas HTML e refazer a separação entre público e docente:

```bash
python3 ferramentas/build_portal.py
python3 ferramentas/build_caderno.py
python3 ferramentas/empacotar_github.py
```

A revisão estética é medida, e não conferida a olho. Os instrumentos rodam sobre
um build sem a marca d'água, porque a aquarela do fundo é lida como tinta pelo
medidor e a barra de rodapé, desenhada depois do conteúdo, esconde o transbordo:

```bash
python3 ferramentas/medir.py --dpi 150   # compila sem fundo e mede
python3 ferramentas/estouros.py          # transbordo por frame, lido no log
python3 ferramentas/calibrar.py          # recalcula o ar de cada frame
python3 ferramentas/simbolos.py          # confere cada símbolo usado
python3 ferramentas/aceite.py            # a lista de aceite, item a item
```

---

## Fontes e verificação

Todas as afirmações normativas do material foram conferidas na fonte oficial, e
o registro dessa conferência está em `fontes/fonte/verificacao-fontes.md`, com o
que foi lido e o que ficou pendente. As principais são a Lei 10.216/2001, a
Portaria GM/MS 2.391/2002, a Resolução CFM 2.057/2013, a Lei 13.819/2019, a
Portaria GM/MS 1.061/2020 e o Parecer CFM 20/2024. A epidemiologia vem do
Boletim Epidemiológico volume 55, número 4, de 2024, do Ministério da Saúde.

O material separa, no próprio texto, o que é norma, o que é recomendação apoiada
em evidência e o que é interpretação clínica.

---

## Licença

O conteúdo didático deste repositório, incluindo os dossiês, a preleção e as
páginas HTML, está sob
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.pt-br):
uso livre com atribuição, sem fins comerciais, e derivações sob a mesma licença.

As ferramentas em `fontes/ferramentas/` estão sob licença MIT, para que o método
de medição possa ser reusado sem as restrições acima. Veja `LICENSE` e
`LICENSE-ferramentas`.

A aquarela de capa e de fundo é de autoria do docente e acompanha a mesma
licença do conteúdo.

---

## Aviso

Material didático de graduação. Não substitui protocolo institucional, diretriz
vigente nem avaliação clínica presencial. Os casos são fictícios e foram
escritos para esta atividade; nenhum descreve método, letalidade comparada ou
cena.
