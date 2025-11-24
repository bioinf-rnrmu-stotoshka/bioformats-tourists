# fastq.py
from __future__ import annotations
from typing import Iterator, Tuple, Optional

from .sequences import SequenceReader

SequencePair = Tuple[str, str]  # (seq_id, sequence)


class FastqReader(SequenceReader):
    """
    Ридер FASTQ.

    Минимальный функционал под задание:

    - read() -> (seq_id, sequence)    — ленивое чтение для статистики
    - _iter_fastq_triplets()          — внутренний генератор (id, seq, qual)
      для построения графиков качества в CLI.
    """

    def __init__(
        self,
        filename: str,
        *,
        alphabet: str = "ACGTNacgtn",
        encoding: str = "utf-8",
        gz: Optional[bool] = None,
    ) -> None:
        super().__init__(filename, alphabet=alphabet, encoding=encoding, gz=gz)

    # ---------- публичный API ----------
    def read(self) -> Iterator[SequencePair]:
        """Ленивое чтение FASTQ файла с возвратом (seq_id, sequence)."""
        for sid, seq, _qual in self._iter_fastq_triplets():
            yield sid, seq

    # ---------- внутренняя логика ----------
    def _iter_fastq_triplets(self) -> Iterator[Tuple[str, str, str]]:
        """
        Генератор записей FASTQ: (seq_id, sequence, quality_string).

        Каждая запись — 4 строки:
          @<id>
          <SEQ>
          +
          <QUAL>
        """
        self.open()
        lines_buffer: list[str] = []

        for line in self.iter_lines(strip=True):
            if not line:
                continue
            lines_buffer.append(line)
            if len(lines_buffer) < 4:
                continue

            header_line, sequence_line, plus_line, quality_line = lines_buffer
            lines_buffer = []  # под следующую запись

            if not header_line.startswith("@"):
                raise ValueError(
                    f"Invalid FASTQ header: expected '@', got {header_line!r}"
                )

            if not plus_line.startswith("+"):
                raise ValueError(
                    f"Invalid FASTQ plus-line: expected '+', got {plus_line!r}"
                )

            if len(sequence_line) != len(quality_line):
                raise ValueError(
                    "Sequence and quality length mismatch: "
                    f"{len(sequence_line)} != {len(quality_line)}"
                )

            seq_id = header_line[1:].strip()
            yield seq_id, sequence_line, quality_line

        if lines_buffer:
            raise ValueError("Truncated FASTQ record at EOF (incomplete 4-line block).")
