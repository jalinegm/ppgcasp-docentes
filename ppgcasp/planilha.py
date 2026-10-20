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


def _byte(c: str) -> int | None:
    try:
        return c.encode("cp1252")[0]
    except UnicodeEncodeError:
        return ord(c) if ord(c) < 256 else None


def _extra(lider: int) -> int:
    return 1 if 0xC2 <= lider <= 0xDF else 2 if 0xE0 <= lider <= 0xEF else 3 if 0xF0 <= lider <= 0xF4 else 0


def _corrigir_uma_vez(texto: str) -> str:
    """Desfaz UTF-8 lido como cp1252/latin-1, sequência a sequência.

    Texto correto passa intacto; um espaço comum após a letra líder vale como U+00A0 (perdido na planilha).
    """
    saida, i = [], 0
    while i < len(texto):
        lider = _byte(texto[i])
        n = _extra(lider) if lider else 0
        trilha = [(_byte(c) if c != " " else 0xA0) for c in texto[i + 1 : i + 1 + n]] if n else []
        if n and len(trilha) == n and all(b is not None and 0x80 <= b <= 0xBF for b in trilha):
            try:
                saida.append(bytes([lider, *trilha]).decode("utf-8"))
                if texto[i + n] == " ":
                    saida.append(" ")  # o espaço comum era o nbsp (U+00A0) que a planilha perdeu; preserva o espaço
                i += 1 + n
                continue
            except UnicodeDecodeError:
                pass
        saida.append(texto[i])
        i += 1
    return "".join(saida)


def corrigir_texto(texto: str) -> str:
    """Aplica a correção até estabilizar (algumas células estão codificadas duas vezes)."""
    texto = re.sub(r"_x([0-9A-Fa-f]{4})_", lambda m: chr(int(m.group(1), 16)), texto)
    for _ in range(3):
        novo = _corrigir_uma_vez(texto)
        if novo == texto:
            break
        texto = novo
    return texto


def titulo_nome(nome: str) -> str:
    palavras = corrigir_texto(nome).split()
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
            docente.artigos.append(Artigo(int(ano), corrigir_texto(str(titulo)).strip(), normalizar_doi(doi)))
    return list(por_slug.values())
