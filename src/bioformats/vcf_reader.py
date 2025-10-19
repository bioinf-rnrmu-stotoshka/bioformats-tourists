import pandas as pd
from bioformats.genomic import GenomicDataReader
from typing import Iterator, Dict, Any


class VcfReader(GenomicDataReader):
    """Класс для чтения VCF файлов"""

    def read(self) -> Iterator[Dict[str, Any]]:
        """
        Генератор для чтения вариантов из VCF файла
        """
        with open(self.filename, 'r') as file:
            for line in file:
                line = line.strip()
                # Пропускаем строки заголовка
                if not line or line.startswith('#'):
                    continue

                fields = line.split('\t')
                if len(fields) >= 8:
                    yield {
                        'chrom': fields[0],
                        'pos': int(fields[1]),
                        'id': fields[2],
                        'ref': fields[3],
                        'alt': fields[4],
                        'qual': float(fields[5]) if fields[5] != '.' else None,
                        'filter': fields[6],
                        'info': fields[7]
                    }

    def get_header(self) -> list[str]:
        """Читает заголовок VCF файла"""
        header_lines = []

        try:
            with open(self.filename, 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line.startswith('#'):
                        break
                    header_lines.append(line)
        except FileNotFoundError:
            print(f"Файл {self.filename} не найден")

        return header_lines

    # Остальные методы УЖЕ ЕСТЬ в GenomicDataReader

    def get_variant_statistics(self) -> pd.DataFrame:
        """Статистика по вариантам (специфичная для VCF)"""
        return self.to_dataframe().groupby('chrom').size().reset_index(name='count')
