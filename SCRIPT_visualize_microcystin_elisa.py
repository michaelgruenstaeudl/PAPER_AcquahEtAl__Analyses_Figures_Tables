#!/usr/bin/env python3
"""
Visualize Microcystin ADDA ELISA plate-reader output.

This script is tailored to CSV exports that contain:
  1. a "Sample assignment map" 96-well plate block, and
  2. one or more "ADDA ELISA" absorbance plate blocks.

It averages repeated plate scans, averages duplicate wells for each sample,
fits a competitive ELISA standard curve, estimates sample concentrations, and
writes publication-ready plots plus a summarized CSV table.

For ABRAXIS Microcystin-ADDA ELISA, the standards are assumed to be:
Standard 0 = 0 ppb, Standard 1 = 0.15 ppb, Standard 2 = 0.40 ppb,
Standard 3 = 1.0 ppb, Standard 4 = 2.0 ppb, Standard 5 = 5.0 ppb.
The control is assumed to be 0.75 ppb.
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

try:
    from scipy.optimize import curve_fit
except Exception:  # pragma: no cover
    curve_fit = None


STANDARD_CONCENTRATIONS = {
    "Standard 0": 0.00,
    "Standard 1": 0.15,
    "Standard 2": 0.40,
    "Standard 3": 1.00,
    "Standard 4": 2.00,
    "Standard 5": 5.00,
}
CONTROL_CONCENTRATION = 0.75
ROWS = list("ABCDEFGH")
COLS = [str(i) for i in range(1, 13)]


def read_csv_rows(path: Path) -> list[list[str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return [[cell.strip() for cell in row] for row in csv.reader(handle)]


def find_plate_blocks(rows: list[list[str]]) -> list[tuple[str, int]]:
    """Return (protocol_name, header_row_index) for each 96-well plate block."""
    blocks: list[tuple[str, int]] = []
    current_protocol = None
    for i, row in enumerate(rows):
        if len(row) >= 2 and row[0] == "Protocol Name:":
            current_protocol = row[1]
        if len(row) >= 14 and row[0] == "450" and row[2:14] == COLS:
            blocks.append((current_protocol or "Unknown", i))
    return blocks


def plate_from_block(rows: list[list[str]], header_index: int, numeric: bool) -> pd.DataFrame:
    records = []
    for offset in range(1, 9):
        row = rows[header_index + offset]
        row_name = row[1]
        for col_name, value in zip(COLS, row[2:14]):
            records.append({"well": f"{row_name}{col_name}", "row": row_name, "column": int(col_name), "value": value})
    df = pd.DataFrame(records)
    if numeric:
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df


def four_parameter_logistic(x: np.ndarray, bottom: float, top: float, ec50: float, hill: float) -> np.ndarray:
    # Decreasing competitive ELISA curve when hill > 0 and top > bottom.
    return bottom + (top - bottom) / (1.0 + (x / ec50) ** hill)


def inverse_four_parameter_logistic(y: np.ndarray, bottom: float, top: float, ec50: float, hill: float) -> np.ndarray:
    y = np.asarray(y, dtype=float)
    ratio = (top - bottom) / (y - bottom) - 1.0
    out = ec50 * np.power(ratio, 1.0 / hill)
    invalid = (y >= top) | (y <= bottom) | (ratio <= 0)
    out[invalid] = np.nan
    return out


def fit_standard_curve(standards: pd.DataFrame) -> tuple[np.ndarray | None, str]:
    nonzero = standards[standards["known_ppb"] > 0].copy()
    x = nonzero["known_ppb"].to_numpy(float)
    y = nonzero["absorbance_mean"].to_numpy(float)

    if curve_fit is None:
        return None, "Scipy unavailable; concentration estimates use log-linear interpolation."

    p0 = [min(y) * 0.9, max(y) * 1.05, 0.75, 1.0]
    bounds = ([0.0, 0.0, 1e-6, 0.01], [3.0, 3.0, 100.0, 10.0])
    try:
        popt, _ = curve_fit(four_parameter_logistic, x, y, p0=p0, bounds=bounds, maxfev=20000)
        return popt, "4PL fit"
    except Exception as exc:
        return None, f"4PL fit failed ({exc}); concentration estimates use log-linear interpolation."


def interpolate_concentration(absorbance: np.ndarray, standards: pd.DataFrame) -> np.ndarray:
    # Monotone interpolation on nonzero standards. Absorbance decreases as concentration increases.
    nonzero = standards[standards["known_ppb"] > 0].sort_values("absorbance_mean")
    return np.interp(
        absorbance,
        nonzero["absorbance_mean"].to_numpy(float),
        nonzero["known_ppb"].to_numpy(float),
        left=np.nan,
        right=np.nan,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Visualize Microcystin ADDA ELISA CSV output.")
    parser.add_argument("csv_file", type=Path, help="Plate-reader CSV export")
    parser.add_argument("--outdir", type=Path, default=Path("elisa_plots"), help="Output directory")
    parser.add_argument("--dpi", type=int, default=300, help="Figure resolution")
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    rows = read_csv_rows(args.csv_file)
    blocks = find_plate_blocks(rows)

    map_blocks = [b for b in blocks if b[0] == "Sample assignment map"]
    data_blocks = [b for b in blocks if b[0] == "ADDA ELISA"]
    if not map_blocks:
        raise ValueError("No sample assignment map block found.")
    if not data_blocks:
        raise ValueError("No ADDA ELISA absorbance block found.")

    assignment = plate_from_block(rows, map_blocks[0][1], numeric=False).rename(columns={"value": "sample"})
    scans = []
    for scan_number, (_, header_index) in enumerate(data_blocks, start=1):
        scan = plate_from_block(rows, header_index, numeric=True).rename(columns={"value": "absorbance"})
        scan["scan"] = scan_number
        scans.append(scan)
    absorbance = pd.concat(scans, ignore_index=True)

    well_data = absorbance.merge(assignment[["well", "sample"]], on="well", how="left")
    well_data = well_data[well_data["sample"].notna() & (well_data["sample"] != "Empty")].copy()

    well_mean = (
        well_data.groupby(["well", "sample"], as_index=False)
        .agg(absorbance_mean=("absorbance", "mean"), absorbance_sd=("absorbance", "std"), n_scans=("absorbance", "size"))
    )

    summary = (
        well_mean.groupby("sample", as_index=False)
        .agg(
            absorbance_mean=("absorbance_mean", "mean"),
            absorbance_sd=("absorbance_mean", "std"),
            n_wells=("well", "size"),
            wells=("well", lambda x: ",".join(x)),
        )
    )
    summary["known_ppb"] = summary["sample"].map(STANDARD_CONCENTRATIONS)
    summary.loc[summary["sample"].str.fullmatch("Control", case=False, na=False), "known_ppb"] = CONTROL_CONCENTRATION

    standards = summary[summary["sample"].isin(STANDARD_CONCENTRATIONS)].copy()
    standards = standards.sort_values("known_ppb")
    popt, fit_note = fit_standard_curve(standards)

    if popt is not None:
        summary["estimated_ppb"] = inverse_four_parameter_logistic(summary["absorbance_mean"].to_numpy(float), *popt)
    else:
        summary["estimated_ppb"] = interpolate_concentration(summary["absorbance_mean"].to_numpy(float), standards)

    summary.loc[summary["sample"].isin(STANDARD_CONCENTRATIONS) | (summary["sample"] == "Control"), "estimated_ppb"] = summary["known_ppb"]
    summary["below_lowest_standard"] = summary["absorbance_mean"] > standards.loc[standards["known_ppb"] == 0.15, "absorbance_mean"].iloc[0]

    summary.to_csv(args.outdir / "elisa_summary.csv", index=False)
    well_data.to_csv(args.outdir / "elisa_well_level_data.csv", index=False)

    # Plot 1: standard curve.
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    nonzero = standards[standards["known_ppb"] > 0]
    ax.errorbar(nonzero["known_ppb"], nonzero["absorbance_mean"], yerr=nonzero["absorbance_sd"], fmt="o", capsize=3, label="Standards")
    if popt is not None:
        xgrid = np.logspace(np.log10(0.15), np.log10(5.0), 300)
        ax.plot(xgrid, four_parameter_logistic(xgrid, *popt), label="4PL fit")
    ax.set_xscale("log")
    ax.set_xlabel("Microcystin concentration (ppb)")
    ax.set_ylabel("Absorbance at 450 nm")
    ax.set_title("Microcystin-ADDA ELISA standard curve")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(args.outdir / "standard_curve.png", dpi=args.dpi)
    fig.savefig(args.outdir / "standard_curve.pdf")
    plt.close(fig)

    # Plot 2: sample absorbance means relative to standards.
    plot_df = summary[~summary["sample"].isin(STANDARD_CONCENTRATIONS)].copy()
    plot_df = plot_df.sort_values("absorbance_mean", ascending=True)
    fig, ax = plt.subplots(figsize=(8.5, max(4.5, 0.35 * len(plot_df))))
    y = np.arange(len(plot_df))
    ax.barh(y, plot_df["absorbance_mean"], xerr=plot_df["absorbance_sd"].fillna(0), capsize=2)
    ax.axvline(standards.loc[standards["known_ppb"] == 0.15, "absorbance_mean"].iloc[0], linestyle="--", linewidth=1, label="0.15 ppb standard")
    ax.axvline(standards.loc[standards["known_ppb"] == 0.00, "absorbance_mean"].iloc[0], linestyle=":", linewidth=1, label="0 ppb standard")
    ax.set_yticks(y)
    ax.set_yticklabels(plot_df["sample"])
    ax.set_xlabel("Absorbance at 450 nm")
    ax.set_title("Sample responses relative to ELISA standards")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(args.outdir / "sample_absorbance.png", dpi=args.dpi)
    fig.savefig(args.outdir / "sample_absorbance.pdf")
    plt.close(fig)

    # Plot 3: estimated concentrations, clipped visually at lowest standard when below range.
    sample_df = summary[~summary["sample"].isin(STANDARD_CONCENTRATIONS) & (summary["sample"] != "Control")].copy()
    sample_df = sample_df.sort_values("estimated_ppb", na_position="first")
    fig, ax = plt.subplots(figsize=(8.5, max(4.5, 0.35 * len(sample_df))))
    y = np.arange(len(sample_df))
    x = sample_df["estimated_ppb"].fillna(0.15)
    labels = ["<0.15" if below else (f"{val:.2f}" if pd.notna(val) else "out of range") for val, below in zip(sample_df["estimated_ppb"], sample_df["below_lowest_standard"])]
    ax.barh(y, x)
    ax.axvline(0.15, linestyle="--", linewidth=1, label="Lowest calibrated standard")
    for yi, xi, label in zip(y, x, labels):
        ax.text(xi, yi, f" {label}", va="center", fontsize=8)
    ax.set_xscale("log")
    ax.set_yticks(y)
    ax.set_yticklabels(sample_df["sample"])
    ax.set_xlabel("Estimated microcystin concentration (ppb)")
    ax.set_title("Estimated ADDA-containing microcystins")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(args.outdir / "estimated_microcystin.png", dpi=args.dpi)
    fig.savefig(args.outdir / "estimated_microcystin.pdf")
    plt.close(fig)

    print(f"Wrote results to: {args.outdir.resolve()}")
    print(f"Curve method: {fit_note}")


if __name__ == "__main__":
    main()
