import unittest
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from vcf_reader import VcfReader


class TestVcfReader(unittest.TestCase):

    def setUp(self):
        """Подготовка тестовых данных"""
        self.test_vcf = "test.vcf"  # файл в корне проекта
        self.reader = VcfReader(self.test_vcf)

    def test_get_header(self):
        """Тест чтения заголовка VCF"""
        header = self.reader.get_header()

        # Проверяем структуру заголовка
        self.assertIn('meta', header)
        self.assertIn('columns', header)

        # Проверяем колонки
        self.assertEqual(len(header['columns']), 8)  # Должно быть 8 колонок
        expected_columns = ['CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO']
        self.assertEqual(header['columns'], expected_columns)

    def test_read_variants(self):
        """Тест чтения вариантов"""
        variants = list(self.reader.read_variants())

        # Должно быть 3 варианта
        self.assertEqual(len(variants), 3)

        # Проверяем первый вариант
        first_var = variants[0]
        self.assertEqual(first_var['chrom'], 'chr1')
        self.assertEqual(first_var['pos'], 100)
        self.assertEqual(first_var['ref'], 'A')
        self.assertEqual(first_var['alt'], 'T')
        self.assertEqual(first_var['qual'], 29.5)

    def test_get_variant_count(self):
        """Тест подсчета вариантов"""
        count = self.reader.get_variant_count()
        self.assertEqual(count, 3)  # Должно быть 3 варианта

    def test_get_variant_statistics(self):
        """Тест статистики с pandas"""
        stats = self.reader.get_variant_statistics()

        # Проверяем структуру DataFrame
        self.assertEqual(list(stats.columns), ['region', 'count'])
        self.assertEqual(len(stats), 2)  # Должны быть 2 региона (chr1 и chr2)

        # Проверяем данные
        chr1_data = stats[stats['region'] == 'chr1']
        chr2_data = stats[stats['region'] == 'chr2']
        self.assertEqual(chr1_data.iloc[0]['count'], 2)  # В chr1 должно быть 2 варианта
        self.assertEqual(chr2_data.iloc[0]['count'], 1)  # В chr2 должно быть 1 вариант

    def test_get_variants_in_region(self):
        """Тест фильтрации по региону"""
        # Ищем варианты в регионе chr1:100-120
        variants = self.reader.get_variants_in_region('chr1', 100, 120)

        # Должно найти только первый вариант (позиция 100)
        self.assertEqual(len(variants), 1)
        self.assertEqual(variants[0]['pos'], 100)
        self.assertEqual(variants[0]['ref'], 'A')

        # Регион где ничего нет
        empty_variants = self.reader.get_variants_in_region('chr1', 300, 400)
        self.assertEqual(len(empty_variants), 0)


if __name__ == '__main__':
    unittest.main()