from pathlib import Path

import pytest

from ppgcasp.planilha import carregar_docentes, normalizar_doi, slugify, titulo_nome

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
