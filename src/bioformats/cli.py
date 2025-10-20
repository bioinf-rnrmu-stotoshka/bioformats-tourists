from __future__ import annotations
import argparse
import os
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import matplotlib.pyplot as plt

from . import FastaReader, FastqReader
from .sam import SamReader
from .vcf import VcfReader


# ---------------------- FASTA ----------------------
def cmd_fasta_stats(args: argparse.Namespace) -> None:
    r = FastaReader(args.input)
    n = r.count()
    avg_len = r.average_length()
    print(f"[FASTA] file: {args.input}")
    print(f"  sequences: {n}")
    print(f"  average length: {avg_len:.2f}")


# ---------------------- FASTQ (QC) ----------------------
def cmd_fastq_qc(args: argparse.Namespace) -> None:
    outdir = Path(args.outdir or "reports")
    outdir.mkdir(parents=True, exist_ok=True)

    qual_by_pos: Dict[int, List[int]] = {}
    base_by_pos: Dict[int, Dict[str, int]] = {}
    lengths: List[int] = []

    fq = FastqReader(args.input)

    # ❗️Один проход: сразу берём (id, seq, qual)
    made_any = False
    for sid, seq, qual in fq._iter_fastq_triplets():
        made_any = True
        lengths.append(len(seq))
        # Phred+33
        quals = [ord(ch) - 33 for ch in qual]
        for i, (b, qv) in enumerate(zip(seq, quals)):
            qual_by_pos.setdefault(i, []).append(qv)
            d = base_by_pos.setdefault(i, {"A": 0, "C": 0, "G": 0, "T": 0, "N": 0})
            d[b.upper()] = d.get(b.upper(), 0) + 1

    if not made_any:
        print(f"[FASTQ] file: {args.input} appears empty.")
        return

    # --- per base sequence quality
    xs = sorted(qual_by_pos.keys())
    mean_q = [sum(qual_by_pos[i]) / len(qual_by_pos[i]) for i in xs]
    plt.figure()
    plt.plot([x + 1 for x in xs], mean_q, marker="o")
    plt.xlabel("Base position"); plt.ylabel("Mean Phred score")
    plt.title("Per-base sequence quality"); plt.grid(True, alpha=0.3)
    plt.tight_layout()
    p1 = outdir / "fastq_per_base_quality.png"
    plt.savefig(p1); plt.close()

    # --- per base sequence content
    acgtn = {"A": [], "C": [], "G": [], "T": [], "N": []}
    for i in xs:
        total = sum(base_by_pos[i].values()) or 1
        for b in acgtn:
            acgtn[b].append(100.0 * base_by_pos[i].get(b, 0) / total)

    plt.figure()
    for b in ["A", "C", "G", "T", "N"]:
        plt.plot([x + 1 for x in xs], acgtn[b], label=b)
    plt.xlabel("Base position"); plt.ylabel("Content, %")
    plt.title("Per-base sequence content"); plt.legend()
    plt.grid(True, alpha=0.3); plt.tight_layout()
    p2 = outdir / "fastq_per_base_content.png"
    plt.savefig(p2); plt.close()

    # --- sequence length distribution
    plt.figure()
    plt.hist(lengths, bins=min(50, max(10, int(len(lengths) ** 0.5))))
    plt.xlabel("Read length"); plt.ylabel("Count"); plt.title("Sequence length distribution")
    plt.tight_layout()
    p3 = outdir / "fastq_sequence_length_distribution.png"
    plt.savefig(p3); plt.close()

    print(f"[FASTQ] QC done. Saved plots to: {outdir}")
    print(f"  - {p1.name}\n  - {p2.name}\n  - {p3.name}")

# ---------------------- SAM ----------------------
def sam_df(reader: SamReader) -> pd.DataFrame:
    rows = []
    for rec in reader.read():
        rows.append(rec)
    return pd.DataFrame(rows)

def cmd_sam_chromstat(args: argparse.Namespace) -> None:
    r = SamReader(args.input)
    df = sam_df(r)
    if df.empty:
        print(f"[SAM] no alignments in {args.input}")
        return
    counts = df.groupby("chrom").size().reset_index(name="count").sort_values("count", ascending=False)
    print(f"[SAM] alignments per chromosome:\n{counts.to_string(index=False)}")
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        counts.to_csv(args.out, index=False)
        print(f"  saved CSV → {args.out}")

def cmd_sam_slice(args: argparse.Namespace) -> None:
    r = SamReader(args.input)
    hits = list(r.filter_by_region(args.chrom, args.start, args.end))
    print(f"[SAM] slice {args.chrom}:{args.start}-{args.end} → {len(hits)} alignments")
    for h in hits[: min(10, len(hits))]:
        print(f"  {h.get('qname')} {h.get('chrom')}:{h.get('pos')}")


# ---------------------- VCF ----------------------
def vcf_df(reader: VcfReader) -> pd.DataFrame:
    rows = []
    for rec in reader.read():
        rows.append(rec)
    return pd.DataFrame(rows)

def cmd_vcf_chromstat(args: argparse.Namespace) -> None:
    r = VcfReader(args.input)
    df = vcf_df(r)
    if df.empty:
        print(f"[VCF] no variants in {args.input}")
        return
    counts = df.groupby("chrom").size().reset_index(name="count").sort_values("count", ascending=False)
    print(f"[VCF] variants per chromosome:\n{counts.to_string(index=False)}")
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        counts.to_csv(args.out, index=False)
        print(f"  saved CSV → {args.out}")

def cmd_vcf_slice(args: argparse.Namespace) -> None:
    r = VcfReader(args.input)
    hits = list(r.filter_by_region(args.chrom, args.start, args.end))
    print(f"[VCF] slice {args.chrom}:{args.start}-{args.end} → {len(hits)} variants")
    for v in hits[: min(10, len(hits))]:
        print(f"  {v.get('chrom')}:{v.get('pos')} {v.get('ref','?')}>{v.get('alt','?')}")


# ---------------------- CLI WIRING ----------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="bioformats", description="Demo CLI for FASTA/FASTQ/SAM/VCF")
    sub = p.add_subparsers(dest="cmd", required=True)

    # fasta stats
    p_fasta = sub.add_parser("fasta", help="FASTA utilities")
    sub_fasta = p_fasta.add_subparsers(dest="subcmd", required=True)
    p_fasta_stats = sub_fasta.add_parser("stats", help="Count sequences & average length")
    p_fasta_stats.add_argument("-i", "--input", required=True, help="FASTA file")
    p_fasta_stats.set_defaults(func=cmd_fasta_stats)

    # fastq qc
    p_fastq = sub.add_parser("fastq", help="FASTQ QC")
    sub_fastq = p_fastq.add_subparsers(dest="subcmd", required=True)
    p_fastq_qc = sub_fastq.add_parser("qc", help="Generate FastQC-like plots")
    p_fastq_qc.add_argument("-i", "--input", required=True, help="FASTQ file")
    p_fastq_qc.add_argument("-o", "--outdir", default="reports", help="Output directory for plots")
    p_fastq_qc.set_defaults(func=cmd_fastq_qc)

    # sam
    p_sam = sub.add_parser("sam", help="SAM utilities")
    sub_sam = p_sam.add_subparsers(dest="subcmd", required=True)
    p_sam_chrom = sub_sam.add_parser("chromstat", help="Alignments per chromosome (CSV optional)")
    p_sam_chrom.add_argument("-i", "--input", required=True, help="SAM file")
    p_sam_chrom.add_argument("-o", "--out", help="Output CSV path")
    p_sam_chrom.set_defaults(func=cmd_sam_chromstat)

    p_sam_slice = sub_sam.add_parser("slice", help="Extract alignments in region")
    p_sam_slice.add_argument("-i", "--input", required=True, help="SAM file")
    p_sam_slice.add_argument("--chrom", required=True)
    p_sam_slice.add_argument("--start", type=int, required=True)
    p_sam_slice.add_argument("--end", type=int, required=True)
    p_sam_slice.set_defaults(func=cmd_sam_slice)

    # vcf
    p_vcf = sub.add_parser("vcf", help="VCF utilities")
    sub_vcf = p_vcf.add_subparsers(dest="subcmd", required=True)
    p_vcf_chrom = sub_vcf.add_parser("chromstat", help="Variants per chromosome (CSV optional)")
    p_vcf_chrom.add_argument("-i", "--input", required=True, help="VCF file")
    p_vcf_chrom.add_argument("-o", "--out", help="Output CSV path")
    p_vcf_chrom.set_defaults(func=cmd_vcf_chromstat)

    p_vcf_slice = sub_vcf.add_parser("slice", help="Extract variants in region")
    p_vcf_slice.add_argument("-i", "--input", required=True, help="VCF file")
    p_vcf_slice.add_argument("--chrom", required=True)
    p_vcf_slice.add_argument("--start", type=int, required=True)
    p_vcf_slice.add_argument("--end", type=int, required=True)
    p_vcf_slice.set_defaults(func=cmd_vcf_slice)

    return p


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
