"""
bioformats — учебный пакет для чтения и анализа биологических форматов данных:
FASTA, FASTQ, SAM и VCF.

Архитектура:
    Reader — базовый класс (работа с файлом, курсор, итерация)
    SequenceReader — абстрактный класс для форматов последовательностей
    GenomicDataReader — абстрактный класс для геномных форматов
    FastaReader, FastqReader, SamReader, VcfReader — конкретные реализации

Пример:
    from bioformats import FastaReader

    with FastaReader("sample.fasta") as r:
        for seq_id, seq in r.read():
            print(seq_id, len(seq))
"""

from .reader import Reader
from .sequences import SequenceReader
from .genomic import GenomicDataReader
from .fasta import FastaReader
from .fastq import FastqReader
from .sam import SamReader
from .vcf import VcfReader

__all__ = ["Reader","SequenceReader","GenomicDataReader","FastaReader","FastqReader","SamReader","VcfReader"]


__version__ = "0.1.0"
__author__ = "bioformats-tourists team"
__license__ = "MIT"
