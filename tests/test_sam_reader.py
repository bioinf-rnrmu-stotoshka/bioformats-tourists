import unittest
import os
import sys

# Добавляем путь чтобы импортировать наши модули
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from sam_reader import SamReader


class TestSamReader(unittest.TestCase):

    def setUp(self):
        """Подготовка тестовых данных"""
        self.test_sam = "test.sam"  # файл в корне проекта
        self.reader = SamReader(self.test_sam)

    def test_get_header(self):
        """Тест чтения заголовка SAM"""
        header = self.reader.get_header()

        # Проверяем что заголовок содержит нужные секции
        self.assertIn('HD', header)
        self.assertIn('SQ', header)

        # Проверяем данные хромосом
        self.assertEqual(len(header['SQ']), 2)  # Должно быть 2 хромосомы
        self.assertEqual(header['SQ'][0]['SN'], 'chr1')  # Первая хромосома - chr1
        self.assertEqual(header['SQ'][1]['SN'], 'chr2')  # Вторая хромосома - chr2

    def test_read_alignments(self):
        """Тест чтения выравниваний"""
        alignments = list(self.reader.read_alignments())

        # Должно быть 2 выравнивания
        self.assertEqual(len(alignments), 2)

        # Проверяем первое выравнивание
        first_align = alignments[0]
        self.assertEqual(first_align['qname'], 'read1')
        self.assertEqual(first_align['rname'], 'chr1')
        self.assertEqual(first_align['pos'], 100)

    def test_get_alignment_count(self):
        """Тест подсчета выравниваний"""
        count = self.reader.get_alignment_count()
        self.assertEqual(count, 2)  # Должно быть 2 выравнивания

    def test_get_alignment_statistics(self):
        """Тест статистики с pandas"""
        stats = self.reader.get_alignment_statistics()

        # Проверяем структуру DataFrame
        self.assertEqual(list(stats.columns), ['chromosome', 'count'])
        self.assertEqual(len(stats), 1)  # Должна быть 1 хромосома в статистике

        # Проверяем данные
        chr1_data = stats[stats['chromosome'] == 'chr1']
        self.assertEqual(chr1_data.iloc[0]['count'], 2)  # В chr1 должно быть 2 выравнивания

    def test_get_alignments_in_region(self):
        """Тест фильтрации по региону"""
        # Ищем выравнивания в регионе chr1:100-120
        alignments = self.reader.get_alignments_in_region('chr1', 100, 120)

        # Должно найти только read1 (позиция 100)
        self.assertEqual(len(alignments), 1)
        self.assertEqual(alignments[0]['qname'], 'read1')

        # Регион где ничего нет
        empty_alignments = self.reader.get_alignments_in_region('chr1', 200, 300)
        self.assertEqual(len(empty_alignments), 0)


if __name__ == '__main__':
    unittest.main()