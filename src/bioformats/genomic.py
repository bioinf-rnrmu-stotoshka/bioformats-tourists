# src/bioformats/genomic.py
from __future__ import annotations
from typing import Iterator, Dict, Any, Optional
from abc import ABC, abstractmethod
import pandas as pd

from .reader import Reader

class GenomicDataReader(Reader, ABC):
    """
    Абстрактный ридер геномных данных (SAM, VCF и т.п.).
    Наследники должны реализовать read() и get_header().
    Общие методы count(), get_chromosomes(), filter_by_region()
    работают полиморфно для всех потомков.
    """

    def __init__(
        self,
        filename: str,
        *,
        encoding: str = "utf-8",
        gz: Optional[bool] = None,
    ) -> None:
        super().__init__(filename, encoding=encoding, gz=gz)
        # буфер для хранения заголовка (если нужно)
        self._header: list[str] = []

    # ----- обязательные абстрактные методы -----
    @abstractmethod
    def read(self) -> Iterator[Dict[str, Any]]:
        """
        Ленивый генератор записей.
        Для SAM — словари с полями alignment.
        Для VCF — словари с variant information.
        """
        ...

    @abstractmethod
    def get_header(self) -> list[str]:
        """Вернуть строки заголовка (например, начинающиеся с @ или #)."""
        ...

    # ----- общий API (работает у всех наследников) -----
    def count(self) -> int:
        """Количество записей (без заголовков)."""
        return sum(1 for _ in self.read())

    def get_chromosomes(self) -> list[str]:
        """Список хромосом, найденных в данных (уникальные CHR)."""
        chroms = set()
        for rec in self.read():
            chrom = rec.get("chrom") or rec.get("CHR")
            if chrom:
                chroms.add(chrom)
        return sorted(chroms)

    def get_reference_genome(self) -> Optional[str]:
        """Вернуть ссылку на референсный геном, если найдено в хедере."""
        for line in self.get_header():
            if "ref=" in line or "reference=" in line:
                # пример: @SQ SN:chr1 LN:1000 ref=GRCh38
                for token in line.split():
                    if token.startswith(("ref=", "reference=")):
                        return token.split("=", 1)[1]
        return None

    def validate_coordinate(self, chrom: str, pos: int) -> bool:
        """Простейшая проверка, что позиция положительна и хромосома есть в наборе."""
        return isinstance(pos, int) and pos > 0 and chrom in self.get_chromosomes()

    def to_dataframe(self, limit: Optional[int] = None) -> pd.DataFrame:
        """Преобразовать прочитанные записи в DataFrame (для статистики)."""
        rows = []
        for i, rec in enumerate(self.read()):
            rows.append(rec)
            if limit and i >= limit:
                break
        return pd.DataFrame(rows)

    def filter_by_region(
        self, chrom: str, start: int, end: int
    ) -> Iterator[Dict[str, Any]]:
        """Фильтрация по координатам (работает для любого формата с полями chrom, pos)."""
        for rec in self.read():
            c = rec.get("chrom") or rec.get("CHR")
            p = rec.get("pos") or rec.get("POS")
            if c == chrom and isinstance(p, int) and start <= p <= end:
                yield rec