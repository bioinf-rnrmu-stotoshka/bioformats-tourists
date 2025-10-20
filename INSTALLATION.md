# Установка и запуск BioFormat Tools

## Требования
- Python 3.9+
- Установленные зависимости

## Установка
```
git clone https://github.com/bioinf-rnrmu-stotoshka/bioformats-tourists
cd bioformats-tourists
pip install -r requirements.txt
```

## Использование
```
from bioformats import FastaReader, FastqReader, SamReader, VcfReader

with FastaReader('example.fasta') as reader:
for seq_id, sequence in reader.read():
print(f"{seq_id}: {len(sequence)} bp")
```

## Документация
```
cd docs
make.bat html
```

Открыть `docs/build/html/index.html` в браузере.