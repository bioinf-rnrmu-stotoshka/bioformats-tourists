#!/usr/bin/env python3
"""
Демонстрационная программа для SAM и VCF ридеров
"""

import sys
import os

# Добавляем путь к нашим модулям
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sam_reader import SamReader
from vcf_reader import VcfReader


def demo_sam_reader():
    """Демонстрация работы SAM ридера"""
    print("=" * 50)
    print("ДЕМО: SAM READER")
    print("=" * 50)

    reader = SamReader('test.sam')

    # 1. Заголовок
    header = reader.get_header()
    print("1. ЗАГОЛОВОК SAM:")
    print(f"   - Версия: {header['HD'][0]['VN']}")
    print(f"   - Сортировка: {header['HD'][0]['SO']}")
    print(f"   - Хромосомы: {[sq['SN'] for sq in header['SQ']]}")

    # 2. Количество выравниваний
    count = reader.get_alignment_count()
    print(f"2. КОЛИЧЕСТВО ВЫРАВНИВАНИЙ: {count}")

    # 3. Статистика с pandas
    stats = reader.get_alignment_statistics()
    print("3. СТАТИСТИКА ПО ХРОМОСОМАМ:")
    print(stats.to_string(index=False))

    # 4. Фильтрация по региону
    print("4. ФИЛЬТРАЦИЯ (chr1:100-120):")
    alignments = reader.get_alignments_in_region('chr1', 100, 120)
    for align in alignments:
        print(f"   - {align['qname']}: pos={align['pos']}, cigar={align['cigar']}")

    # 5. Чтение выравниваний
    print("5. ПЕРВЫЕ 2 ВЫРАВНИВАНИЯ:")
    reader2 = SamReader('test.sam')
    for i, align in enumerate(reader2.read_alignments()):
        if i >= 2:  # Покажем только первые 2
            break
        print(f"   - {align['qname']}: {align['rname']}:{align['pos']}")


def demo_vcf_reader():
    """Демонстрация работы VCF ридера"""
    print("\n" + "=" * 50)
    print("ДЕМО: VCF READER")
    print("=" * 50)

    reader = VcfReader('test.vcf')

    # 1. Заголовок
    header = reader.get_header()
    print("1. ЗАГОЛОВОК VCF:")
    print(f"   - Колонки: {header['columns']}")
    print(f"   - Мета-строк: {len(header['meta'])}")

    # 2. Количество вариантов
    count = reader.get_variant_count()
    print(f"2. КОЛИЧЕСТВО ВАРИАНТОВ: {count}")

    # 3. Статистика с pandas
    stats = reader.get_variant_statistics()
    print("3. СТАТИСТИКА ПО РЕГИОНАМ:")
    print(stats.to_string(index=False))

    # 4. Фильтрация по региону
    print("4. ФИЛЬТРАЦИЯ (chr1:100-120):")
    variants = reader.get_variants_in_region('chr1', 100, 120)
    for var in variants:
        print(f"   - {var['chrom']}:{var['pos']} {var['ref']}->{var['alt']} (qual={var['qual']})")

    # 5. Чтение вариантов
    print("5. ВСЕ ВАРИАНТЫ:")
    reader2 = VcfReader('test.vcf')
    for var in reader2.read_variants():
        print(f"   - {var['chrom']}:{var['pos']} {var['ref']}->{var['alt']}")


if __name__ == "__main__":
    demo_sam_reader()
    demo_vcf_reader()
    print("\n" + "=" * 50)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 50)
