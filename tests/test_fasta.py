import textwrap
from bioformats import FastaReader


def write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    return p


def test_fasta_basic(tmp_path):
    fasta = write(
        tmp_path,
        "tiny.fasta",
        """
        >seq1
        ACGTACGT
        >seq2
        ACGTNN
        """,
    )

    r = FastaReader(str(fasta))
    items = list(r.read())

    assert len(items) == 2
    assert items[0][0] == "seq1"
    assert items[0][1] == "ACGTACGT"
    assert r.count() == 2
    assert r.average_length() == 7.0
    assert r.validate_sequence("ACGTN")
