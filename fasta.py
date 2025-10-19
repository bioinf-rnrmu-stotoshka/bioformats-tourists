class Fasta:
    """Класс для FASTA """
    
    def __init__(self, filename):
        self.filename = filename
    
    def count_sequences(self):
        """Подсчет количества последовательностей."""
        count = 0
        for _ in self._read_sequences():
            count += 1
        return count
    
    def average_length(self):
        """Вычисление средней длины"""
        total_length = 0
        count = 0
        
        for header, seq in self._read_sequences():
            total_length += len(seq)
            count += 1
        
        return total_length / count if count > 0 else 0
    
    def _read_sequences(self):
        """Генератор"""
        current_header = None
        current_seq = []
        
        with open(self.filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('>'):
                    if current_header is not None:
                        yield current_header, ''.join(current_seq)
                    current_header = line[1:]
                    current_seq = []
                else:
                    current_seq.append(line)
            
            if current_header is not None:
                yield current_header, ''.join(current_seq)