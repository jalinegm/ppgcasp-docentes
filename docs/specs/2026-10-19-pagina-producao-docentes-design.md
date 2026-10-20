# Página de produção e impacto do corpo docente — Design

Data: 2026-10-19
Proposta: APCN Mestrado Profissional em Ciências Ambientais e Sistemas Produtivos (IFFar, Área 49)

## Intenção

Site público que apresenta o grupo de docentes da proposta e a produção de cada um, com ênfase no **impacto social** da pesquisa. Público duplo: avaliador CAPES e comunidade. O avaliador deve sair com a impressão de um grupo coeso, produtivo e com repercussão fora da academia.

Referência funcional: página de publicações do Prof. Anderson Bueno (`buenoas.github.io/publications.qmd`), que mostra, para cada artigo, o donut Altmetric e o selo de citações Dimensions a partir do DOI.

## Objetivos

- Página geral com panorama do grupo e grade de docentes.
- Uma página por docente com produções e impacto.
- Badges Altmetric + Dimensions em cada artigo com DOI.
- Deploy em GitHub Pages.

## Não objetivos

- Não é sistema editável online; dados vêm de planilha e Lattes, regenerados por script.
- Não calcula pontuação CAPES (isso fica na planilha).
- Sem login, sem backend.

## Anti-objetivos (falha mesmo que funcione)

- Aparência de "site feito por IA": gradientes genéricos, emojis, cards todos iguais, frases de marketing vazias.
- Mostrar números vazios ou "—" como se fossem dados. Bloco sem dado some.
- Perder artigos: artigo sem DOI ou não encontrado nas APIs **continua na lista**.

## Dados (decidido)

- **Fonte primária de artigos:** `Planilha_de_Pontuacao_e_Prontidao_APCN_Ciencias_Ambientais.xlsx`, aba `Lançamentos - Artigos` (colunas Docente, Linha, Ano, Título, DOI).
- **Período:** 2021–2025. Artigos de 2026 ficam fora.
- **Fonte complementar:** Lattes em `Lattes/Lattes/` (XML ou ZIP contendo XML). Usado para: resumo, campus, e contagem de "Além dos artigos": trabalhos técnicos, eventos organizados, cursos ministrados, materiais didáticos, programas de rádio/TV e entrevistas na mídia, orientações de pós-graduação concluídas. No Lattes, só entram os itens de 2021–2025.
- **Docentes:** os 17 da aba de artigos. **Excluídos:** Letícia Trevisan Gressler e Julian (não entram na proposta).
- Linhas: 1 = Biodiversidade, Saúde Ambiental e Conservação; 2 = Inovação, Biotecnologia e Sustentabilidade Produtiva. Cleudson, Éverton, Lessandro, Luana e Tatiana (sem linha na planilha) vão para a **linha 2** (decisão da usuária). Resultado: linha 1 com 6 docentes, linha 2 com 11.
- Docentes sem Lattes na pasta (Rangel, Cleudson): página só com artigos da planilha, sem bloco "Além dos artigos".
- O nome `Cleudson JosÃ© Michelon` está com encoding quebrado na planilha. Corrigir para `Cleudson José Michelon` no script. Normalizar caixa dos nomes (planilha mistura MAIÚSCULAS e normal).

## Página geral (decidido)

Estrutura "Editorial", de cima para baixo:

1. **Topo verde-escuro.** Sobretítulo "Mestrado Profissional · Instituto Federal Farroupilha". Título grande: **Ciências Ambientais e Sistemas Produtivos**. Sem texto abaixo do título (decisão da usuária).
2. **Números animados (sobem ao carregar):** docentes, artigos 2021–2025, com DOI, campi.
3. **Impacto social (condicional):** aparece só se a soma de atenção Altmetric do grupo > 0. Mostra total de menções e destaca os artigos com maior atenção (notícias, políticas públicas, quando houver). Sem dados, a seção não é renderizada.
4. **Grade de docentes por linha de pesquisa:** cartão com foto (vazia por enquanto, mostra iniciais), nome, nº artigos e nº com DOI. Clique abre a página do docente.

## Página do docente (decidido, aprovada no mockup)

1. Topo verde-escuro: "← Corpo docente", foto (iniciais por enquanto), linha · campus, nome, resumo de 1 frase.
2. Números: artigos 2021–2025, com DOI, soma de citações Dimensions, soma de atenção Altmetric. Número zero ou indisponível: o bloco some.
3. "Além dos artigos": cartões com contagens do Lattes. Contagem zero não aparece.
4. Artigos agrupados por ano (mais recente primeiro). Cada item: donut Altmetric (`data-badge-type="donut"`, popover) + selo Dimensions (`small_circle`), título, link DOI. Sem DOI: etiqueta "sem DOI", item continua.

## Visual (decidido)

- Tokens do `design.md` (paleta, Fustat + Inter Tight, raios 16/24/999px, sombras discretas). **Sem logo nem nome AbacatePay.**
- Motion só em destaques: contagem dos números, entrada suave escalonada, leve elevação em hover. Respeitar `prefers-reduced-motion`.
- Responsivo: uma coluna no celular.

## Stack (escolha do Claude)

- Site estático: HTML + CSS + JS puro, sem framework.
- Script Python `build.py` lê planilha + Lattes, consulta APIs e gera `site/index.html`, `site/docentes/<slug>.html` e `site/data.json`.
- Somas de impacto calculadas na geração via APIs públicas: Altmetric `api.altmetric.com/v1/doi/<doi>` e Dimensions `metrics-api.dimensions.ai/doi/<doi>`. Respostas guardadas em cache JSON local para não refazer as chamadas. DOI não encontrado (HTTP 404) conta como zero, e o artigo continua listado.
- Badges no navegador continuam ao vivo pelos scripts oficiais (`embed.js` Altmetric, `badge.js` Dimensions).
- Deploy: repositório GitHub com a pasta `site/` publicada via GitHub Pages (Actions ou branch `gh-pages`).
- Fotos: pasta `site/fotos/<slug>.jpg`. Se existir, substitui as iniciais automaticamente.

## Em aberto (para a usuária)

- Nenhum. Repositório GitHub: `profes-PPGCASP` (decisão da usuária). Site servido em subcaminho `/profes-PPGCASP/`, então todos os links internos devem ser relativos.

## Fica para o construtor

- Slugs, nomes de arquivo, estrutura de CSS.
- Mapeamento exato das tags do XML Lattes para as categorias "Além dos artigos".
- Extração do campus a partir do Lattes (endereço profissional), com fallback vazio.
