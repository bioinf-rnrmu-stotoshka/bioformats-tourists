"""
Наследуется от SequenceReader.
"""

from typing import Iterator, Tuple, List
from .sequences import SequenceReader, SequencePair

class Fastq(SequenceReader):
    """Класс для работы с FASTQ файлами."""
    
    def __init__(self, filename: str, **kwargs):
        super().__init__(filename, **kwargs)
        self._quality_scores_cache = None
    
    def read(self) -> Iterator[SequencePair]:
        """Ленивое чтение FASTQ файла с возвратом (seq_id, sequence)."""
        with self:
            lines_buffer = []
            
            for line in self.iter_lines(strip=True):
                if not line:
                    continue
                    
                lines_buffer.append(line)
                
                # FASTQ записи всегда по 4 строки
                if len(lines_buffer) == 4:
                    header_line, sequence_line, plus_line, quality_line = lines_buffer
                    
                    # Базовая валидация формата
                    if not header_line.startswith('@'):
                        raise ValueError(f"Invalid FASTQ format: expected '@' in header, got '{header_line}'")
                    if plus_line != '+':
                        raise ValueError(f"Invalid FASTQ format: expected '+', got '{plus_line}'")
                    if len(sequence_line) != len(quality_line):
                        raise ValueError(f"Sequence and quality length mismatch: {len(sequence_line)} != {len(quality_line)}")
                    
                    # Извлекаем ID (убираем @ и все после пробела/таба)
                    seq_id = header_line[1:].split()[0]
                    sequence = sequence_line
                    
                    if self.validate_sequence(sequence):
                        yield seq_id, sequence
                    
                    lines_buffer = []
    
    def read_with_quality(self) -> Iterator[Tuple[str, str, str]]:
        """Чтение с возвратом (seq_id, sequence, quality)."""
        with self:
            lines_buffer = []
            
            for line in self.iter_lines(strip=True):
                if not line:
                    continue
                    
                lines_buffer.append(line)
                
                if len(lines_buffer) == 4:
                    header_line, sequence_line, plus_line, quality_line = lines_buffer
                    seq_id = header_line[1:].split()[0]
                    
                    if self.validate_sequence(sequence_line):
                        yield seq_id, sequence_line, quality_line
                    
                    lines_buffer = []
    
    def _read_sequences(self) -> Iterator[Tuple[str, str, str, str]]:
        """Старый метод для обратной совместимости."""
        for header_line, sequence_line, plus_line, quality_line in self._read_fastq_entries():
            yield header_line[1:], sequence_line, plus_line, quality_line
    
    def _read_fastq_entries(self) -> Iterator[Tuple[str, str, str, str]]:
        """Чтение полных FASTQ записей."""
        with self:
            lines_buffer = []
            
            for line in self.iter_lines(strip=True):
                if not line:
                    continue
                    
                lines_buffer.append(line)
                
                if len(lines_buffer) == 4:
                    yield tuple(lines_buffer)
                    lines_buffer = []
    
    def get_quality_scores(self) -> List[int]:
        """Получить все quality scores как числа (осторожно с памятью!)."""
        if self._quality_scores_cache is None:
            scores = []
            for _, _, quality in self.read_with_quality():
                # Преобразование Phred качества в числа
                qual_scores = [ord(char) - 33 for char in quality]
                scores.extend(qual_scores)
            self._quality_scores_cache = scores
        return self._quality_scores_cache
    
    def average_quality(self) -> float:
        """Среднее качество последовательностей."""
        scores = self.get_quality_scores()
        return sum(scores) / len(scores) if scores else 0.0
    
    def plot_quality(self):
        """Простой график качества последовательностей."""
        try:
            import matplotlib.pyplot as plt
            
            scores = self.get_quality_scores()
            
            plt.figure(figsize=(10, 4))
            plt.hist(scores, bins=50, alpha=0.7)
            plt.xlabel('Quality Score')
            plt.ylabel('Frequency')
            plt.title('Sequence Quality Distribution')
            plt.grid(True, alpha=0.3)
            plt.show()
            
        except ImportError:
            print("Для построения графиков установите matplotlib: pip install matplotlib")
    
    def plot_length_distribution(self):
        """График распределения длин последовательностей."""
        try:
            import matplotlib.pyplot as plt
            
            lengths = [len(seq) for _, seq in self.read()]
            
            plt.figure(figsize=(10, 4))
            plt.hist(lengths, bins=30, alpha=0.7, edgecolor='black')
            plt.xlabel('Sequence Length')
            plt.ylabel('Frequency')
            plt.title('Sequence Length Distribution')
            plt.grid(True, alpha=0.3)
            plt.show()
            
        except ImportError:
            print("Для построения графиков установите matplotlib: pip install matplotlib")
    
    def filter_by_quality(self, min_quality: float = 20.0) -> Iterator[Tuple[str, str, str]]:
        """Фильтрация последовательностей по минимальному качеству."""
        for seq_id, sequence, quality in self.read_with_quality():
            qual_scores = [ord(char) - 33 for char in quality]
            avg_quality = sum(qual_scores) / len(qual_scores)
            if avg_quality >= min_quality:
                yield seq_id, sequence, quality