from pathlib import Path

import pytest

from ppgcasp.planilha import carregar_docentes, corrigir_texto, normalizar_doi, slugify, titulo_nome

XLSX = Path(__file__).parent.parent / "dados" / "planilha.xlsx"


def test_normalizar_doi_url():
    assert normalizar_doi("https://doi.org/10.1/ABC") == "10.1/abc"


def test_normalizar_doi_none():
    assert normalizar_doi(None) is None


def test_normalizar_doi_prefixo_doi():
    assert normalizar_doi("doi:10.1/x") == "10.1/x"


def test_normalizar_doi_puro_com_espaco():
    assert normalizar_doi(" 10.1/X ") == "10.1/x"


def test_titulo_nome_mojibake():
    assert titulo_nome("Cleudson JosÃ© Michelon") == "Cleudson José Michelon"


def test_titulo_nome_maiusculas():
    assert titulo_nome("LESSANDRO DE CONTI") == "Lessandro de Conti"


def test_slugify_acento():
    assert slugify("Éverton Lutz") == "everton-lutz"


@pytest.fixture(scope="module")
def docentes():
    return carregar_docentes(XLSX)


def test_total_docentes(docentes):
    assert len(docentes) == 17


def test_exclui_gressler(docentes):
    assert not any("gressler" in d.nome.lower() for d in docentes)


def test_periodo_2021_2025(docentes):
    anos = [a.ano for d in docentes for a in d.artigos]
    assert min(anos) >= 2021 and max(anos) <= 2025
    assert len(anos) == 131


def test_total_com_doi(docentes):
    assert sum(1 for d in docentes for a in d.artigos if a.doi) == 123


def test_anderson_15_artigos(docentes):
    d = next(d for d in docentes if d.slug == "anderson-saldanha-bueno")
    assert len(d.artigos) == 15


def test_linhas(docentes):
    por = {d.slug: d.linha for d in docentes}
    assert por["luana-mendes-dos-santos"] == 2
    assert por["jonas-sponchiado"] == 1


def test_corrigir_texto_cp1252_e_escape():
    assert corrigir_texto("PARÃ‚METROS HÃ_x008d_BRIDOS") == "PARÂMETROS HÍBRIDOS"
    assert corrigir_texto("Educação Ambiental") == "Educação Ambiental"
    assert corrigir_texto("cultivo mÃ­nimo") == "cultivo mínimo"


def test_corrigir_texto_sequencias_mistas_e_maiusculas_legitimas():
    assert corrigir_texto("submetida Ã inoculaÃ§Ã£o") == "submetida à inoculação"
    assert corrigir_texto("REGIÃO NOROESTE GRÃOS") == "REGIÃO NOROESTE GRÃOS"
    assert corrigir_texto("SÃ£o JoÃ£o") == "São João"


def test_titulos_reais_sem_mojibake(docentes):
    import re

    ruins = [
        a.titulo
        for d in docentes
        for a in d.artigos
        if "_x00" in a.titulo or re.search(r"[ÃÂ][-¿Œ-™ ]", a.titulo)
    ]
    assert ruins == []
