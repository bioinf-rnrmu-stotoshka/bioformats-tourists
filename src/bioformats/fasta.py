# fasta.py
"""
FASTA ридер.

Наследуется от SequenceReader и реализует только ленивое чтение
последовательностей (seq_id, sequence). Статистика:
- count()
- average_length()

реализована в базовом SequenceReader.
"""

from typing import Iterator
from .sequences import SequenceReader, SequencePair


class FastaReader(SequenceReader):
    """Класс для работы с FASTA файлами."""

    def read(self) -> Iterator[SequencePair]:
        """
        Ленивое чтение FASTA файла с возвратом (seq_id, sequence).

        Формат:
            >seq_id [опциональное описание]
            ACGT...
            ACGT...
        """
        with self:
            current_header = None
            current_seq_parts: list[str] = []

            for line in self.iter_lines(strip=True):
                if not line:
                    continue

                if line.startswith(">"):
                    # если была предыдущая последовательность — отдаём её
                    if current_header is not None and current_seq_parts:
                        sequence = "".join(current_seq_parts)
                        if self.validate_sequence(sequence):
                            yield current_header, sequence

                    # начинаем новую
                    current_header = line[1:].split()[0]  # только первый токен до пробела
                    current_seq_parts = []
                else:
                    current_seq_parts.append(line)

            # последняя последовательность
            if current_header is not None and current_seq_parts:
                sequence = "".join(current_seq_parts)
                if self.validate_sequence(sequence):
                    yield current_header, sequence
