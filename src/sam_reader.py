import pandas as pd


class SamReader:
    """Класс для чтения SAM файлов"""

    def __init__(self, filename: str):
        self.filename = filename

    def get_header(self) -> dict:
        """Читает заголовок SAM файла"""
        header = {'HD': [], 'SQ': [], 'RG': [], 'PG': [], 'CO': []}

        try:
            with open(self.filename, 'r') as file:
                for line in file:
                    if not line.startswith('@'):
                        break  # Заголовок закончился

                    # Парсим строку заголовка
                    if line.startswith('@HD'):
                        parts = line.strip().split('\t')
                        hd_info = {}
                        for part in parts[1:]:
                            if ':' in part:
                                key, value = part.split(':', 1)
                                hd_info[key] = value
                        header['HD'].append(hd_info)

                    elif line.startswith('@SQ'):
                        parts = line.strip().split('\t')
                        sq_info = {}
                        for part in parts[1:]:
                            if ':' in part:
                                key, value = part.split(':', 1)
                                sq_info[key] = value
                        header['SQ'].append(sq_info)

        except FileNotFoundError:
            print(f"Файл {self.filename} не найден")

        return header

    def read_alignments(self):
        """
        Генератор для чтения выравниваний из SAM файла
        Возвращает по одному выравниванию за раз
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
                        'rname': fields[2],  # имя референсной последовательности
                        'pos': int(fields[3]),  # позиция
                        'cigar': fields[5],  # CIGAR строка
                        'seq': fields[9]  # последовательность
                    }

    def get_alignment_count(self) -> int:
        """Возвращает общее количество выравниваний"""
        count = 0
        for _ in self.read_alignments():
            count += 1
        return count

    def get_alignment_statistics(self) -> pd.DataFrame:
        """
        Возвращает статистику по выравниваниям в виде DataFrame
        """
        chrom_counts = {}

        for alignment in self.read_alignments():
            chrom = alignment['rname']
            chrom_counts[chrom] = chrom_counts.get(chrom, 0) + 1

        # Создаем DataFrame
        df = pd.DataFrame(list(chrom_counts.items()), columns=['chromosome', 'count'])
        return df

    def get_alignments_in_region(self, chrom: str, start: int, end: int) -> list:
        """
        Возвращает выравнивания в заданном геномном регионе

        Args:
            chrom: имя хромосомы (например, 'chr1')
            start: начало региона (1-based)
            end: конец региона (1-based)
        """
        result = []

        with open(self.filename, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('@'):
                    continue

                fields = line.split('\t')
                if len(fields) >= 11:
                    pos = int(fields[3])
                    # Проверяем регион
                    if (fields[2] == chrom and
                            pos >= start and
                            pos <= end):
                        result.append({
                            'qname': fields[0],
                            'flag': int(fields[1]),
                            'rname': fields[2],
                            'pos': pos,
                            'cigar': fields[5],
                            'seq': fields[9]
                        })

        return result

