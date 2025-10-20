# BioFormat Tools


![img_2.png](img_2.png)

Проект для работы с основными биологическими форматами данных: FASTA, FASTQ, SAM, VCF.

## Возможности

- **FASTA**: чтение последовательностей, статистика
- **FASTQ**: анализ качества, построение графиков  
- **SAM**: работа с выравниваниями, фильтрация по регионам
- **VCF**: анализ геномных вариантов

## Быстрый старт

```bash
# Установка
git clone https://github.com/bioinf-rnrmu-stotoshka/bioformats-tourists
cd bioformats-tourists
pip install -r requirements.txt

# Использование
from bioformats import FastaReader

with FastaReader('example.fasta') as reader:
    for seq_id, sequence in reader.read():
        print(f"{seq_id}: {len(sequence)} bp")

Документация
Полная документация доступна в папке docs/build/html/.

Команда
bioformats-tourists team

