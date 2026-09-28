# MATERIAL DOCENTE — não subir ao repositório público

Esta pasta contém o que fica **fora** do GitHub: o gabarito e o handout de
condução, com as fontes de ambos.

## Por que separado

Em repositório público, todo arquivo versionado fica acessível pela árvore do
repositório, mesmo que nenhuma página tenha link para ele. Basta um aluno abrir
a aba de código e navegar. O gabarito traz, para cada um dos seis casos, as
formulações defensáveis, o que sustenta cada uma, o que não decide sozinho, as
ausências plantadas e como percebê-las, as condutas inadequadas, o erro
previsível e a pergunta da defesa. Publicá-lo esvazia a atividade inteira: a
plenária existe justamente para a turma construir isso, e o par 1 só funciona
porque ninguém sabe de antemão que os dois dossiês foram escritos para serem
indistinguíveis fora de três elementos.

O `.gitignore` do repositório público já bloqueia os padrões `gabarito*`,
`handout*`, `docente/` e `MATERIAL-DOCENTE/`. Ainda assim, guarde esta pasta em
outro lugar: fora da pasta do repositório, o risco desaparece em vez de depender
de uma regra.

## O que há aqui

```
docente/gabarito.pdf         gabarito docente, A4, 10 páginas
docente/handout.pdf          notas de condução, A4, 6 páginas
docente/*.tex                fontes LuaLaTeX dos dois
fonte/gabarito.md            texto do gabarito, fonte única de verdade
fonte/handout-docente.md     texto do handout, fonte única de verdade
```

Os dois PDFs são gerados dos dois arquivos `.md`: edite o texto, rode o
conversor e recompile.

```bash
python3 ferramentas/md2tex.py --sem-titulo fonte/gabarito.md docente/corpo-gabarito.tex
cd docente && lualatex gabarito.tex && lualatex gabarito.tex
```

## Se um dia quiser versionar

Use um repositório **privado** separado, nunca o mesmo. Em repositório privado, o
GitHub Pages do plano gratuito não publica, o que é exatamente o comportamento
desejado aqui.

## Depois da atividade

Se você quiser liberar o gabarito para a turma depois da defesa e da plenária,
o caminho limpo é enviar o PDF pelo ambiente virtual do módulo, com data, e não
mover o arquivo para o repositório público. Assim a turma do semestre seguinte
não encontra o gabarito pronto.
