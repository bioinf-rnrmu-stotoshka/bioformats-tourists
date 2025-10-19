
class Fastq:
    """Класс для FASTQ файлов."""
    
    def __init__(self, filename):
        self.filename = filename
    
    def count_sequences(self):
        """Подсчет количества последовательностей."""
        count = 0
        for _ in self._read_sequences():
            count += 1
        return count
    
    def average_length(self):
        """Вычисление средней длины последовательностей."""
        total_length = 0
        count = 0
        
        for header, seq, plus, qual in self._read_sequences():
            total_length += len(seq)
            count += 1
        
        return total_length / count if count > 0 else 0
    
    def plot_quality(self):
        """Простой график качества последовательностей."""
        try:
            import matplotlib.pyplot as plt
            
            qualities = []
            for header, seq, plus, qual in self._read_sequences():
                # Преобразование Phred качества в числа
                qual_scores = [ord(char) - 33 for char in qual]
                qualities.extend(qual_scores)
            
            plt.figure(figsize=(10, 4))
            plt.hist(qualities, bins=50, alpha=0.7)
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
            
            lengths = []
            for header, seq, plus, qual in self._read_sequences():
                lengths.append(len(seq))
            
            plt.figure(figsize=(10, 4))
            plt.hist(lengths, bins=30, alpha=0.7, edgecolor='black')
            plt.xlabel('Sequence Length')
            plt.ylabel('Frequency')
            plt.title('Sequence Length Distribution')
            plt.grid(True, alpha=0.3)
            plt.show()
            
        except ImportError:
            print("Для построения графиков установите matplotlib: pip install matplotlib")
    
    def _read_sequences(self):
        """Генератор"""
        lines = []
        with open(self.filename, 'r') as f:
            for line in f:
                lines.append(line.strip())
                if len(lines) == 4:
                    yield lines[0][1:], lines[1], lines[2], lines[3]  # header, sequence, plus, quality
                    lines = []