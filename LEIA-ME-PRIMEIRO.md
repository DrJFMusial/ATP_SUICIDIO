# Duas pastas, dois destinos

Este pacote está dividido em duas pastas, e a divisão é deliberada.

## `atp-risco-suicidio/` — vai para o GitHub

É o repositório público, pronto para subir. Já traz `README.md`, `LICENSE`,
`.gitignore`, `.nojekyll` e `CITATION.cff`, além da página, do caderno, dos três
PDFs e das fontes LuaLaTeX da preleção.

Passo a passo, na interface do GitHub:

1. Crie um repositório novo. Ele precisa ser **público** para o GitHub Pages
   funcionar no plano gratuito. Não marque a opção de adicionar README, porque
   já existe um aqui.
2. Na página do repositório vazio, clique em **uploading an existing file**.
   Abra esta pasta, selecione **tudo o que está dentro dela** e arraste para a
   área de upload. Confirme com *Commit changes*.
3. Vá em **Settings → Pages**. Em *Source* escolha **Deploy from a branch**; em
   *Branch* escolha **main** e a pasta **/ (root)**. Salve.
4. Espere um ou dois minutos. O endereço aparece no alto dessa mesma página de
   Settings → Pages, no formato `https://SEUUSUARIO.github.io/NOMEDOREPO/`.
5. Depois que o endereço existir, edite o `README.md` e troque `USUARIO` e
   `REPOSITORIO` pelo endereço real, para que o link no topo do repositório
   funcione.

Uma advertência sobre o upload por arrastar: o navegador não envia arquivos que
começam com ponto. `.gitignore` e `.nojekyll` são exatamente assim. Se você
subir por arrastar, crie os dois depois, pela opção *Add file → Create new
file*, colando o conteúdo que está aqui. Pela linha de comando isso não
acontece, e o `git add .` leva os dois.

O `.nojekyll` importa: sem ele o GitHub passa o site pelo Jekyll, que ignora
pastas iniciadas por sublinhado e às vezes reescreve o que não deveria. O
`.gitignore` importa porque bloqueia os padrões `gabarito*`, `handout*` e
`docente/`, de modo que um `git add .` distraído não sobe o que está na outra
pasta.

## `MATERIAL-DOCENTE/` — não vai para o GitHub

Gabarito, handout de condução e as fontes dos dois. Guarde em outro lugar, fora
da pasta do repositório. Em repositório público todo arquivo versionado fica
acessível pela árvore, mesmo sem link em página nenhuma, e o gabarito traz as
formulações defensáveis e os erros previsíveis dos seis casos. Publicá-lo
esvazia a plenária, que existe para a turma construir isso.

O `LEIA-ME.md` dessa pasta explica o raciocínio inteiro e o que fazer se você
quiser liberar o gabarito para a turma depois da defesa.

## Conferência

O empacotador roda uma verificação antes de fechar as duas pastas: nenhum
arquivo com `gabarito` ou `handout` no nome pode estar do lado público, e nenhum
arquivo público pode conter as marcas de texto do gabarito. Se qualquer uma das
duas condições falhar, ele aborta em vez de empacotar. Para refazer o pacote
depois de uma edição:

```bash
python3 ferramentas/empacotar_github.py
```
