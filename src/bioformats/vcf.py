# vcf.py
from __future__ import annotations
from typing import Iterator, Dict, Any

from .genomic import GenomicDataReader


class VcfReader(GenomicDataReader):
    """Класс для чтения VCF файлов."""

    def read(self) -> Iterator[Dict[str, Any]]:
        """
        Ленивое чтение вариантов из VCF файла.

        Возвращает словари с ключами:
          - chrom
          - pos
          - id
          - ref
          - alt
          - qual
          - filter
          - info
        """
        with self:
            for line in self.iter_lines(strip=True):
                # пропускаем заголовок
                if not line or line.startswith("#"):
                    continue

                fields = line.split("\t")
                if len(fields) < 8:
                    continue

                yield {
                    "chrom": fields[0],
                    "pos": int(fields[1]),
                    "id": fields[2],
                    "ref": fields[3],
                    "alt": fields[4],
                    "qual": float(fields[5]) if fields[5] != "." else None,
                    "filter": fields[6],
                    "info": fields[7],
                }

    def get_header(self) -> list[str]:
        """
        Вернуть строки заголовка VCF (все строки, начинающиеся с '#').
        """
        header_lines: list[str] = []
        with self:
            for line in self.iter_lines(strip=False):
                if not line.startswith("#"):
                    break
                header_lines.append(line.rstrip("\n"))
        return header_lines

    def header_by_group(self) -> dict[str, list[str]]:
        """
        Простейшая группировка заголовков по типам:

          - 'INFO'   : строки с '##INFO'
          - 'FILTER' : строки с '##FILTER'
          - 'FORMAT' : строки с '##FORMAT'
          - 'CONTIG' : строки с '##contig'
          - 'META'   : все прочие '##'
          - 'COLUMNS': строка '#CHROM ...'

        Это даёт "информацию по отдельным группам заголовков".
        """
        groups: dict[str, list[str]] = {}
        for line in self.get_header():
            if line.startswith("##INFO"):
                groups.setdefault("INFO", []).append(line)
            elif line.startswith("##FILTER"):
                groups.setdefault("FILTER", []).append(line)
            elif line.startswith("##FORMAT"):
                groups.setdefault("FORMAT", []).append(line)
            elif line.startswith("##contig"):
                groups.setdefault("CONTIG", []).append(line)
            elif line.startswith("##"):
                groups.setdefault("META", []).append(line)
            elif line.startswith("#CHROM"):
                groups.setdefault("COLUMNS", []).append(line)
        return groups
