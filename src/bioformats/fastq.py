from __future__ import annotations
from typing import Iterator, Tuple, List, Dict, Optional

from .sequences import SequenceReader

SequencePair = Tuple[str, str]  # (seq_id, sequence)


class FastqReader(SequenceReader):
    """
    Ридер FASTQ:
    - read()        -> (seq_id, sequence)
    - get_quality_scores(seq_id) -> List[int] (Phred+33)
    - get_average_quality(seq_id) -> float
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
        self._seq_cache: Dict[str, str] = {}
        self._qual_cache: Dict[str, List[int]] = {}
        self._scanned: bool = False  # прошли ли по файлу полностью и заполнили кэши

    # ---------- публичный API ----------
    def read(self) -> Iterator[SequencePair]:
        """
        Ленивое чтение FASTQ файла с возвратом (seq_id, sequence).
        Без кэширования: полезно, когда нужен поток.
        """
        for sid, seq, _qual in self._iter_fastq_triplets():
            yield (sid, seq)

    def get_quality_scores(self, seq_id: str) -> List[int]:
        """
        Вернуть список Phred-оценок для данного seq_id (Phred+33).
        Первый вызов пройдёт по файлу, далее берём из кэша.
        """
        if seq_id in self._qual_cache:
            return self._qual_cache[seq_id]

        # если уже сканировали весь файл и не нашли — пусто
        if self._scanned:
            return []

        # иначе сканируем, наполняем кэши
        for sid, seq, q in self._iter_fastq_triplets():
            self._seq_cache.setdefault(sid, seq)
            self._qual_cache.setdefault(sid, self._phred(q))
            if sid == seq_id:
                return self._qual_cache[sid]

        # дошли до конца — теперь знаем, что всё прочитано
        self._scanned = True
        return self._qual_cache.get(seq_id, [])

    def get_average_quality(self, seq_id: str) -> float:
        scores = self.get_quality_scores(seq_id)
        return (sum(scores) / len(scores)) if scores else 0.0

    # ---------- внутренняя логика ----------
    def _iter_fastq_triplets(self) -> Iterator[Tuple[str, str, str]]:
        """
        Генератор записей FASTQ: (seq_id, sequence, quality_string).

        Каждая запись — 4 строки:
          @<id>
          <SEQ>
          +
          <QUAL>         (длина QUAL == длине SEQ)

        Допускаем '+' с комментарием (например, '+ r1'), это валидно по FASTQ.
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
            lines_buffer = []  # сбросить буфер под следующую запись

            # базовые проверки формата
            if not header_line.startswith("@"):
                raise ValueError(f"Invalid FASTQ header: expected '@', got {header_line!r}")

            # '+' допускает дополнительные символы (например '+ r1')
            if not plus_line.startswith("+"):
                raise ValueError(f"Invalid FASTQ plus-line: expected '+', got {plus_line!r}")

            # длина seq и qual должна совпадать
            if len(sequence_line) != len(quality_line):
                raise ValueError(
                    f"Sequence and quality length mismatch: {len(sequence_line)} != {len(quality_line)}"
                )

            seq_id = header_line[1:].strip()
            yield (seq_id, sequence_line, quality_line)

        # если файл закончился на неполной записи — это форматная ошибка
        if lines_buffer:
            raise ValueError("Truncated FASTQ record at EOF (incomplete 4-line block).")

    @staticmethod
    def _phred(qual: str) -> List[int]:
        """Преобразование строки качеств в список Phred-оценок (Phred+33)."""
        # '!' -> 0, '"' -> 1, '#' -> 2, 'I' -> 40, и т.д.
        return [ord(ch) - 33 for ch in qual]
