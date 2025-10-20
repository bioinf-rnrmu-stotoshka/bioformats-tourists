# src/bioformats/sequences.py
from __future__ import annotations
from typing import Iterator, Tuple, Optional
from abc import ABC, abstractmethod

from .reader import Reader

SequencePair = Tuple[str, str]  # (seq_id, sequence)

class SequenceReader(Reader, ABC):
    """
    Абстрактный ридер последовательностей.
    Наследники (FastaReader, FastqReader) обязаны реализовать read(),
    который лениво выдаёт пары (seq_id, sequence).

    Общие методы (get_sequence, validate_sequence, count, average_length)
    работают полиморфно для всех наследников.
    """

    def __init__(
        self,
        filename: str,
        *,
        alphabet: str = "ACGTNacgtn",
        encoding: str = "utf-8",
        gz: Optional[bool] = None,
    ) -> None:
        super().__init__(filename, encoding=encoding, gz=gz)
        self.alphabet = set(alphabet)

    # ----- обязателен к реализации в наследниках -----
    @abstractmethod
    def read(self) -> Iterator[SequencePair]:
        """
        Должен лениво возвращать (seq_id, sequence).
        Пример для FASTA: ('seq1', 'ACGT...')
        Пример для FASTQ: ('seq1', 'ACGT...')  # качество обрабатывается в наследнике
        """
        ...

    # ----- общий полиморфный API для всех формат-ридеров -----
    def __iter__(self) -> Iterator[SequencePair]:
        return self.read()

    def get_sequence(self, seq_id: str) -> str:
        """Найти и вернуть последовательность по идентификатору (O(n))."""
        for sid, seq in self.read():
            if sid == seq_id:
                return seq
        raise KeyError(f"Sequence {seq_id!r} not found in {self.filename}")

    def validate_sequence(self, sequence: str) -> bool:
        """Базовая валидация по алфавиту (можно переопределить в наследнике)."""
        return all(ch in self.alphabet for ch in sequence)

    def count(self) -> int:
        """Количество последовательностей в файле."""
        return sum(1 for _ in self.read())

    def average_length(self) -> float:
        """Средняя длина последовательностей (0.0, если пусто)."""
        total = 0
        n = 0
        for _, seq in self.read():
            total += len(seq)
            n += 1
        return (total / n) if n else 0.0