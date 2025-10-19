import unittest
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from bioformats.sam_reader import SamReader


class TestSamReader(unittest.TestCase):

    def setUp(self):
        """Подготовка тестовых данных"""
        self.test_sam = "../test.sam"
        self.reader = SamReader(self.test_sam)

    def test_get_header(self):
        """Тест чтения заголовка SAM"""
        header_lines = self.reader.get_header()

        # В test.sam 3 строки заголовка: @HD, @SQ, @SQ
        self.assertEqual(len(header_lines), 3)
        self.assertTrue(any('@HD' in line for line in header_lines))
        self.assertTrue(any('@SQ' in line for line in header_lines))

    def test_read(self):
        """Тест чтения выравниваний"""
        alignments = list(self.reader.read())

        # Должно быть 2 выравнивания
        self.assertEqual(len(alignments), 2)

        # Проверяем первое выравнивание
        first_align = alignments[0]
        self.assertEqual(first_align['qname'], 'read1')
        self.assertEqual(first_align['chrom'], 'chr1')
        self.assertEqual(first_align['pos'], 100)

    def test_count(self):
        """Тест подсчета выравниваний"""
        count = self.reader.count()
        self.assertEqual(count, 2)

    def test_filter_by_region(self):
        """Тест фильтрации по региону"""
        # Ищем выравнивания в регионе chr1:100-120
        alignments = list(self.reader.filter_by_region('chr1', 100, 120))

        # Должно найти только read1 (позиция 100)
        self.assertEqual(len(alignments), 1)
        self.assertEqual(alignments[0]['qname'], 'read1')

        # Регион где ничего нет
        empty_alignments = list(self.reader.filter_by_region('chr1', 200, 300))
        self.assertEqual(len(empty_alignments), 0)


if __name__ == '__main__':
    unittest.main()