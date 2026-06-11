### Comparative genomic analyses (MUMmer4)

```bash
# Run from the paper workspace root
cd C:/GitHub/PAPER_AcquahEtAl__Analyses_Figures_Tables

# Input files
REF="./DATA__Comparative_genomic_analyses/Limnothrix_sp_BL_A_16_CP166615.fasta"
QRY="./DATA__Comparative_genomic_analyses/FinalAssembly_bactGenome_corrected.fasta"
INV="./DATA__Comparative_genomic_analyses/six_major_inversions_ref.csv"

# Temporary/derived alignment tables
OUTDIR="./DATA__Comparative_genomic_analyses"

# Final outputs
VIZDIR="./VIZ__Comparative_genomic_analyses"
LOG="${VIZDIR}/Limnothrix_sp_BLA16_vs_BacterialChr__orientation_identity_summary.txt"

mkdir -p "${OUTDIR}"
mkdir -p "${VIZDIR}"

# Create inversion-corrected reference
python SCRIPT__reverse_ref_inversions.py \
    "${REF}" \
    "${INV}" \
    "${OUTDIR}/Limnothrix_sp_BL_A_16_CP166615_inversions_corrected.fasta"

REF_CORRECTED="${OUTDIR}/Limnothrix_sp_BL_A_16_CP166615_inversions_corrected.fasta"

# Whole-genome alignment of the original chromosomes
nucmer --maxmatch \
    -p "${OUTDIR}/original_orientation" \
    "${REF}" \
    "${QRY}"

delta-filter -r -q -l 1000 \
    "${OUTDIR}/original_orientation.delta" \
    > "${OUTDIR}/original_orientation.filt.delta"

show-coords -rclTH \
    "${OUTDIR}/original_orientation.filt.delta" \
    > "${OUTDIR}/original_orientation.coords.tsv"

# Whole-genome alignment after computational correction of inversion regions
nucmer --maxmatch \
    -p "${OUTDIR}/inversion_corrected" \
    "${REF_CORRECTED}" \
    "${QRY}"

delta-filter -r -q -l 1000 \
    "${OUTDIR}/inversion_corrected.delta" \
    > "${OUTDIR}/inversion_corrected.filt.delta"

show-coords -rclTH \
    "${OUTDIR}/inversion_corrected.filt.delta" \
    > "${OUTDIR}/inversion_corrected.coords.tsv"

# Dotplot visualizations (PNG and SVG)
python SCRIPT__MUMmer4_plot_coords_dotplot.py \
    "${OUTDIR}/original_orientation.coords.tsv" \
    "${VIZDIR}/original_orientation_dotplot"

python SCRIPT__MUMmer4_plot_coords_dotplot.py \
    "${OUTDIR}/inversion_corrected.coords.tsv" \
    "${VIZDIR}/inversion_corrected_dotplot"

# Similarity summary log
python SCRIPT__summarize_mummer_identity.py \
    "${REF}" \
    "${QRY}" \
    "${OUTDIR}/original_orientation.coords.tsv" \
    "${OUTDIR}/inversion_corrected.coords.tsv" \
    | tee "${LOG}"
```### Comparative genomic analyses (MUMmer4)

```bash
# Activate environment (example)
conda activate mummer4_env

# Paths
DATADIR="./DATA__Comparative_genomic_analyses"
VIZDIR="./VIZ__Comparative_genomic_analyses"
REF="${DATADIR}/input/Limnothrix_sp_BL_A_16_CP166615.fasta"
QRY="${DATADIR}/input/FinalAssembly_bactGenome_corrected.fasta"
INV="${DATADIR}/six_major_inversions_ref.csv"
PFX="${DATADIR}/Limnothrix_sp_BLA16_vs_BacterialChr__MUMmer4"

mkdir -p "${DATADIR}" "${VIZDIR}"

# 1) Whole-genome alignment and plotting
nucmer --maxmatch -p "${PFX}" "${REF}" "${QRY}"
delta-filter -r -q -l 1000 "${PFX}.delta" > "${PFX}.filt.delta"
show-coords -H -T -r -c "${PFX}.filt.delta" > "${PFX}.coords.tsv"

python SCRIPT__MUMmer4_plot_coords_dotplot.py \
  "${PFX}.coords.tsv" \
  "${VIZDIR}/Limnothrix_sp_BLA16_vs_BacterialChr__MUMmer4.dotplot"

# 2) Inversion-corrected comparison and identity summary
python SCRIPT__reverse_ref_inversions.py \
  "${REF}" \
  "${INV}" \
  "${DATADIR}/Limnothrix_sp_BL_A_16_CP166615_reoriented.fasta"

REF_CORRECTED="${DATADIR}/Limnothrix_sp_BL_A_16_CP166615_reoriented.fasta"

nucmer --maxmatch -p "${DATADIR}/original_orientation" "${REF}" "${QRY}"
delta-filter -r -q -l 1000 "${DATADIR}/original_orientation.delta" > "${DATADIR}/original_orientation.filt.delta"
show-coords -rclTH "${DATADIR}/original_orientation.filt.delta" > "${DATADIR}/original_orientation.coords.tsv"

nucmer --maxmatch -p "${DATADIR}/inversion_corrected" "${REF_CORRECTED}" "${QRY}"
delta-filter -r -q -l 1000 "${DATADIR}/inversion_corrected.delta" > "${DATADIR}/inversion_corrected.filt.delta"
show-coords -rclTH "${DATADIR}/inversion_corrected.filt.delta" > "${DATADIR}/inversion_corrected.coords.tsv"

python SCRIPT__summarize_mummer_identity.py \
  "${REF}" \
  "${QRY}" \
  "${DATADIR}/original_orientation.coords.tsv" \
  "${DATADIR}/inversion_corrected.coords.tsv" \
  | tee "${VIZDIR}/Limnothrix_sp_BLA16_vs_BacterialChr__orientation_identity_summary.txt"
```

### Output locations
- Temporary and intermediate data: `DATA__Comparative_genomic_analyses`
- Dotplot images (`.png`, `.svg`): `VIZ__Comparative_genomic_analyses`
- Orientation/identity summary log: `VIZ__Comparative_genomic_analyses`
