# sam.py
from __future__ import annotations
from typing import Iterator, Dict, Any

from .genomic import GenomicDataReader


class SamReader(GenomicDataReader):
    """Класс для чтения SAM файлов."""

    def read(self) -> Iterator[Dict[str, Any]]:
        """
        Ленивое чтение выравниваний из SAM файла.

        Возвращает словари с ключами:
          - qname: имя рида
          - flag:  флаг
          - chrom: референсная последовательность
          - pos:   позиция (1-based)
          - cigar: CIGAR-строка
          - seq:   нуклеотидная последовательность
        """
        with self:
            for line in self.iter_lines(strip=True):
                # пропускаем заголовки и пустые строки
                if not line or line.startswith("@"):
                    continue

                fields = line.split("\t")
                if len(fields) < 11:
                    continue

                yield {
                    "qname": fields[0],
                    "flag": int(fields[1]),
                    "chrom": fields[2],
                    "pos": int(fields[3]),
                    "cigar": fields[5],
                    "seq": fields[9],
                }

    def get_header(self) -> list[str]:
        """
        Вернуть строки заголовка SAM файла (начинаются с '@').
        """
        header_lines: list[str] = []
        with self:
            for line in self.iter_lines(strip=False):
                if not line.startswith("@"):
                    break
                header_lines.append(line.rstrip("\n"))
        return header_lines

    def header_by_group(self) -> dict[str, list[str]]:
        """
        Группировка строк заголовка по типу (@HD, @SQ, @RG, @PG и т.п.).

        Возвращает словарь:
            {"HD": [...], "SQ": [...], "RG": [...], "PG": [...], ...}
        """
        groups: dict[str, list[str]] = {}
        for line in self.get_header():
            if line.startswith("@") and len(line) >= 3:
                tag = line[1:3]
                groups.setdefault(tag, []).append(line)
        return groups
