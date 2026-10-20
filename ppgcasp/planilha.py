import re
import unicodedata
from pathlib import Path

import openpyxl

from .models import Artigo, Docente

ABA_ARTIGOS = "Lançamentos - Artigos"
ANO_MIN, ANO_MAX = 2021, 2025
EXCLUIDOS = {"leticia-trevisan-gressler", "julian"}
MINUSCULAS = {"de", "da", "do", "das", "dos", "e"}


def normalizar_doi(raw: str | None) -> str | None:
    if not raw:
        return None
    doi = str(raw).strip().lower()
    doi = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", doi)
    return doi.strip() or None


def _corrigir_mojibake(texto: str) -> str:
    try:
        return texto.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return texto


def titulo_nome(nome: str) -> str:
    palavras = _corrigir_mojibake(nome).split()
    saida = []
    for i, p in enumerate(palavras):
        baixa = p.lower()
        saida.append(baixa if i > 0 and baixa in MINUSCULAS else baixa.capitalize())
    return " ".join(saida)


def slugify(nome: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", sem_acento.lower()).strip("-")


def _linha(texto: str | None) -> int:
    return 1 if texto and "biodiversidade" in texto.lower() else 2


def carregar_docentes(caminho_xlsx: Path) -> list[Docente]:
    wb = openpyxl.load_workbook(caminho_xlsx, read_only=True, data_only=True)
    por_slug: dict[str, Docente] = {}
    for linha in list(wb[ABA_ARTIGOS].iter_rows(values_only=True))[1:]:
        nome_bruto, linha_pesq, ano, titulo, doi = linha[:5]
        if not nome_bruto or not ano:
            continue
        nome = titulo_nome(str(nome_bruto))
        slug = slugify(nome)
        if slug in EXCLUIDOS:
            continue
        docente = por_slug.setdefault(slug, Docente(nome, slug, 2))
        if linha_pesq:
            docente.linha = _linha(str(linha_pesq))
        if ANO_MIN <= int(ano) <= ANO_MAX:
            docente.artigos.append(Artigo(int(ano), str(titulo).strip(), normalizar_doi(doi)))
    return list(por_slug.values())
