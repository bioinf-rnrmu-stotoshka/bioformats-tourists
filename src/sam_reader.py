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