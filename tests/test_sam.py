import unittest
from pathlib import Path
from bioformats.sam import SamReader

SAM_CONTENT = """\
@HD\tVN:1.6\tSO:coordinate
@SQ\tSN:chr1\tLN:1000
@SQ\tSN:chr2\tLN:500
read1\t0\tchr1\t100\t255\t10M\t*\t0\t0\tACTGACTGAC\t*
read2\t0\tchr2\t250\t255\t10M\t*\t0\t0\tNNNNNNNNNN\t*
"""

class TestSamReader(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(__file__).parent
        self.path = self.tmp / "tiny.sam"
        self.path.write_text(SAM_CONTENT, encoding="utf-8")
        self.reader = SamReader(str(self.path))

    def test_get_header(self):
        header = self.reader.get_header()
        assert any("@HD" in line for line in header)
        assert sum(l.startswith("@SQ") for l in header) == 2

    def test_read(self):
        alignments = list(self.reader.read())
        assert len(alignments) == 2
        assert alignments[0]["qname"] == "read1"
        assert alignments[0]["chrom"] == "chr1"
        assert alignments[0]["pos"] == 100

    def test_count_and_filter(self):
        assert self.reader.count() == 2
        hits = list(self.reader.filter_by_region("chr1", 100, 120))
        assert len(hits) == 1
        assert hits[0]["qname"] == "read1"
