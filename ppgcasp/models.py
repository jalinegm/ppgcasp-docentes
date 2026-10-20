from dataclasses import dataclass, field


@dataclass
class Artigo:
    ano: int
    titulo: str
    doi: str | None


@dataclass
class LattesInfo:
    resumo: str
    campus: str
    contagens: dict[str, int]


@dataclass
class Impacto:
    citacoes: int
    altmetric_score: float
    noticias: int
    politicas: int
    disponivel: bool


@dataclass
class Docente:
    nome: str
    slug: str
    linha: int
    artigos: list[Artigo] = field(default_factory=list)
    lattes: LattesInfo | None = None
    impacto: Impacto | None = None
