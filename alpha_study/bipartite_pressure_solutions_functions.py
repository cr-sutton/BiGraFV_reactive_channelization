from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import r2_score


def read_scalar_from_vtk(vtk_path, scalar_name="Liquid_Pressure"):
    values = []
    data_n = None
    found_scalars = False
    after_lookup = False

    with open(vtk_path, "r", errors="replace") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue

            if s.startswith("POINT_DATA") or s.startswith("CELL_DATA"):
                parts = s.split()
                if len(parts) >= 2:
                    try:
                        data_n = int(parts[1])
                    except ValueError:
                        data_n = None

            parts = s.split()

            if len(parts) >= 2 and parts[0] == "SCALARS" and parts[1] == scalar_name:
                found_scalars = True
                after_lookup = False
                continue

            if found_scalars and after_lookup and len(parts) >= 1 and parts[0] == "SCALARS":
                break

            if found_scalars and s.startswith("LOOKUP_TABLE"):
                after_lookup = True
                continue

            if found_scalars and after_lookup:
                for tok in parts:
                    try:
                        values.append(float(tok))
                    except ValueError:
                        break

                    if data_n is not None and len(values) >= data_n:
                        break

            if data_n is not None and len(values) >= data_n:
                break

    if not found_scalars:
        raise ValueError(f"Could not find scalar '{scalar_name}' in {vtk_path}")

    values = np.asarray(values, dtype=float)

    if data_n is not None and len(values) != data_n:
        raise ValueError(
            f"VTK scalar '{scalar_name}' read {len(values)} values, expected {data_n}"
        )

    return values


def read_fracture_pressure_from_dfn(
    materialid_path,
    vtk_path,
    scalar_name="Liquid_Pressure",
    header_lines=3,
):
    fracture_ids = []
    with open(materialid_path, "r") as f:
        for _ in range(header_lines):
            next(f, None)
        for line in f:
            s = line.strip()
            if not s:
                continue
            fracture_ids.append(int(s.split()[0]))

    fracture_ids = np.asarray(fracture_ids, dtype=int)
    values = read_scalar_from_vtk(vtk_path, scalar_name=scalar_name)

    n_expected = len(fracture_ids)
    if len(values) < n_expected:
        raise ValueError(
            f"VTK scalar '{scalar_name}' read {len(values)} values, "
            f"but materialid.dat has {n_expected} IDs."
        )

    values = values[:n_expected]

    ids_unique = np.unique(fracture_ids)
    mean_vals = np.zeros(ids_unique.shape[0], dtype=float)

    for k, fid in enumerate(ids_unique):
        mean_vals[k] = values[fracture_ids == fid].mean()

    return pd.DataFrame({
        "fracture_id": ids_unique,
        "pressure_fullDFN": mean_vals,
    })


def parse_graph_inp(inp_path: str, want_fields=("imt1", "pressure")):
    """
    Parse mesh .inp file and return:
      - df_all : all parsed numeric columns
      - df_sel : requested columns only

    This mirrors the old workflow
    """

    def is_descriptor_line(s: str) -> bool:
        if "," not in s:
            return False
        left = s.split(",", 1)[0].strip()
        right = s.split(",", 1)[1].strip().lower()
        if not left:
            return False
        return ("integer" in right) or ("real" in right)

    def starts_with_int(s: str) -> bool:
        if not s:
            return False
        tok = s.split()[0]
        return tok.lstrip("+-").isdigit()

    with open(inp_path, "r", errors="replace") as f:
        lines = [ln.rstrip("\n") for ln in f]

    desc_start = None
    desc_fields = []

    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if is_descriptor_line(s):
            j = i
            fields = []
            while j < len(lines) and is_descriptor_line(lines[j].strip()):
                name = lines[j].split(",", 1)[0].strip()
                fields.append(name)
                j += 1

            fields_lower = [x.lower() for x in fields]
            if all(w.lower() in fields_lower for w in want_fields):
                desc_start = i
                desc_fields = fields
                i = j
                break

            i = j
        else:
            i += 1

    if desc_start is None:
        raise ValueError(
            f"Could not find a block containing fields {want_fields} in {inp_path}"
        )

    k = desc_start + len(desc_fields)

    while k < len(lines) and not starts_with_int(lines[k].strip()):
        k += 1

    if k >= len(lines):
        raise ValueError("Found block but no numeric data rows after it.")

    data_rows = []
    ncols = None

    while k < len(lines):
        s = lines[k].strip()
        if not s:
            k += 1
            continue

        if not starts_with_int(s):
            break

        parts = s.split()

        try:
            row = [float(x) for x in parts]
        except ValueError:
            break

        if ncols is None:
            ncols = len(row)
        else:
            if len(row) < ncols:
                row = row + [float("nan")] * (ncols - len(row))
            elif len(row) > ncols:
                row = row[:ncols]

        data_rows.append(row)
        k += 1

    if not data_rows:
        raise ValueError("No numeric table rows parsed.")

    colnames = [f"col{i}" for i in range(1, ncols + 1)]

    if ncols == 1 + len(desc_fields):
        colnames = ["row_id"] + desc_fields
    else:
        colnames[0] = "row_id"
        max_map = min(len(desc_fields), ncols - 1)
        for idx in range(max_map):
            colnames[1 + idx] = desc_fields[idx]

    df_all = pd.DataFrame(data_rows, columns=colnames)

    cols_lower = {c.lower(): c for c in df_all.columns}
    missing = [w for w in want_fields if w.lower() not in cols_lower]
    if missing:
        raise ValueError(
            f"Parsed table but could not find columns {missing}. "
            f"Available columns: {list(df_all.columns)}"
        )

    df_sel = pd.DataFrame({w: df_all[cols_lower[w.lower()]] for w in want_fields})

    if "imt1" in [w.lower() for w in want_fields]:
        imt_col = cols_lower["imt1"]
        df_sel["imt1"] = df_all[imt_col].round().astype("Int64")

    return df_all, df_sel


def make_pressure_plots(x, y, outdir=None, prefix=""):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.size == 0 or y.size == 0:
        return

    outdir = Path(outdir) if outdir is not None else None
    if outdir is not None:
        outdir.mkdir(parents=True, exist_ok=True)

    mn = min(np.min(x), np.min(y))
    mx = max(np.max(x), np.max(y))
    residual = y - x
    r2 = r2_score(x, y) if x.size > 1 else np.nan

    # 1:1 plot
    plt.figure()
    plt.scatter(x, y, alpha=0.4, s=20)
    plt.plot([mn, mx], [mn, mx])
    plt.xlabel("Full DFN pressure")
    plt.ylabel("Graph pressure")
    plt.title(f"1:1 pressure comparison (R²={r2:.6f})")
    plt.grid(True)
    plt.tight_layout()
    if outdir is not None:
        plt.savefig(outdir / f"{prefix}pressure_1to1.png", dpi=200)
    plt.close()

    # residual scatter plot
    plt.figure()
    plt.scatter(x, residual, alpha=0.4, s=20)
    plt.axhline(0.0, linestyle="--")
    plt.xlabel("Full DFN pressure")
    plt.ylabel("Residual (graph - DFN)")
    plt.title("Residual plot")
    plt.grid(True)
    plt.tight_layout()
    if outdir is not None:
        plt.savefig(outdir / f"{prefix}pressure_residuals.png", dpi=200)
    plt.close()

    # residual KDE
    plt.figure()
    kde = stats.gaussian_kde(residual)
    xx = np.linspace(residual.min(), residual.max(), 500)
    plt.plot(xx, kde(xx))
    plt.axvline(0.0, linestyle="--")
    plt.xlabel("Residual (graph - DFN)")
    plt.ylabel("Density")
    plt.title("KDE of residuals")
    plt.grid(True)
    plt.tight_layout()
    if outdir is not None:
        plt.savefig(outdir / f"{prefix}pressure_residuals_kde.png", dpi=200)
    plt.close()

    # Q-Q plot
    plt.figure()
    stats.probplot(residual, dist="norm", plot=plt)
    plt.title("Q-Q plot of residuals")
    plt.tight_layout()
    if outdir is not None:
        plt.savefig(outdir / f"{prefix}pressure_residuals_qq.png", dpi=200)
    plt.close()


def get_pressures(
    materialid_path: str = "./4_rects_dfn/materialid.dat",
    dfn_vtk_path: str = "./4_rects_dfn/pflotran_graph_pressure-001.vtk",
    graph_inp_path: str = "./4_rects_graph/reduced_mesh.inp",
    outdir: str | None = None,
    make_plots: bool = True,
):
    df_full_avg = read_fracture_pressure_from_dfn(materialid_path, dfn_vtk_path)

    df_graph, df_graph_pressure = parse_graph_inp(
        graph_inp_path,
        want_fields=("imt1", "Liquid_Pressure"),
    )

    df_graph_avg = (
        df_graph_pressure
        .dropna(subset=["imt1", "Liquid_Pressure"])
        .groupby("imt1", as_index=False)["Liquid_Pressure"]
        .mean()
        .rename(columns={"imt1": "fracture_id", "Liquid_Pressure": "pressure_graph"})
        .sort_values("fracture_id")
    )

    df_cmp = (
        df_full_avg
        .merge(df_graph_avg, on="fracture_id", how="inner")
        .sort_values("fracture_id")
    )

    x = df_cmp["pressure_fullDFN"].to_numpy(dtype=float)
    y = df_cmp["pressure_graph"].to_numpy(dtype=float)

    if make_plots:
        make_pressure_plots(x, y, outdir=outdir)

    return x, y, df_cmp


if __name__ == "__main__":
    x, y, df_cmp = get_pressures(make_plots=False)
    print(f"Paired fractures: {len(x)}")
    print(df_cmp)