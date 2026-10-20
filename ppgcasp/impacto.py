import json
import os
import time
from pathlib import Path

import requests

from .models import Docente, Impacto

ALTMETRIC = "https://api.altmetric.com/v1/doi/{doi}"
DIMENSIONS = "https://metrics-api.dimensions.ai/doi/{doi}"


def carregar_cache(caminho: Path) -> dict:
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def salvar_cache(caminho: Path, cache: dict) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")


def _consultar(get, url: str, tentativas: int = 2):
    """Retorna (status, json) ou (None, {}) se a rede falhar."""
    for _ in range(tentativas):
        try:
            r = get(url, timeout=10)
            if r.status_code in (200, 404):
                return r.status_code, (r.json() if r.status_code == 200 else {})
        except (requests.RequestException, ValueError):
            pass
    return None, {}


def buscar_impacto_doi(doi: str, cache: dict, get=requests.get, pausa: float = 1.0) -> dict:
    if doi in cache:
        return cache[doi]
    url_alt = ALTMETRIC.format(doi=doi)
    if os.environ.get("ALTMETRIC_API_KEY"):
        url_alt += f"?key={os.environ['ALTMETRIC_API_KEY']}"
    st_alt, alt = _consultar(get, url_alt)
    st_dim, dim = _consultar(get, DIMENSIONS.format(doi=doi))
    resultado = {
        "citacoes": int(dim.get("times_cited") or 0),
        "score": float(alt.get("score") or 0) if st_alt == 200 else 0,
        "noticias": int(alt.get("cited_by_msm_count") or 0),
        "politicas": int(alt.get("cited_by_policies_count") or 0),
        "ok": st_alt is not None and st_dim is not None,
    }
    if resultado["ok"]:
        cache[doi] = resultado
    time.sleep(pausa)
    return resultado


def somar_impacto(docente: Docente, cache: dict, get=requests.get, pausa: float = 1.0) -> Impacto:
    resultados = []
    for artigo in docente.artigos:
        if not artigo.doi:
            continue
        r = buscar_impacto_doi(artigo.doi, cache, get=get, pausa=pausa)
        artigo.score, artigo.citacoes = float(r["score"]), r["citacoes"]
        resultados.append(r)
    return Impacto(
        citacoes=sum(r["citacoes"] for r in resultados),
        altmetric_score=float(sum(r["score"] for r in resultados)),
        noticias=sum(r["noticias"] for r in resultados),
        politicas=sum(r["politicas"] for r in resultados),
        disponivel=any(r["ok"] for r in resultados),
    )


def somar_grupo(docentes: list[Docente]) -> Impacto:
    impactos = [d.impacto for d in docentes if d.impacto]
    return Impacto(
        citacoes=sum(i.citacoes for i in impactos),
        altmetric_score=float(sum(i.altmetric_score for i in impactos)),
        noticias=sum(i.noticias for i in impactos),
        politicas=sum(i.politicas for i in impactos),
        disponivel=any(i.disponivel for i in impactos),
    )
