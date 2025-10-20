# BioFormat Tools


![img_2.png](img_2.png)

Проект для работы с основными биологическими форматами данных: FASTA, FASTQ, SAM, VCF.

## Возможности

- **FASTA**: чтение последовательностей, статистика
- **FASTQ**: анализ качества, построение графиков  
- **SAM**: работа с выравниваниями, фильтрация по регионам
- **VCF**: анализ геномных вариантов

---
## Установка (Python 3.9+)
```bash
git clone https://github.com/bioinf-rnrmu-stotoshka/bioformats-tourists
cd bioformats-tourists

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -U pip

# установить пакет (из pyproject.toml)
pip install -e .
# для разработки с тестами можно так:
# pip install -e .[dev]
```
---
## Быстрый пример (как библиотека)
```
from bioformats import FastaReader
with FastaReader("sample_data/example.fasta") as reader:
    for seq_id, sequence in reader.read():
        print(f"{seq_id}: {len(sequence)} bp")
```
---
## CLI (демонстрационные команды)
```
# FASTA статистика
bioformats fasta stats -i sample_data/example.fasta

# FASTQ QC: сохранит 3 PNG в ./reports
bioformats fastq qc -i sample_data/example.fastq -o reports

# SAM: сводка по хромосомам и срез по региону
bioformats sam chromstat -i sample_data/example.sam
bioformats sam slice -i sample_data/example.sam --chrom chr1 --start 100 --end 200

# VCF: сводка и срез
bioformats vcf chromstat -i sample_data/example.vcf
bioformats vcf slice -i sample_data/example.vcf --chrom chr1 --start 90 --end 150
```

## Документация

```
Полная документация доступна в папке docs/build/html/
```
## Команда

<img width="201" height="201" alt="Снимок экрана 2025-10-20 в 13 22 42" src="https://github.com/user-attachments/assets/2105e197-5d97-4bf6-9664-ccc45d9e6b02" />
<img width="201" height="201" alt="Снимок экрана 2025-10-20 в 13 22 55" src="https://github.com/user-attachments/assets/525cf805-7f72-47df-afdd-fa0f1efff502" />
<img width="201" height="201" alt="Снимок экрана 2025-10-20 в 13 23 06" src="https://github.com/user-attachments/assets/6a8ba2c0-6225-44cb-a5c9-c2974457c5cf" />
<img width="201" height="201" alt="Снимок экрана 2025-10-20 в 13 23 28" src="https://github.com/user-attachments/assets/843846ae-83ac-4485-bd41-5200babe6923" />

Все очень старались

 Лицензия
```
Проект распространяется под лицензией MIT.
См. LICENSE
 для подробностей.

```

<img width="1229" height="580" alt="Снимок экрана 2025-10-20 в 13 46 44" src="https://github.com/user-attachments/assets/97b11dc0-893f-457b-bba7-2ce190deb8ae" />



