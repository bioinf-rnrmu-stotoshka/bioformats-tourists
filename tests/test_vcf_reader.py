import unittest
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from bioformats.vcf_reader import VcfReader


class TestVcfReader(unittest.TestCase):

    def setUp(self):
        """Подготовка тестовых данных"""
        self.test_vcf = "../test.vcf"
        self.reader = VcfReader(self.test_vcf)

    def test_get_header(self):
        """Тест чтения заголовка VCF"""
        header_lines = self.reader.get_header()

        # В test.vcf 4 строки заголовка
        self.assertEqual(len(header_lines), 4)
        self.assertTrue(any(line.startswith('##') for line in header_lines))
        self.assertTrue(any(line.startswith('#CHROM') for line in header_lines))

    def test_read(self):
        """Тест чтения вариантов"""
        variants = list(self.reader.read())

        # Должно быть 3 варианта
        self.assertEqual(len(variants), 3)

        # Проверяем первый вариант
        first_var = variants[0]
        self.assertEqual(first_var['chrom'], 'chr1')
        self.assertEqual(first_var['pos'], 100)
        self.assertEqual(first_var['ref'], 'A')
        self.assertEqual(first_var['alt'], 'T')
        self.assertEqual(first_var['qual'], 29.5)

    def test_count(self):
        """Тест подсчета вариантов"""
        count = self.reader.count()
        self.assertEqual(count, 3)

    def test_filter_by_region(self):
        """Тест фильтрации по региону"""
        # Ищем варианты в регионе chr1:100-120
        variants = list(self.reader.filter_by_region('chr1', 100, 120))


        self.assertEqual(len(variants), 1)
        self.assertEqual(variants[0]['pos'], 100)
        self.assertEqual(variants[0]['ref'], 'A')

        # Регион где ничего нет
        empty_variants = list(self.reader.filter_by_region('chr1', 300, 400))
        self.assertEqual(len(empty_variants), 0)


if __name__ == '__main__':
    unittest.main()