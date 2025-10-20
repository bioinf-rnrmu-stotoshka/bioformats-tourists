# src/bioformats/reader.py
from __future__ import annotations
from typing import Iterator, Optional, Callable, TextIO
from contextlib import contextmanager
import io
import os
import gzip

class Reader:
    """
    Универсальный базовый ридер с «курсором» (self._fh).
    - Управляет ресурсом (open/close, контекстный менеджер)
    - Даёт итераторы строк (лениво), peek следующей строки,
      позиционирование (seek/tell), пропуск хедеров и т.д.
    - Прозрачно работает с .gz (text mode)
    """

    def __init__(self, filename: str, encoding: str = "utf-8", gz: Optional[bool] = None):
        self.filename = filename
        self.encoding = encoding
        # auto-detect gzip by extension, unless forced via gz=
        self._is_gz = gz if gz is not None else filename.endswith(".gz")
        self._fh: Optional[TextIO] = None
        self._peek_buf: Optional[str] = None  # буфер для peek_line()

    # ---------- lifecycle ----------
    def open(self) -> None:
        if self._fh is not None and not self._fh.closed:
            return
        if self._is_gz:
            # gzip в текстовом режиме с нужной кодировкой
            self._fh = io.TextIOWrapper(gzip.open(self.filename, "rb"), encoding=self.encoding)
        else:
            self._fh = open(self.filename, "r", encoding=self.encoding)

    def close(self) -> None:
        if self._fh and not self._fh.closed:
            try:
                # если обёрнутый gzip, корректно закрываем обе стороны
                raw = getattr(self._fh, "buffer", None)
                self._fh.close()
                if raw and hasattr(raw, "close"):
                    raw.close()
            finally:
                self._fh = None
                self._peek_buf = None

    def __enter__(self) -> "Reader":
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    # ---------- cursor utils ----------
    def tell(self) -> int:
        """Текущая позиция курсора (байты)."""
        assert self._fh is not None, "Reader is not open"
        return self._fh.tell()

    def seek(self, pos: int, whence: int = os.SEEK_SET) -> None:
        """Переместить курсор (байты). Сбрасывает peek-буфер."""
        assert self._fh is not None, "Reader is not open"
        self._fh.seek(pos, whence)
        self._peek_buf = None

    # ---------- line-level API ----------
    def _readline(self) -> Optional[str]:
        """Внутреннее чтение одной строки (с учётом peek-буфера)."""
        assert self._fh is not None, "Reader is not open"
        if self._peek_buf is not None:
            line, self._peek_buf = self._peek_buf, None
            return line
        line = self._fh.readline()
        if line == "":
            return None
        return line

    def peek_line(self) -> Optional[str]:
        """Вернуть следующую строку, не сдвигая курсор (одна строка буферизуется)."""
        assert self._fh is not None, "Reader is not open"
        if self._peek_buf is None:
            self._peek_buf = self._fh.readline()
            if self._peek_buf == "":
                self._peek_buf = None
        return self._peek_buf

    def iter_lines(self, strip: bool = True) -> Iterator[str]:
        """
        Ленивый генератор строк от текущей позиции.
        Учитывает peek-буфер. Ничего не грузит целиком в память.
        """
        self.open()
        while True:
            line = self._readline()
            if line is None:
                break
            yield line.strip() if strip else line

    def iter_until(self, stop_pred: Callable[[str], bool], include_stop: bool = False) -> Iterator[str]:
        """
        Идём по строкам, пока stop_pred(line) == False.
        Удобно для FASTA (копим до следующего '>' и т.п.).
        """
        for line in self.iter_lines(strip=False):
            if stop_pred(line):
                if include_stop:
                    yield line
                else:
                    # положим в peek, чтобы наследник увидел «границу»
                    self._peek_buf = line
                break
            else:
                yield line.rstrip("\n")

    def skip_while(self, pred: Callable[[str], bool]) -> None:
        """Пропустить строки, пока предикат истинен (например, хедеры SAM/VCF)."""
        while True:
            nxt = self.peek_line()
            if nxt is None or not pred(nxt):
                return
            _ = self._readline()  # реально потребим строку

    # ---------- binary/chunk (на всякий случай) ----------
    @contextmanager
    def raw(self):
        """Доступ к файловому объекту напрямую (если нужно что-то особенное)."""
        self.open()
        assert self._fh is not None
        yield self._fh

    def iter_chunked(self, size: int = 1 << 20) -> Iterator[str]:
        """
        Чтение крупными чанками (байты -> строки по splitlines()).
        Полезно для спец. случаев, обычно iter_lines достаточно.
        """
        self.open()
        assert self._fh is not None
        while True:
            chunk = self._fh.read(size)
            if not chunk:
                break
            for line in chunk.splitlines():
                yield line