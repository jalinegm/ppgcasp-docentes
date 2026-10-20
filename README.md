# profes-PPGCASP

Site do corpo docente do Mestrado Profissional em Ciências Ambientais e Sistemas Produtivos (IFFar).
Publicado com GitHub Pages em `https://<usuario>.github.io/profes-PPGCASP/`.

## Atualizar os dados

1. Substitua `dados/planilha.xlsx` pela versão atual da planilha de pontuação (aba `Lançamentos - Artigos`).
2. Substitua os arquivos `.xml` ou `.zip` do Lattes em `dados/lattes/`.
3. Coloque as fotos em `fotos/<slug-do-docente>.jpg` (ex.: `fotos/anderson-saldanha-bueno.jpg`). Sem foto, o site mostra as iniciais.
4. Rode `uv run python build.py`. Para atualizar os totais de impacto, use `uv run python build.py --buscar` (veja a seção APIs).
5. Confira em `site/index.html` (`python -m http.server -d site`).
6. Faça commit (inclusive `.cache/impacto.json`) e push na branch `main`. O GitHub Actions publica o site.

## APIs de impacto (opcional)

Os selos Altmetric e Dimensions de cada artigo carregam ao vivo no navegador e não precisam de configuração.
Os **totais** (citações e atenção Altmetric por docente e do grupo, seção "Impacto social") vêm do `--buscar`:

- Altmetric exige chave: `ALTMETRIC_API_KEY=... uv run python build.py --buscar`.
- A API de métricas do Dimensions informa que organizações não registradas não estão autorizadas; use só com autorização.

Sem `--buscar`, o site usa o cache em `.cache/impacto.json`; sem cache, os totais e a seção "Impacto social" não aparecem.

## Regras

- Artigos de 2021 a 2025. Artigo sem DOI, ou sem dados nas APIs, continua na lista.
- Blocos sem dados (impacto social, contagens do Lattes) não aparecem.
- Testes: `uv run pytest`.

## Ativar o GitHub Pages

Em Settings → Pages → Source, escolha **GitHub Actions**.
