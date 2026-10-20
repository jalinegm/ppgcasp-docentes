import requests

from ppgcasp.impacto import buscar_impacto_doi, carregar_cache, salvar_cache, somar_grupo, somar_impacto
from ppgcasp.models import Artigo, Docente, Impacto


class Resp:
    def __init__(self, status, corpo=None):
        self.status_code = status
        self._corpo = corpo or {}

    def json(self):
        return self._corpo


def get_falso(alt, dim, chamadas=None):
    def get(url, timeout=10):
        if chamadas is not None:
            chamadas.append(url)
        return alt if "altmetric" in url else dim
    return get


def test_altmetric_404_dimensions_200():
    get = get_falso(Resp(404), Resp(200, {"times_cited": 7}))
    r = buscar_impacto_doi("10.1/a", {}, get=get, pausa=0)
    assert r == {"citacoes": 7, "score": 0, "noticias": 0, "politicas": 0, "alt_ok": True, "dim_ok": True, "ok": True}


def test_altmetric_campos():
    alt = Resp(200, {"score": 12.5, "cited_by_msm_count": 3, "cited_by_policies_count": 1})
    r = buscar_impacto_doi("10.1/a", {}, get=get_falso(alt, Resp(404)), pausa=0)
    assert (r["score"], r["noticias"], r["politicas"], r["citacoes"]) == (12.5, 3, 1, 0)


def test_falha_nao_grava_cache():
    cache = {}
    r = buscar_impacto_doi("10.1/a", cache, get=get_falso(Resp(500), Resp(500)), pausa=0)
    assert r["ok"] is False and cache == {}


def test_timeout_nao_quebra():
    def get(url, timeout=10):
        raise requests.Timeout()
    r = buscar_impacto_doi("10.1/a", {}, get=get, pausa=0)
    assert r["ok"] is False


def test_cache_evita_chamada():
    chamadas = []
    get = get_falso(Resp(404), Resp(200, {"times_cited": 2}), chamadas)
    cache = {}
    buscar_impacto_doi("10.1/a", cache, get=get, pausa=0)
    n = len(chamadas)
    buscar_impacto_doi("10.1/a", cache, get=get, pausa=0)
    assert len(chamadas) == n


def test_somar_impacto():
    d = Docente("X", "x", 1, [Artigo(2024, "a", "10.1/a"), Artigo(2024, "b", "10.1/b"), Artigo(2024, "c", None)])
    get = get_falso(Resp(200, {"score": 2, "cited_by_msm_count": 1}), Resp(200, {"times_cited": 5}))
    imp = somar_impacto(d, {}, get=get, pausa=0)
    assert imp == Impacto(10, 4.0, 2, 0, True)


def test_somar_impacto_sem_doi():
    d = Docente("X", "x", 1, [Artigo(2024, "c", None)])
    assert somar_impacto(d, {}, get=None, pausa=0) == Impacto(0, 0.0, 0, 0, False)


def test_somar_grupo_conta_artigo_coautorado_uma_vez():
    comum1 = Artigo(2024, "Comum", "10.1/c", score=4.0, citacoes=2, noticias=1)
    comum2 = Artigo(2024, "Comum", "10.1/c", score=4.0, citacoes=2, noticias=1)
    so_b = Artigo(2024, "Só B", None, score=0.0, citacoes=0)
    a = Docente("A", "a", 1, [comum1], impacto=Impacto(2, 4.0, 1, 0, True))
    b = Docente("B", "b", 1, [comum2, so_b], impacto=Impacto(2, 4.0, 1, 0, True))
    c = Docente("C", "c", 1, impacto=None)
    assert somar_grupo([a, b, c]) == Impacto(2, 4.0, 1, 0, True)


def test_cache_roundtrip(tmp_path):
    p = tmp_path / "c.json"
    assert carregar_cache(p) == {}
    salvar_cache(p, {"10.1/a": {"ok": True}})
    assert carregar_cache(p) == {"10.1/a": {"ok": True}}


def test_somar_impacto_guarda_por_artigo():
    a = Artigo(2024, "a", "10.1/a")
    d = Docente("X", "x", 1, [a])
    get = get_falso(Resp(200, {"score": 9}), Resp(200, {"times_cited": 4}))
    somar_impacto(d, {}, get=get, pausa=0)
    assert (a.score, a.citacoes) == (9.0, 4)


def test_altmetric_usa_chave_do_ambiente(monkeypatch):
    monkeypatch.setenv("ALTMETRIC_API_KEY", "abc123")
    chamadas = []
    buscar_impacto_doi("10.1/a", {}, get=get_falso(Resp(404), Resp(404), chamadas), pausa=0)
    assert any("altmetric" in u and "key=abc123" in u for u in chamadas)


def test_resultado_parcial_vai_para_cache_e_reconsulta_com_chave(monkeypatch):
    monkeypatch.delenv("ALTMETRIC_API_KEY", raising=False)
    cache = {}
    chamadas = []
    get = get_falso(Resp(403), Resp(200, {"times_cited": 6}), chamadas)
    r = buscar_impacto_doi("10.1/a", cache, get=get, pausa=0)
    assert r["citacoes"] == 6 and "10.1/a" in cache
    n = len(chamadas)
    buscar_impacto_doi("10.1/a", cache, get=get, pausa=0)
    assert len(chamadas) == n  # sem chave: não insiste no Altmetric
    monkeypatch.setenv("ALTMETRIC_API_KEY", "k")
    buscar_impacto_doi("10.1/a", cache, get=get, pausa=0)
    assert len(chamadas) > n  # com chave: reconsulta o Altmetric
