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
    assert r == {"citacoes": 7, "score": 0, "noticias": 0, "politicas": 0, "ok": True}


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


def test_somar_grupo():
    a = Docente("A", "a", 1, impacto=Impacto(1, 2.0, 1, 0, True))
    b = Docente("B", "b", 1, impacto=Impacto(2, 3.0, 0, 1, True))
    c = Docente("C", "c", 1, impacto=None)
    assert somar_grupo([a, b, c]) == Impacto(3, 5.0, 1, 1, True)


def test_cache_roundtrip(tmp_path):
    p = tmp_path / "c.json"
    assert carregar_cache(p) == {}
    salvar_cache(p, {"10.1/a": {"ok": True}})
    assert carregar_cache(p) == {"10.1/a": {"ok": True}}
