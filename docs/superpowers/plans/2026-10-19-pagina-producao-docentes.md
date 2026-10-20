# Página de produção e impacto dos docentes — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Gerar site estático (GitHub Pages) com panorama do grupo e uma página por docente, com artigos 2021–2025, badges Altmetric/Dimensions e produção do Lattes.

**Architecture:** `build.py` (pacote `ppgcasp/`) lê planilha + Lattes, consulta Altmetric/Dimensions com cache em disco, monta um modelo de dados e renderiza HTML com Jinja2 em `site/`. CSS/JS são arquivos estáticos copiados para `site/`. Deploy por GitHub Actions publicando `site/`.

**Tech Stack:** Python 3.12, uv, openpyxl, Jinja2, requests, pytest. Front: HTML/CSS/JS puros.

**Spec:** `site-docentes/docs/specs/2026-10-19-pagina-producao-docentes-design.md`

## Global Constraints

- Período dos artigos: 2021–2025 (2026 excluído).
- Excluir docentes: Letícia Trevisan Gressler e Julian. Restam 17 docentes.
- Linhas: 1 = "Biodiversidade, Saúde Ambiental e Conservação"; 2 = "Inovação, Biotecnologia e Sustentabilidade Produtiva". Cleudson, Éverton, Lessandro, Luana, Tatiana → linha 2.
- Título da página geral: "Ciências Ambientais e Sistemas Produtivos". Sobretítulo: "Mestrado Profissional · Instituto Federal Farroupilha". Sem texto abaixo do título.
- Tokens: lime `#9EEA6C`, green `#58C411`, darkGreen `#244C4E`, outline `#337D63`, text `#4C5267`, background `#E2E7F1`, surface `#FFFFFF`. Fontes Fustat (títulos, 600, tracking -0.03em) e Inter Tight (corpo, 500). Raios 16/24/999px. Sem logo nem nome AbacatePay.
- Links internos relativos (site serve em `/profes-PPGCASP/`).
- Blocos sem dado (zero, indisponível) não são renderizados. Artigo sem DOI ou não encontrado nas APIs continua na lista.
- `prefers-reduced-motion` desativa animações.
- Português do Brasil em todo o texto da interface.

## Review Focus

- Artigo com DOI em formato `https://doi.org/...` ou `doi:...` ou só `10.xxx`: normalizar para `10.xxx` minúsculo sem espaço.
- API Altmetric/Dimensions fora do ar ou com timeout: build não quebra, impacto = indisponível, cache preservado.
- Nome do docente com acento quebrado (`JosÃ©`) ou em MAIÚSCULAS: exibir normalizado; slug sem acento.
- Docente sem Lattes ou ZIP sem XML legível: página só com artigos.
- Docente com 0 artigos no período: card e página renderizam sem bloco de números zerados.
- Título de artigo com `<`, `&` ou aspas: escapado no HTML.

---

## File Structure

- `site-docentes/pyproject.toml` — deps e config pytest.
- `site-docentes/ppgcasp/models.py` — dataclasses `Artigo`, `Docente`, `LattesInfo`, `Impacto`.
- `site-docentes/ppgcasp/planilha.py` — leitura da planilha.
- `site-docentes/ppgcasp/lattes.py` — leitura XML/ZIP do Lattes.
- `site-docentes/ppgcasp/impacto.py` — APIs + cache.
- `site-docentes/ppgcasp/render.py` — Jinja2 → HTML.
- `site-docentes/ppgcasp/templates/{base,index,docente}.html`
- `site-docentes/static/{style.css,app.js}`
- `site-docentes/build.py` — CLI.
- `site-docentes/tests/` — um arquivo por módulo.
- `site-docentes/.github/workflows/pages.yml`
- Dados de entrada ficam no pai: `../Planilha_de_Pontuacao_e_Prontidao_APCN_Ciencias_Ambientais.xlsx`, `../Lattes/Lattes/`.

### Task 1: Scaffold, modelos e leitura da planilha

**Files:**
- Create: `site-docentes/pyproject.toml`, `ppgcasp/__init__.py`, `ppgcasp/models.py`, `ppgcasp/planilha.py`, `tests/test_planilha.py`

**Interfaces:**
- Produces:
  - `Artigo(ano: int, titulo: str, doi: str | None)`
  - `Docente(nome: str, slug: str, linha: int, artigos: list[Artigo], lattes: LattesInfo | None, impacto: Impacto | None)`
  - `LattesInfo(resumo: str, campus: str, contagens: dict[str, int])`
  - `Impacto(citacoes: int, altmetric_score: float, noticias: int, politicas: int, disponivel: bool)`
  - `normalizar_doi(raw: str | None) -> str | None`
  - `slugify(nome: str) -> str`
  - `titulo_nome(nome: str) -> str` (corrige mojibake e caixa; mantém "de", "dos", "da" minúsculos)
  - `carregar_docentes(caminho_xlsx: Path) -> list[Docente]`

- [ ] **Step 1: Write failing tests** em `tests/test_planilha.py`: `normalizar_doi("https://doi.org/10.1/ABC")=="10.1/abc"`, `normalizar_doi(None) is None`, `normalizar_doi("doi:10.1/x")=="10.1/x"`; `titulo_nome("Cleudson JosÃ© Michelon")=="Cleudson José Michelon"`; `titulo_nome("LESSANDRO DE CONTI")=="Lessandro de Conti"`; `slugify("Éverton Lutz")=="everton-lutz"`; com a planilha real, `len(carregar_docentes(P))==17`, nenhum nome contém "Gressler", todos artigos têm `2021<=ano<=2025`, soma de artigos = 131, soma com DOI = 123, Anderson tem 15 artigos, Luana tem `linha==2`, Jonas tem `linha==1`.
- [ ] **Step 2: Run** `uv run pytest tests/test_planilha.py -v` — Expected: FAIL (módulo inexistente).
- [ ] **Step 3: Implement** `pyproject.toml` (deps: openpyxl, jinja2, requests; dev: pytest), `models.py` e `planilha.py`. Ler aba `Lançamentos - Artigos` (colunas A Docente, B Linha, C Ano, D Título, E DOI). Linha por nome da coluna B; vazia → 2 (regra da spec). Agrupar por nome normalizado (casefold + mojibake corrigido via `s.encode('latin-1').decode('utf-8')` com fallback).
- [ ] **Step 4: Run** testes — Expected: PASS.
- [ ] **Step 5: Commit** `git init` na pasta `site-docentes` se necessário; `git add . && git commit -m "feat: ler docentes e artigos da planilha"`.

### Task 2: Leitura do Lattes

**Files:**
- Create: `ppgcasp/lattes.py`, `tests/test_lattes.py`

**Interfaces:**
- Consumes: `LattesInfo`, `slugify`, `titulo_nome` (Task 1).
- Produces: `carregar_lattes(pasta: Path) -> dict[str, LattesInfo]` (chave = slug do docente); `CATEGORIAS: list[tuple[str, str]]` com (chave, rótulo) na ordem: `trabalhos_tecnicos`/"trabalhos técnicos", `eventos`/"eventos organizados", `cursos`/"cursos ministrados", `material_didatico`/"materiais didáticos", `midia`/"programas de rádio/TV e mídia", `orientacoes`/"orientações de pós-graduação".

- [ ] **Step 1: Failing tests:** com `Lattes/Lattes/`, `carregar_lattes` tem chave `anderson-saldanha-bueno` com `contagens["trabalhos_tecnicos"]>0` (só itens 2021–2025, valor ≤ 35), `resumo` não vazio, `campus` contém "Júlio de Castilhos"; ZIP e XML ambos lidos (ao menos 12 docentes presentes); arquivo ZIP corrompido (criar em `tmp_path`) é ignorado sem exceção.
- [ ] **Step 2: Run** — Expected: FAIL.
- [ ] **Step 3: Implement.** Para cada `.xml` ou `.zip` (extrair o primeiro `.xml` em memória), parsear com `xml.etree`. Nome vem de `DADOS-GERAIS@NOME-COMPLETO`. Mapear tags para categorias, filtrando pelo atributo ANO dos `DADOS-BASICOS-*`: `TRABALHO-TECNICO`, `ORGANIZACAO-DE-EVENTO`, `CURSO-DE-CURTA-DURACAO-MINISTRADO`, `DESENVOLVIMENTO-DE-MATERIAL-DIDATICO-OU-INSTRUCIONAL`, `PROGRAMA-DE-RADIO-OU-TV` + `ENTREVISTAS-MESAS-REDONDAS-PROGRAMAS-E-COMENTARIOS-NA-MIDIA`, `ORIENTACOES-CONCLUIDAS-PARA-MESTRADO` + `...-DOUTORADO`. Resumo = `RESUMO-CV@TEXTO-RESUMO-CV-RH` cortado na 1ª frase (máx. 220 caracteres). Campus = `ENDERECO-PROFISSIONAL@NOME-INSTITUICAO-EMPRESA`/`CIDADE` quando contiver "Farroupilha"; vazio se não achar. O construtor confere as tags reais abrindo um XML.
- [ ] **Step 4: Run** — Expected: PASS.
- [ ] **Step 5: Commit** `feat: ler producao do Lattes`.

### Task 3: Impacto (Altmetric + Dimensions) com cache

**Files:**
- Create: `ppgcasp/impacto.py`, `tests/test_impacto.py`

**Interfaces:**
- Consumes: `Impacto`, `Docente`.
- Produces: `buscar_impacto_doi(doi: str, cache: dict, get=requests.get) -> dict` (retorna `{"citacoes": int, "score": float, "noticias": int, "politicas": int, "ok": bool}`); `carregar_cache(path)`/`salvar_cache(path, cache)`; `somar_impacto(docente: Docente, cache: dict) -> Impacto`; `somar_grupo(docentes) -> Impacto`.

- [ ] **Step 1: Failing tests** com `get` falso (sem rede): Altmetric 404 + Dimensions 200 `{"times_cited": 7}` → citacoes 7, score 0, ok True; ambos 500/timeout → `ok False` e não grava no cache; segunda chamada com mesmo DOI não chama `get` (cache); `somar_impacto` soma dois artigos e ignora os `ok False` mas marca `disponivel` True se ao menos um ok; docente sem DOI → `Impacto(0,0,0,0,False)`.
- [ ] **Step 2: Run** — Expected: FAIL.
- [ ] **Step 3: Implement.** Altmetric `https://api.altmetric.com/v1/doi/{doi}` (campos `score`, `cited_by_msm_count`, `cited_by_policies_count`; 404 = zero). Dimensions `https://metrics-api.dimensions.ai/doi/{doi}` (campo `times_cited`). Timeout 10 s, 1 retry, pausa de 1 s entre DOIs. Cache JSON em `site-docentes/.cache/impacto.json`; só grava resultados `ok`.
- [ ] **Step 4: Run** — Expected: PASS.
- [ ] **Step 5: Commit** `feat: buscar impacto com cache`.

### Task 4: Templates e estilo

**Files:**
- Create: `ppgcasp/render.py`, `ppgcasp/templates/base.html`, `index.html`, `docente.html`, `static/style.css`, `static/app.js`, `tests/test_render.py`

**Interfaces:**
- Consumes: modelos das Tasks 1–3, `CATEGORIAS`.
- Produces: `renderizar_site(docentes: list[Docente], grupo: Impacto, saida: Path) -> None` escreve `index.html`, `docentes/<slug>.html`, copia `static/` para `saida/static/` e `fotos/` se existir.

- [ ] **Step 1: Failing tests** (renderizar em `tmp_path` com 3 docentes fictícios): `index.html` contém "Ciências Ambientais e Sistemas Produtivos", "Mestrado Profissional · Instituto Federal Farroupilha", os dois títulos de linha, link relativo `docentes/<slug>.html` (nunca começa com `/`); com `grupo.disponivel=False` ou `altmetric_score==0` não contém "Impacto social"; com score>0 contém; página do docente com artigo sem DOI contém "sem DOI" e o título; título com `<b>&` aparece escapado; docente sem `lattes` não contém "Além dos artigos"; contagem 0 não gera cartão; docente com `fotos/<slug>.jpg` existente usa `<img>`, senão iniciais; página do docente contém `data-doi="<doi>"` para `altmetric-embed` e `__dimensions_badge_embed__`, e os scripts `embed.js` e `badge.js`; link "← Corpo docente" é relativo (`../index.html`).
- [ ] **Step 2: Run** — Expected: FAIL.
- [ ] **Step 3: Implement** templates seguindo o mockup aprovado (`.superpowers/brainstorm/18739-1792449237/content/docente-anderson.html` e `editorial-v3.html`: topo verde-escuro, números com `data-n` animados por `app.js` via `requestAnimationFrame`, cartões com hover `translateY(-4px)` e `--shadow-hover`, entrada escalonada). Páginas dos docentes organizam artigos por ano decrescente. Grade: 4 colunas desktop, 2 tablet, 1 celular. `app.js` pula animação com `prefers-reduced-motion`. Autoescape do Jinja ligado. Google Fonts: Fustat e Inter Tight.
- [ ] **Step 4: Run** — Expected: PASS.
- [ ] **Step 5: Commit** `feat: templates e estilo do site`.

### Task 5: CLI de build, GitHub Pages e conferência visual

**Files:**
- Create: `build.py`, `.github/workflows/pages.yml`, `README.md`, `.gitignore` (`site/`, `.cache/` exceto `impacto.json`, `.venv/`), `tests/test_build.py`

**Interfaces:**
- Consumes: tudo acima.
- Produces: `python build.py [--xlsx PATH] [--lattes DIR] [--sem-rede] [--saida site]`.

- [ ] **Step 1: Failing test:** `main(["--sem-rede", "--saida", str(tmp_path)])` com dados reais gera `index.html` e 17 arquivos em `docentes/`; `--sem-rede` usa só o cache e não faz requisição.
- [ ] **Step 2: Run** — Expected: FAIL.
- [ ] **Step 3: Implement** `build.py` ligando as tasks; por padrão busca impacto (com cache); imprime resumo (docentes, artigos, DOIs sem retorno). `pages.yml`: em push na `main`, `uv run python build.py`, publica `site/` com `actions/upload-pages-artifact` + `actions/deploy-pages`. Como as pastas de dados ficam fora do repo, o README explica commitar cópias em `dados/` e o `build.py` usa `dados/` por padrão quando existir. Guardar `.cache/impacto.json` no repo para o CI não depender de rede.
- [ ] **Step 4: Run** `uv run pytest -v` — Expected: tudo PASS.
- [ ] **Step 5: Build real e conferência visual:** `uv run python build.py`, servir `site/` com `python -m http.server`, abrir no navegador (index + 2 docentes + celular 390px) e conferir: números animam, selos aparecem, grade por linha (6 + 11), nenhum link quebrado, sem bloco vazio.
- [ ] **Step 6: Commit** `feat: build do site e deploy no GitHub Pages`.
- [ ] **Step 7: Publicar** (só com aprovação da usuária): criar repo `profes-PPGCASP`, push, ativar Pages (Source: GitHub Actions).
