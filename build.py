"""Gera o site estático em site/ a partir da planilha e dos Lattes."""
import argparse
from pathlib import Path

import requests

from ppgcasp.impacto import carregar_cache, salvar_cache, somar_grupo, somar_impacto
from ppgcasp.lattes import carregar_lattes
from ppgcasp.models import chave_artigo
from ppgcasp.planilha import carregar_docentes
from ppgcasp.render import renderizar_site

RAIZ = Path(__file__).parent


def _sem_rede(url, timeout=10):
    raise requests.ConnectionError("sem --buscar")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", type=Path, default=RAIZ / "dados" / "planilha.xlsx")
    ap.add_argument("--lattes", type=Path, default=RAIZ / "dados" / "lattes")
    ap.add_argument("--fotos", type=Path, default=RAIZ / "fotos")
    ap.add_argument("--cache", type=Path, default=RAIZ / ".cache" / "impacto.json")
    ap.add_argument("--saida", type=Path, default=RAIZ / "site")
    ap.add_argument("--buscar", action="store_true",
                    help="consulta Altmetric/Dimensions e atualiza o cache (exige chave/autorização das APIs)")
    args = ap.parse_args(argv)

    docentes = carregar_docentes(args.xlsx)
    lattes = carregar_lattes(args.lattes)
    cache = carregar_cache(args.cache)
    get, pausa = (requests.get, 1.0) if args.buscar else (_sem_rede, 0)

    for d in docentes:
        d.lattes = lattes.get(d.slug)
        d.impacto = somar_impacto(d, cache, get=get, pausa=pausa)
        if args.buscar:
            salvar_cache(args.cache, cache)
    grupo = somar_grupo(docentes)

    renderizar_site(docentes, grupo, args.saida, fotos=args.fotos)

    artigos = list({chave_artigo(a): a for d in docentes for a in d.artigos}.values())
    sem_retorno = sum(1 for a in artigos if a.doi and a.doi not in cache)
    print(f"{len(docentes)} docentes · {len(artigos)} artigos · "
          f"{sum(1 for a in artigos if a.doi)} com DOI · {sem_retorno} DOI sem dados de impacto")
    print(f"Lattes encontrado para {sum(1 for d in docentes if d.lattes)} de {len(docentes)} docentes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
