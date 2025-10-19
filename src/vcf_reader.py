import pandas as pd


class VcfReader:
    """Класс для чтения VCF файлов"""

    def __init__(self, filename: str):
        self.filename = filename

    def get_header(self) -> dict:
        """Читает заголовок VCF файла"""
        header = {
            'meta': [],  # Строки с ##
            'columns': []  # Строка с #CHROM
        }

        try:
            with open(self.filename, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line.startswith('##'):
                        header['meta'].append(line)
                    elif line.startswith('#CHROM'):
                        header['columns'] = line.lstrip('#').split('\t')
                        break
        except FileNotFoundError:
            print(f"Файл {self.filename} не найден")

        return header

    def read_variants(self):
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

    def get_variant_count(self) -> int:
        """Возвращает общее количество вариантов"""
        count = 0
        for _ in self.read_variants():
            count += 1
        return count

    def get_variant_statistics(self) -> pd.DataFrame:
        """
        Возвращает статистику по вариантам в виде DataFrame
        """
        region_counts = {}

        # ОТКРЫВАЕМ ФАЙЛ ЗАНОВО для статистики
        with open(self.filename, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                fields = line.split('\t')
                if len(fields) >= 8:
                    chrom = fields[0]
                    region_counts[chrom] = region_counts.get(chrom, 0) + 1

        # Создаем DataFrame
        df = pd.DataFrame(list(region_counts.items()), columns=['region', 'count'])
        return df

    def get_variants_in_region(self, chrom: str, start: int, end: int) -> list:
        """
        Возвращает варианты в заданном геномном регионе
        """
        result = []

        with open(self.filename, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                fields = line.split('\t')
                if len(fields) >= 8:
                    pos = int(fields[1])
                    if (fields[0] == chrom and
                            pos >= start and
                            pos <= end):
                        result.append({
                            'chrom': fields[0],
                            'pos': pos,
                            'id': fields[2],
                            'ref': fields[3],
                            'alt': fields[4],
                            'qual': float(fields[5]) if fields[5] != '.' else None,
                            'filter': fields[6],
                            'info': fields[7]
                        })

        return result
