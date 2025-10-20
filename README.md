[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/I6I1ViQv)
# кто-то код писал, а кто-то спал
# ходят слухи что именно они делают документацию


 ниже — готовый `README.md`. Скопируй целиком в корень репозитория как `README.md`. Я отметил 2 удобные места, куда вставлять изображение UML (SVG/PNG).

---

# bioformats

Учебный пакет для чтения и анализа **FASTA, FASTQ, SAM, VCF** c акцентом на работу с большими файлами (генераторы).
Проект включает CLI-утилиту `bioformats`, автотесты и Sphinx-документацию.

> **UML диаграмма классов**
> Вставь файл с диаграммой (например, `docs/uml.svg` или `images/uml.png`) вот сюда:
> `![UML diagram](docs/uml.svg)`
> *(см. раздел «Диаграмма классов (UML)» ниже для генерации и места хранения)*

---

## Возможности

* **FASTA/FASTQ**: количество записей, средняя длина; в FASTQ — извлечение Phred-качеств и средних значений.
* **FASTQ QC**: три графика — *per-base quality*, *per-base content*, *length distribution*.
* **SAM/VCF**: чтение заголовков, подсчёт записей, статистика по хромосомам, фильтрация по региону.
* Чтение ленивыми генераторами, поддержка больших файлов.

---

## Установка

Рекомендуется отдельное виртуальное окружение.

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
python -m pip install -U pip
pip install -e .[dev]           # поставит пакет + pytest
```

Проверка:

```bash
python -c "import bioformats; print('bioformats', bioformats.__version__)"
bioformats --help
```

---

## Быстрый старт (CLI)

Данные для демо лежат в `sample_data/`.

### FASTA

```bash
bioformats fasta stats -i sample_data/example.fasta
```

### FASTQ (QC графики → папка reports/)

```bash
bioformats fastq qc -i sample_data/example.fastq -o reports
```

### SAM

```bash
bioformats sam chromstat -i sample_data/example.sam -o reports/sam_chrom.csv
bioformats sam slice -i sample_data/example.sam --chrom chr1 --start 100 --end 200
```

### VCF

```bash
bioformats vcf chromstat -i sample_data/example.vcf -o reports/vcf_chrom.csv
bioformats vcf slice -i sample_data/example.vcf --chrom chr1 --start 90 --end 150
```

---

## Использование как библиотеки

```python
from bioformats import FastaReader, FastqReader
from bioformats.sam import SamReader
from bioformats.vcf import VcfReader

with FastaReader("my.fasta") as r:
    print("N=", r.count(), "avg_len=", r.average_length())

fq = FastqReader("reads.fastq")
print(fq.get_average_quality("read_001"))

sam = SamReader("alignments.sam")
hits = list(sam.filter_by_region("chr1", 100_000, 101_000))

vcf = VcfReader("variants.vcf")
print("Variants:", vcf.count())
```

---

## Тесты

```bash
pytest -q
```

> Если запускаешь не из корня — убедись, что `pytest.ini` содержит:
>
> ```
> [pytest]
> pythonpath = src
> ```

---

## Документация (Sphinx)

Установить инструменты:

```bash
pip install -e .[docs]
```

Сборка HTML:

```bash
make -C docs html
# открыть: docs/build/html/index.html
```

Публикация на GitHub Pages: включить Pages в настройках репозитория и указывать ветку/папку с собранным HTML (например, `gh-pages`).

---

## Диаграмма классов (UML)

### Как сгенерировать автоматически

**Вариант A — Sphinx встроенно**

1. Установи системно Graphviz (macOS `brew install graphviz` / Ubuntu `sudo apt-get install graphviz` / Windows `choco install graphviz`).
2. В `docs/source/uml.rst` добавь:

```
UML
===

.. inheritance-diagram::
   bioformats.reader
   bioformats.sequences
   bioformats.genomic
   bioformats.fasta
   bioformats.fastq
   bioformats.sam
   bioformats.vcf
   :parts: 1
   :top-classes: bioformats.reader.Reader
```

3. Собери: `make -C docs html` — SVG окажется в `docs/build/html/_images/`.

**Вариант B — pyreverse (PNG/SVG)**

```bash
pip install pylint graphviz
pyreverse -o svg -p bioformats src/bioformats
# получишь: classes_bioformats.svg
```

### Куда положить и как вставить в README

* Рекомендуем поместить в `docs/uml.svg` **или** `images/uml.png`.
* Вставка в README (Markdown):

```markdown
![UML diagram](docs/uml.svg)
```

*(Это то самое место вверху README, помеченное как «UML диаграмма классов».)*

---

## Структура проекта

```
bioformats-tourists/
├── README.md
├── pyproject.toml
├── pytest.ini
├── src/bioformats/
│   ├── __init__.py
│   ├── reader.py
│   ├── sequences.py
│   ├── genomic.py
│   ├── fasta.py
│   ├── fastq.py
│   ├── sam.py
│   ├── vcf.py
│   └── cli.py
├── tests/
│   ├── test_fasta.py
│   ├── test_fastq.py
│   ├── test_sam.py
│   └── test_vcf.py
├── sample_data/
│   ├── example.fasta
│   ├── example.fastq
│   ├── example.sam
│   └── example.vcf
└── docs/                      # Sphinx
    └── ...
```

---

## Лицензия

MIT (см. `LICENSE`).

---

## Благодарности

Команда **bioformats-tourists**. Спасибо за примеры данных NCBI/UniProt.

---

> **Напоминание про UML:**
> После того как получишь картинку, просто добавь файл `docs/uml.svg` в репозиторий и раскомментируй/оставь строку:
> `![UML diagram](docs/uml.svg)` — изображение появится в этом README на GitHub.

<img width="205" height="201" alt="Снимок экрана 2025-10-20 в 03 49 06" src="https://github.com/user-attachments/assets/4eefb02e-b242-4530-a5f4-7951484aa94a" />
<img width="203" height="199" alt="Снимок экрана 2025-10-20 в 03 55 29" src="https://github.com/user-attachments/assets/1245a9ec-adeb-4433-a946-a6459b1d09f0" />


<img width="203" height="199" alt="Снимок экрана 2025-10-20 в 03 57 02" src="https://github.com/user-attachments/assets/9f85c26d-491d-4a03-bf95-d98353cb3bd4" />
<img width="203" height="199" alt="Снимок экрана 2025-10-20 в 03 57 16" src="https://github.com/user-attachments/assets/7149c201-0dd6-4d7c-be98-a7678f91fc84" />

<img width="201" height="191" alt="Снимок экрана 2025-10-20 в 03 57 45" src="https://github.com/user-attachments/assets/7ca73840-0cb8-4316-82ac-2b3f34e58f4a" />

<img width="201" height="191" alt="Снимок экрана 2025-10-20 в 03 59 11" src="https://github.com/user-attachments/assets/35ea3087-9927-4b28-b320-701e9ca2a185" />
