import shutil
from itertools import groupby
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .lattes import CATEGORIAS
from .models import Docente, Impacto

BASE = Path(__file__).parent
STATIC = BASE.parent / "static"
LINHAS = {
    1: "Biodiversidade, Saúde Ambiental e Conservação",
    2: "Inovação, Biotecnologia e Sustentabilidade Produtiva",
}


def _iniciais(nome: str) -> str:
    partes = nome.split()
    return (partes[0][0] + partes[-1][0]).upper() if len(partes) > 1 else nome[:2].upper()


def _plural(n: int, singular: str, plural: str) -> str:
    return f"{n} {singular if n == 1 else plural}"


def _por_ano(artigos):
    ordenados = sorted(artigos, key=lambda a: -a.ano)
    return [(ano, list(g)) for ano, g in groupby(ordenados, key=lambda a: a.ano)]


def _env() -> Environment:
    env = Environment(loader=FileSystemLoader(BASE / "templates"), autoescape=select_autoescape(["html"]))
    env.filters["plural"] = _plural
    return env


def renderizar_site(docentes: list[Docente], grupo: Impacto, saida: Path, fotos: Path | None = None) -> None:
    env = _env()
    saida.mkdir(parents=True, exist_ok=True)
    (saida / "docentes").mkdir(exist_ok=True)
    shutil.copytree(STATIC, saida / "static", dirs_exist_ok=True)

    tem_foto = {d.slug: bool(fotos and (fotos / f"{d.slug}.jpg").exists()) for d in docentes}
    if fotos and fotos.exists():
        shutil.copytree(fotos, saida / "fotos", dirs_exist_ok=True)

    por_linha = [
        (LINHAS[n], sorted((d for d in docentes if d.linha == n), key=lambda d: d.nome))
        for n in sorted(LINHAS)
    ]
    todos_artigos = [(d, a) for d in docentes for a in d.artigos]
    destaques = sorted((p for p in todos_artigos if p[1].score > 0), key=lambda p: -p[1].score)[:3]
    kpis = {
        "docentes": len(docentes),
        "artigos": len(todos_artigos),
        "doi": sum(1 for _, a in todos_artigos if a.doi),
        "linhas": len(LINHAS),
    }
    (saida / "index.html").write_text(
        env.get_template("index.html").render(
            raiz="", por_linha=por_linha, grupo=grupo, destaques=destaques, kpis=kpis,
            tem_foto=tem_foto, iniciais=_iniciais,
        ),
        encoding="utf-8",
    )

    tpl = env.get_template("docente.html")
    for d in docentes:
        cartoes = [
            (d.lattes.contagens.get(chave, 0), rotulo)
            for chave, rotulo in CATEGORIAS
            if d.lattes and d.lattes.contagens.get(chave, 0) > 0
        ]
        (saida / "docentes" / f"{d.slug}.html").write_text(
            tpl.render(
                raiz="../", d=d, linha=LINHAS[d.linha], anos=_por_ano(d.artigos), cartoes=cartoes,
                com_doi=sum(1 for a in d.artigos if a.doi), foto=tem_foto[d.slug], iniciais=_iniciais(d.nome),
            ),
            encoding="utf-8",
        )
