import unittest
from pathlib import Path
from bioformats.vcf import VcfReader

VCF_CONTENT = """\
##fileformat=VCFv4.2
##source=test
##reference=GRCh38
#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO
chr1\t100\t.\tA\tG\t50\tPASS\t.
chr1\t150\t.\tC\tT\t70\tPASS\t.
chr2\t250\t.\tG\tA\t99\tPASS\t.
"""

class TestVcfReader(unittest.TestCase):
    def setUp(self):
        p = Path(__file__).parent / "tiny.vcf"
        p.write_text(VCF_CONTENT, encoding="utf-8")
        self.reader = VcfReader(str(p))

    def test_header(self):
        header = self.reader.get_header()
        assert len(header) >= 3
        assert any("reference" in h for h in header)

    def test_read(self):
        variants = list(self.reader.read())
        assert len(variants) == 3
        assert variants[0]["chrom"] == "chr1"
        assert variants[0]["pos"] == 100

    def test_count_and_filter(self):
        assert self.reader.count() == 3
        hits = list(self.reader.filter_by_region("chr1", 90, 120))
        assert len(hits) == 1
        assert hits[0]["pos"] == 100
