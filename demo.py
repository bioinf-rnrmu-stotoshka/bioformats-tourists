#!/usr/bin/env python3
"""
Демонстрационная программа для SAM и VCF ридеров
"""

import sys
import os

# Добавляем путь к нашим модулям
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from bioformats.sam_reader import SamReader
from bioformats.vcf_reader import VcfReader


def parse_sam_header(header_lines):
    """Парсим SAM заголовок из списка строк"""
    header = {'HD': [], 'SQ': []}
    for line in header_lines:
        if line.startswith('@HD'):
            parts = line.split('\t')
            hd_info = {}
            for part in parts[1:]:
                if ':' in part:
                    key, value = part.split(':', 1)
                    hd_info[key] = value
            header['HD'].append(hd_info)
        elif line.startswith('@SQ'):
            parts = line.split('\t')
            sq_info = {}
            for part in parts[1:]:
                if ':' in part:
                    key, value = part.split(':', 1)
                    sq_info[key] = value
            header['SQ'].append(sq_info)
    return header


def demo_sam_reader():
    """Демонстрация работы SAM ридера"""
    print("=" * 50)
    print("ДЕМО: SAM READER")
    print("=" * 50)

    reader = SamReader('test.sam')

    # 1. Заголовок (теперь парсим вручную)
    header_lines = reader.get_header()
    header = parse_sam_header(header_lines)
    print("1. ЗАГОЛОВОК SAM:")
    if header['HD']:
        print(f"   - Версия: {header['HD'][0].get('VN', 'N/A')}")
        print(f"   - Сортировка: {header['HD'][0].get('SO', 'N/A')}")
    print(f"   - Хромосомы: {[sq['SN'] for sq in header['SQ']]}")

    # 2. Количество выравниваний
    count = reader.count()  # используем унаследованный метод!
    print(f"2. КОЛИЧЕСТВО ВЫРАВНИВАНИЙ: {count}")

    # 3. Статистика с pandas
    stats_df = reader.to_dataframe()  # используем унаследованный метод!
    stats = stats_df.groupby('chrom').size().reset_index(name='count')
    print("3. СТАТИСТИКА ПО ХРОМОСОМАМ:")
    print(stats.to_string(index=False))

    # 4. Фильтрация по региону
    print("4. ФИЛЬТРАЦИЯ (chr1:100-120):")
    alignments = list(reader.filter_by_region('chr1', 100, 120))  # унаследованный метод!
    for align in alignments:
        print(f"   - {align['qname']}: pos={align['pos']}, cigar={align['cigar']}")

    # 5. Чтение выравниваний
    print("5. ПЕРВЫЕ 2 ВЫРАВНИВАНИЯ:")
    reader2 = SamReader('test.sam')
    for i, align in enumerate(reader2.read()):
        if i >= 2:
            break
        print(f"   - {align['qname']}: {align['chrom']}:{align['pos']}")


def demo_vcf_reader():
    """Демонстрация работы VCF ридера"""
    print("\n" + "=" * 50)
    print("ДЕМО: VCF READER")
    print("=" * 50)

    reader = VcfReader('test.vcf')

    # 1. Заголовок
    header = reader.get_header()
    print("1. ЗАГОЛОВОК VCF:")
    print(f"   - Строк заголовка: {len(header)}")
    if header:
        columns_line = [line for line in header if line.startswith('#CHROM')]
        if columns_line:
            columns = columns_line[0].lstrip('#').split('\t')
            print(f"   - Колонки: {columns}")

    # 2. Количество вариантов
    count = reader.count()  # унаследованный метод!
    print(f"2. КОЛИЧЕСТВО ВАРИАНТОВ: {count}")

    # 3. Статистика с pandas
    stats_df = reader.to_dataframe()  # унаследованный метод!
    stats = stats_df.groupby('chrom').size().reset_index(name='count')
    print("3. СТАТИСТИКА ПО РЕГИОНАМ:")
    print(stats.to_string(index=False))

    # 4. Фильтрация по региону
    print("4. ФИЛЬТРАЦИЯ (chr1:100-120):")
    variants = list(reader.filter_by_region('chr1', 100, 120))  # унаследованный метод!
    for var in variants:
        print(f"   - {var['chrom']}:{var['pos']} {var['ref']}->{var['alt']} (qual={var['qual']})")

    # 5. Чтение вариантов
    print("5. ВСЕ ВАРИАНТЫ:")
    reader2 = VcfReader('test.vcf')
    for var in reader2.read():
        print(f"   - {var['chrom']}:{var['pos']} {var['ref']}->{var['alt']}")


if __name__ == "__main__":
    demo_sam_reader()
    demo_vcf_reader()
    print("\n" + "=" * 50)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
    print("=" * 50)
