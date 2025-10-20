import pandas as pd
from bioformats.genomic import GenomicDataReader
from typing import Iterator, Dict, Any


class SamReader(GenomicDataReader):
    """Класс для чтения SAM файлов"""

    def read(self) -> Iterator[Dict[str, Any]]:
        """
        Генератор для чтения выравниваний из SAM файла
        """
        with open(self.filename, 'r') as file:
            for line in file:
                line = line.strip()
                # Пропускаем строки заголовка и пустые строки
                if not line or line.startswith('@'):
                    continue

                # Разбиваем строку на поля
                fields = line.split('\t')
                if len(fields) >= 11:
                    # Возвращаем поля выравнивания
                    yield {
                        'qname': fields[0],  # имя рида
                        'flag': int(fields[1]),  # флаги
                        'chrom': fields[2],  # имя референсной последовательности
                        'pos': int(fields[3]),  # позиция
                        'cigar': fields[5],  # CIGAR строка
                        'seq': fields[9]  # последовательность
                    }

    def get_header(self) -> list[str]:
        """Читает заголовок SAM файла"""
        header_lines = []

        try:
            with open(self.filename, 'r') as file:
                for line in file:
                    if not line.startswith('@'):
                        break
                    header_lines.append(line.strip())
        except FileNotFoundError:
            print(f"Файл {self.filename} не найден")

        return header_lines

    # Остальные методы УЖЕ ЕСТЬ в GenomicDataReader:
    # - count() - уже есть
    # - get_chromosomes() - уже есть
    # - filter_by_region() - уже есть (работает с полями 'chrom' и 'pos')
    # - to_dataframe() - уже есть

    # Дополнительные специфичные методы можно оставить:
    def get_alignment_statistics(self) -> pd.DataFrame:
        """Статистика по выравниваниям (специфичная для SAM)"""
        return self.to_dataframe().groupby('chrom').size().reset_index(name='count')

