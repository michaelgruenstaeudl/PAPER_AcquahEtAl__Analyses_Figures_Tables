# PAPER Acquah et al. - Figures and Tables
Code for generating publication-quality figures and tables for the manuscript of Acquah et al.

### Cross-connection
The analysis files of the data visualized here can be found on [Zenodo.org](https://zenodo.org/) under the repository with the DOI [10.5281/zenodo.20129247](https://doi.org/10.5281/zenodo.20129247).


### Visualizations

#### Figure Photo collage
```bash
bash SCRIPT__arrange_subimages_for_photo_collage.sh DATA__Subimages_for_PhotoCollage/ VIZ__PhotoCollage/PhotoCollage.jpg
```
![Photo collage of sampling at HorseThief Reservoir](VIZ__PhotoCollage/PhotoCollage.jpg)

#### Figure: 16S rRNA metagenomics
The code for creating the following figure is displayed [here](CODE__Figure_16S_rRNA_metagenomics.md).

![Compound figure on 16S rRNA metagenomics](VIZ__Figure_16S_rRNA_metagenomics/Fig_16S_rRNA__COMBINED.png)


#### Tables: Sequencing statistics and assembly quality
The code for extracting read statistics and assessing the quality of the assembly process is found [here](CODE__Assembly_quality_assessment.md). 

| Stage                                              | Illumina MiSeq - read pairs            | Oxford Nanopore - single reads |
| -------------------------------------------------- | -------------------------------------- | ------------------------------ |
| Pairs/reads pre-QC                                 | 8,581,010                              | 545,128                        |
| Pairs/reads post-QC (% of pre-QC)                  | 8,417,521 (98.09%)                     | 131,458 (24.12%)               |
| Avg. pair/read length post-QC (bp)                 | 295.2                                  | 4,527.4                        |
| Fully mapped pairs/reads (% of post-QC)            | 6,803,729 (80.83%)                     | 75,614 (57.52%)                |

The same tables in LaTeX format [here](TABLES/TABLE_Read_statistics_Illumina_and_OxfordNanopore.tex).

| Quality metric                         | Bacterial chromo | Plasmid           |
| -------------------------------------- | ---------------- | ----------------- |
| Length (bp)                            | 4,537,128        | 4,038             |
| N50                                    | 4,537,128        | 4,038             |
| L50                                    | 1                | 1                 |
| Longest segment (bp)                   | 4,537,128        | 4,038             |
| GC content (%)                         | 55.26%           | 49.33%            |
| Merqury: Consensus QV                  | 29.81            | 40.23             |
| Merqury: K-mer error rate              | 1.04e-03         | 9.49e-05          |
| Merqury: K-mer completeness (%)        | 96.68%           | 94.51%            |
| QUAST: Avg. cov. depth (Illumina; ON)  | 416X; 84X        | 2402X; 295X       |
| QUAST: Cov. >= 1X (% - Illumina; ON)   | 100%; 100%       | 100%; 100%        |
| QUAST: Cov. >= 10X (% - Illumina; ON)  | 100%; 100%       | 100%; 100%        |
| CheckM2: Completeness (%)              | 99.99%           | n.a.              |
| CheckM2: Contamination (%)             | 0.47%            | n.a.              |

Assembly statistics and quality assessment metrics for the complete bacterial chromosome and plasmid. The assembly size metrics (length, N50, L50, and longest segment length) were calculated from the initial raw contigs prior to circularization; all remaining metrics were inferred from the final circularized assemblies. CheckM2 did not evaluate the plasmid genome because the molecule is too small to encode sufficient lineage-specific genes for gene set comparisons. Abbreviations: Cov., coverage; QV, quality value; ON, Oxford Nanopore; n.a., not applicable.

The same tables in LaTeX format [here](TABLES/TABLE_Assembly_quality_metrics.tex).

#### Figure: Genome map
```bash
pip install cairosvg

python SCRIPT__generating_genome_map.py \
    --large-svg ./DATA__GenomeMap/03_for_merging/Limnothrix_sp_HT2024_chromosome__GenomeMap__step3.svg \
    --small-svg ./DATA__GenomeMap/03_for_merging/Limnothrix_sp_HT2024_plasmid__GenomeMap__step3.svg \
    --output-prefix ./VIZ__GenomeMap/genome_map \
    --large-size 4537128 \
    --small-size 4038 \
    --small-exaggeration 100
```
![Complete genome map](VIZ__GenomeMap/GenomeMap_withLegend_2026_05_27.png)


#### Figure: Comparative genomic analyses
The code for creating the following figure is displayed [here](CODE__Comparative_genomic_analyses.md).

![Dotplot figure](VIZ__Comparative_genomic_analyses/Limnothrix_sp_BLA16_vs_BacterialChr__MUMmer4.dotplot.png)


#### Figure: Genomic inversion testing
The code for creating the following figure is displayed [here](CODE__Genomic_inversion_testing.md).

![Compound figure on genomic inversion testing](VIZ__Figure_Genomic_inversion_testing/Fig_Genomic_inversion__COMBINED.png)



#### Table: Custom PCR primers for genomic inversion testing
The following oligonucleotide PCR primers were designed and used in the genomic inversion testing

| Inversion | Oligo Name | Oligo Sequence (5' to 3') | Approx. amplicon length |
| --------- | ---------- | ------------------------- | ----------------------- |
| 1         | sta.F      | AGCTARARAATCGCGCGATTAY    | Inv1.sta: 300 bp        |
| 1         | sta.R      | GGAGCATCAACCATGAAACAGC    |                         |
| 1         | end.F      | ATCCAGATTGGTACTTGGAAGCG   | Inv1.end: 400 bp        |
| 1         | end.R      | CTAGACTAAACTTCGGGGGTAGAC  |                         |
| ---       | ---        | ---                       | ---                     |
| 2         | sta.F      | TTGTGCATACCAAGTCCAAAAGTC  | Inv2.sta: 450 bp        |
| 2         | sta.R      | GGTAAGGAATTCGGGCTGATAGTA  |                         |
| 2         | end.F      | AAAACAGGAACMAAATAGCAGGGG  | Inv2.end: 120 bp        |
| 2         | end.R      | GATTTGTCAGCGTTAGAGATTGGG  |                         |
| ---       | ---        | ---                       | ---                     |
| 3         | sta.F      | AGGTCTAGCACTTCTGAGAGGAT   | Inv3.sta: 3000 bp       |
| 3         | sta.R      | GAAATTTTCAGCCGAATTCGCAC   |                         |
| 3         | end.F      | CGTTGCCCATCCCTGAAGAT      | Inv3.end: 1900 bp       |
| 3         | end.R      | AGAGCCGATCGTTGCGATAG      |                         |
| ---       | ---        | ---                       | ---                     |
| 4         | sta.F      | CCCAATGGTCACGMAAGGGTTAAT  | Inv4.sta: 1900 bp       |
| 4         | sta.R      | AAGGCATTGAACAAGGTATTGAGC  |                         |
| 4         | end.F      | AAGCSAWGAAASAKYACCCARACT  | Inv4.end: 1300 bp       |
| 4         | end.R      | YACCTACTAACTGCCTCATAGCAT  |                         |
| ---       | ---        | ---                       | ---                     |
| 5         | sta.F      | TYRCCAGTTCTTGMAATGCTGATT  | Inv5.sta: 300 bp        |
| 5         | sta.R      | TTTATCTATCAACGCTGTTTCGCC  |                         |
| 5         | end.F      | GCCATGTATTTGGATGTGTTGGAA  | Inv5.end: 470 bp        |
| 5         | end.R      | GCGATAGGCCCAAATCATAATTCC  |                         |
| ---       | ---        | ---                       | ---                     |
| 6         | sta.F      | AAAATCCGCCGAAGAAAATTTGC   | Inv6.sta: 2000 bp       |
| 6         | sta.R      | GGGAAGACCATYAAGGAAGCAGA   |                         |
| 6         | end.F      | ACAAAAACAACGAACAGGTAGGG   | Inv6.end: 290 bp        |
| 6         | end.R      | TTAACAATCCTTTCCCYACACCT   |                         |

The same table in LaTeX format [here](TABLES/TABLE_Custom_PCR_primers_for_genomic_inversion_testing.tex).