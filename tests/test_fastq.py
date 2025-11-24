import textwrap
from bioformats import FastqReader


def write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    return p


def test_fastq_quality_api(tmp_path):
    fastq = write(
        tmp_path,
        "q.fastq",
        """
        @r1
        ACGT
        +
        IIII
        @r2
        ACAA
        +
        !!!!
        """,
    )
    r = FastqReader(str(fastq))

    q1 = r.get_quality_scores("r1")
    assert len(q1) == 4
    assert r.get_average_quality("r1") == 40.0
    q2 = r.get_quality_scores("r2")
    assert len(q2) == 4
    assert r.get_average_quality("r2") == 0.0


def test_fastq_iterates_records(tmp_path):
    fastq = write(
        tmp_path,
        "iter.fastq",
        """
        @a
        ACT
        +
        !!!
        @b
        GGGG
        +
        ####
        """,
    )

    r = FastqReader(str(fastq))
    items = list(r.read())

    assert len(items) == 2
    assert items[0][0] == "a"
    assert items[0][1] == "ACT"
    assert items[1][0] == "b"
    assert items[1][1] == "GGGG"
