"""
Наследуется от SequenceReader.
"""

from typing import Iterator, Tuple
from .sequences import SequenceReader, SequencePair

class FastaReader(SequenceReader):
    """Класс для работы с FASTA файлами."""
    
    def read(self) -> Iterator[SequencePair]:
        """Ленивое чтение FASTA файла с возвратом (seq_id, sequence)."""
        with self:
            current_header = None
            current_seq_parts = []
            
            for line in self.iter_lines(strip=True):
                if not line:
                    continue
                    
                if line.startswith('>'):
                    # Сохраняем предыдущую последовательность
                    if current_header is not None:
                        sequence = ''.join(current_seq_parts)
                        if self.validate_sequence(sequence):
                            yield current_header, sequence
                    
                    # Начинаем новую последовательность
                    current_header = line[1:].split()[0]  # Берем только первый токен до пробела
                    current_seq_parts = []
                else:
                    current_seq_parts.append(line)
            
            # Не забываем последнюю последовательность
            if current_header is not None and current_seq_parts:
                sequence = ''.join(current_seq_parts)
                if self.validate_sequence(sequence):
                    yield current_header, sequence
    
    def read_sequences(self) -> Iterator[Tuple[str, str]]:
        """Альтернативное имя для обратной совместимости."""
        return self.read()
    
    def _read_sequences(self) -> Iterator[Tuple[str, str]]:
        """Старый метод для обратной совместимости."""
        return self.read()
    
    def get_sequence_by_index(self, index: int) -> Tuple[str, str]:
        """Получить последовательность по индексу (начиная с 0)."""
        for i, (header, seq) in enumerate(self.read()):
            if i == index:
                return header, seq
        raise IndexError(f"Sequence index {index} out of range")
    
    def filter_sequences(self, min_length: int = 0, max_length: int = None) -> Iterator[SequencePair]:
        """Фильтрация последовательностей по длине."""
        for header, seq in self.read():
            seq_len = len(seq)
            if seq_len >= min_length and (max_length is None or seq_len <= max_length):
                yield header, seq
    
    def to_dict(self) -> dict:
        """Преобразовать все последовательности в словарь (осторожно с большими файлами!)."""
        return dict(self.read())