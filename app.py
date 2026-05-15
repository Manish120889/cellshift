"""
Cellshift — Excel Transformation Engine
Upload. Analyze. Transform. Download.
Built for Surrey businesses that waste hours in spreadsheets.
"""

import streamlit as st
import pandas as pd
import io
import re
from datetime import datetime

# ─── PAGE CONFIG ───
st.set_page_config(
    page_title="Cellshift | Smart Excel Transformations",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
.main > div { padding-top: 1rem; }
.stApp { background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%); }

/* Header */
.hero-title { font-size: 2.4rem; font-weight: 700; color: #1B2A4A;
    background: linear-gradient(135deg, #1B2A4A 0%, #2E75B6 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem; }
.hero-sub { font-size: 1.1rem; color: #64748b; margin-bottom: 1.5rem; }

/* Cards */
.transform-card {
    background: white; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 1rem 1.2rem; margin-bottom: 0.8rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04); transition: all 0.2s;
}
.transform-card:hover { border-color: #2E75B6; box-shadow: 0 4px 12px rgba(46,117,182,0.12); }
.card-title { font-weight: 600; color: #1B2A4A; font-size: 0.95rem; }
.card-desc { color: #64748b; font-size: 0.82rem; margin-top: 0.2rem; }

/* Stats */
.stat-box {
    background: linear-gradient(135deg, #1B2A4A 0%, #2E75B6 100%);
    color: white; border-radius: 10px; padding: 1rem 1.2rem;
    text-align: center;
}
.stat-num { font-size: 1.8rem; font-weight: 700; }
.stat-label { font-size: 0.75rem; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.05em; }

/* Upload area */
.upload-zone {
    border: 2px dashed #2E75B6; border-radius: 16px; padding: 2rem;
    text-align: center; background: #f0f7ff; margin: 1rem 0;
}

/* Badge */
.badge { display: inline-block; background: #E8792F; color: white; font-size: 0.7rem;
    padding: 0.15rem 0.5rem; border-radius: 20px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.04em; }
.badge-green { background: #22c55e; }
.badge-blue { background: #2E75B6; }

/* Footer */
.footer { text-align: center; padding: 2rem 0 1rem; color: #94a3b8; font-size: 0.8rem;
    border-top: 1px solid #e2e8f0; margin-top: 3rem; }
</style>
""", unsafe_allow_html=True)


# ─── HELPER FUNCTIONS ───
def analyze_dataframe(df):
    """Deep analysis of uploaded DataFrame — returns dict of findings."""
    analysis = {
        "rows": len(df),
        "cols": len(df.columns),
        "duplicates": df.duplicated().sum(),
        "blank_cells": int(df.isnull().sum().sum()),
        "blank_rows": int(df.isnull().all(axis=1).sum()),
        "blank_cols": [c for c in df.columns if df[c].isnull().all()],
        "numeric_cols": list(df.select_dtypes(include="number").columns),
        "text_cols": list(df.select_dtypes(include="object").columns),
        "date_cols": [],
        "potential_pivot_cols": [],
        "wide_format": False,
        "mixed_types": [],
        "column_types": {},
    }

    # Detect date columns
    for col in df.columns:
        sample = df[col].dropna().head(20)
        if sample.empty:
            continue
        date_count = 0
        for v in sample:
            s = str(v).strip()
            if re.search(r"\d{4}[-/]\d{1,2}[-/]\d{1,2}", s) or \
               re.search(r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}", s):
                date_count += 1
        if date_count > len(sample) * 0.5:
            analysis["date_cols"].append(col)

    # Detect wide/pivot format (many numeric columns with similar headers)
    num_cols = analysis["numeric_cols"]
    if len(num_cols) > 5 and len(num_cols) > len(df.columns) * 0.4:
        analysis["wide_format"] = True
        analysis["potential_pivot_cols"] = [c for c in df.columns if c not in num_cols]

    # Detect mixed types
    for col in analysis["text_cols"]:
        sample = df[col].dropna().head(50)
        num_like = sum(1 for v in sample if str(v).replace(".", "").replace("-", "").isdigit())
        if 0 < num_like < len(sample) and num_like > len(sample) * 0.3:
            analysis["mixed_types"].append(col)

    # Column type summary
    for col in df.columns:
        if col in analysis["date_cols"]:
            analysis["column_types"][col] = "Date"
        elif col in analysis["numeric_cols"]:
            analysis["column_types"][col] = "Numeric"
        else:
            analysis["column_types"][col] = "Text"

    return analysis


def transform_remove_duplicates(df, subset_cols=None):
    if subset_cols:
        return df.drop_duplicates(subset=subset_cols)
    return df.drop_duplicates()


def transform_remove_blanks(df, mode="rows"):
    if mode == "rows":
        return df.dropna(how="all")
    elif mode == "blank_columns":
        return df.dropna(axis=1, how="all")
    else:
        return df.fillna("")


def transform_unpivot(df, id_cols, value_cols):
    return pd.melt(df, id_vars=id_cols, value_vars=value_cols,
                   var_name="Attribute", value_name="Value")


def transform_pivot(df, index_col, columns_col, values_col, agg_func="sum"):
    agg_map = {"sum": "sum", "mean": "mean", "count": "count", "max": "max", "min": "min"}
    return pd.pivot_table(df, index=index_col, columns=columns_col,
                          values=values_col, aggfunc=agg_map.get(agg_func, "sum")).reset_index()


def transform_standardize_dates(df, date_cols, target_format="%Y-%m-%d"):
    result = df.copy()
    for col in date_cols:
        result[col] = pd.to_datetime(result[col], errors="coerce", dayfirst=False).dt.strftime(target_format)
    return result


def transform_split_column(df, col, delimiter=","):
    result = df.copy()
    split_df = result[col].astype(str).str.split(delimiter, expand=True)
    for i, new_col in enumerate(split_df.columns):
        result[f"{col}_part{i+1}"] = split_df[new_col].str.strip()
    return result


def transform_fix_types(df, cols):
    result = df.copy()
    for col in cols:
        result[col] = pd.to_numeric(result[col], errors="coerce")
    return result


def transform_conditional_flag(df, col, operator, value):
    result = df.copy()
    try:
        val = float(value)
        if operator == ">":
            result["FLAG"] = result[col].apply(lambda x: "FLAGGED" if pd.to_numeric(x, errors="coerce") is not None and float(x) > val else "")
        elif operator == "<":
            result["FLAG"] = result[col].apply(lambda x: "FLAGGED" if pd.to_numeric(x, errors="coerce") is not None and float(x) < val else "")
        elif operator == "=":
            result["FLAG"] = result[col].apply(lambda x: "FLAGGED" if str(x).strip() == str(value).strip() else "")
    except (ValueError, TypeError):
        result["FLAG"] = result[col].apply(lambda x: "FLAGGED" if str(x).strip() == str(value).strip() else "")
    return result


def transform_vlookup(df_main, df_lookup, main_key, lookup_key, merge_cols):
    subset = df_lookup[[lookup_key] + merge_cols].copy()
    return df_main.merge(subset, left_on=main_key, right_on=lookup_key, how="left", suffixes=("", "_lookup"))


def create_audit_log(original_df, transformed_df, transforms_applied):
    log_data = {
        "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] * len(transforms_applied),
        "Transformation": transforms_applied,
        "Original Rows": [len(original_df)] * len(transforms_applied),
        "Result Rows": [len(transformed_df)] * len(transforms_applied),
        "Rows Changed": [abs(len(original_df) - len(transformed_df))] * len(transforms_applied),
    }
    return pd.DataFrame(log_data)


def to_excel_download(df, audit_df=None):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Transformed", index=False)
        if audit_df is not None and not audit_df.empty:
            audit_df.to_excel(writer, sheet_name="Audit Log", index=False)
    return output.getvalue()


# ─── MAIN APP ───
def main():
    # Header
    st.markdown('<p class="hero-title">Cellshift</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-sub">Upload your Excel file. Get intelligent transformations in 60 seconds. No coding required.</p>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("### Cellshift")
        st.markdown('<span class="badge badge-green">FREE BETA</span>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("**How it works:**")
        st.markdown("1. Upload your Excel/CSV file")
        st.markdown("2. Review auto-analysis")
        st.markdown("3. Toggle transformations")
        st.markdown("4. Preview & download")
        st.markdown("---")
        st.markdown("**Supported formats:**")
        st.markdown("`.xlsx` `.xls` `.csv`")
        st.markdown("---")
        st.markdown("**Built for Surrey businesses**")
        st.markdown("Construction • Retail • Services • Healthcare")
        st.markdown("---")
        st.caption("Cellshift v1.0 | Beta")

    # File Upload
    st.markdown('<div class="upload-zone">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Drop your Excel or CSV file here",
        type=["xlsx", "xls", "csv"],
        help="Maximum 50MB. Your data stays private — nothing is stored on our servers."
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Optional: second file for VLOOKUP
    vlookup_file = None

    if uploaded_file is None:
        # Show feature cards when no file uploaded
        st.markdown("---")
        st.markdown("### What Cellshift Can Do")
        cols = st.columns(3)
        features = [
            ("Remove Duplicates", "Detect and eliminate duplicate rows instantly"),
            ("Unpivot Data", "Convert wide allocation matrices to clean long format"),
            ("Pivot & Aggregate", "Group data by any column with sum, avg, count"),
            ("Clean Blanks", "Remove empty rows/columns or fill with smart defaults"),
            ("Standardize Dates", "Normalize mixed date formats across systems"),
            ("Split Columns", "Break combined fields into separate clean columns"),
            ("VLOOKUP Merge", "Match and merge data from two files by key column"),
            ("Fix Data Types", "Convert text-numbers to proper numeric format"),
            ("Conditional Flags", "Flag rows matching your custom business rules"),
        ]
        for i, (title, desc) in enumerate(features):
            with cols[i % 3]:
                st.markdown(f"""<div class="transform-card">
                    <div class="card-title">{title}</div>
                    <div class="card-desc">{desc}</div>
                </div>""", unsafe_allow_html=True)
        return

    # ─── LOAD DATA ───
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file, engine="openpyxl")
    except Exception:
        try:
            uploaded_file.seek(0)
            df = pd.read_excel(uploaded_file, engine="xlrd")
        except Exception as e:
            st.error(f"Could not read file: {e}")
            return

    original_df = df.copy()
    transforms_applied = []

    # ─── AUTO ANALYSIS ───
    analysis = analyze_dataframe(df)

    st.markdown("---")
    st.markdown("### File Analysis")

    # Stats row
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{analysis["rows"]:,}</div><div class="stat-label">Rows</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{analysis["cols"]}</div><div class="stat-label">Columns</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{analysis["duplicates"]:,}</div><div class="stat-label">Duplicates</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{analysis["blank_cells"]:,}</div><div class="stat-label">Blank Cells</div></div>', unsafe_allow_html=True)
    with c5:
        pct = round((analysis["blank_cells"] / max(1, analysis["rows"] * analysis["cols"])) * 100, 1)
        st.markdown(f'<div class="stat-box"><div class="stat-num">{pct}%</div><div class="stat-label">Data Quality</div></div>', unsafe_allow_html=True)

    # Smart recommendations
    st.markdown("#### Smart Recommendations")
    recs = []
    if analysis["duplicates"] > 0:
        recs.append(f"Found **{analysis['duplicates']} duplicate rows** — consider removing them")
    if analysis["blank_rows"] > 0:
        recs.append(f"Found **{analysis['blank_rows']} completely blank rows** — clean them up")
    if analysis["blank_cols"]:
        recs.append(f"Found **{len(analysis['blank_cols'])} empty columns**: {', '.join(str(c) for c in analysis['blank_cols'][:5])}")
    if analysis["wide_format"]:
        recs.append("Data appears to be in **wide/matrix format** — unpivoting may help")
    if analysis["date_cols"]:
        recs.append(f"Detected **date columns**: {', '.join(str(c) for c in analysis['date_cols'][:5])} — standardize formats")
    if analysis["mixed_types"]:
        recs.append(f"**Mixed data types** in: {', '.join(str(c) for c in analysis['mixed_types'][:5])} — fix for accurate calculations")
    if not recs:
        recs.append("Your data looks clean! Select any transformation below to enhance it further.")

    for rec in recs:
        st.markdown(f"- {rec}")

    # ─── TRANSFORMATIONS ───
    st.markdown("---")
    st.markdown("### Select Transformations")

    # 1. Remove Duplicates
    with st.expander("Remove Duplicates" + (f" — {analysis['duplicates']} found" if analysis['duplicates'] > 0 else ""), expanded=analysis["duplicates"] > 0):
        do_dedup = st.checkbox("Remove duplicate rows", key="dedup")
        dedup_cols = st.multiselect("Check duplicates based on columns (leave empty for all):",
                                     df.columns.tolist(), key="dedup_cols")
        if do_dedup:
            df = transform_remove_duplicates(df, dedup_cols if dedup_cols else None)
            transforms_applied.append(f"Removed duplicates (cols: {dedup_cols or 'all'})")

    # 2. Clean Blanks
    with st.expander("Clean Blanks" + (f" — {analysis['blank_cells']} blank cells" if analysis['blank_cells'] > 0 else "")):
        blank_mode = st.radio("How to handle blanks:", ["Remove blank rows", "Remove blank columns", "Fill blanks with empty string"], key="blank_mode")
        do_blanks = st.checkbox("Apply blank cleaning", key="blanks")
        if do_blanks:
            mode_map = {"Remove blank rows": "rows", "Remove blank columns": "blank_columns", "Fill blanks with empty string": "fill"}
            df = transform_remove_blanks(df, mode_map[blank_mode])
            transforms_applied.append(f"Cleaned blanks ({blank_mode})")

    # 3. Unpivot
    if analysis["wide_format"] or len(df.columns) > 4:
        with st.expander("Unpivot / Melt" + (" — Wide format detected" if analysis["wide_format"] else "")):
            id_cols = st.multiselect("ID columns (keep fixed):", df.columns.tolist(),
                                      default=analysis["potential_pivot_cols"][:3] if analysis["potential_pivot_cols"] else [], key="unpivot_id")
            value_cols = st.multiselect("Value columns (to unpivot):", df.columns.tolist(),
                                         default=analysis["numeric_cols"][:10] if analysis["wide_format"] else [], key="unpivot_val")
            do_unpivot = st.checkbox("Apply unpivot", key="unpivot")
            if do_unpivot and id_cols and value_cols:
                df = transform_unpivot(df, id_cols, value_cols)
                transforms_applied.append(f"Unpivoted (IDs: {id_cols}, Values: {len(value_cols)} cols)")

    # 4. Pivot
    with st.expander("Pivot / Aggregate"):
        if len(df.columns) >= 3:
            pivot_idx = st.selectbox("Group by (rows):", df.columns.tolist(), key="pivot_idx")
            pivot_col = st.selectbox("Spread across (columns):", df.columns.tolist(), index=min(1, len(df.columns)-1), key="pivot_col")
            num_cols_available = df.select_dtypes(include="number").columns.tolist()
            if num_cols_available:
                pivot_val = st.selectbox("Values:", num_cols_available, key="pivot_val")
                pivot_agg = st.selectbox("Aggregation:", ["sum", "mean", "count", "max", "min"], key="pivot_agg")
                do_pivot = st.checkbox("Apply pivot", key="pivot")
                if do_pivot:
                    try:
                        df = transform_pivot(df, pivot_idx, pivot_col, pivot_val, pivot_agg)
                        transforms_applied.append(f"Pivoted ({pivot_idx} x {pivot_col}, {pivot_agg} of {pivot_val})")
                    except Exception as e:
                        st.warning(f"Pivot failed: {e}")
            else:
                st.info("No numeric columns available for pivot values")

    # 5. Standardize Dates
    if analysis["date_cols"]:
        with st.expander(f"Standardize Dates — {len(analysis['date_cols'])} date columns detected"):
            sel_date_cols = st.multiselect("Columns to standardize:", analysis["date_cols"],
                                            default=analysis["date_cols"], key="date_cols")
            date_fmt = st.selectbox("Target format:", ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%d-%b-%Y"], key="date_fmt")
            do_dates = st.checkbox("Apply date standardization", key="dates")
            if do_dates and sel_date_cols:
                df = transform_standardize_dates(df, sel_date_cols, date_fmt)
                transforms_applied.append(f"Standardized dates ({', '.join(str(c) for c in sel_date_cols)} -> {date_fmt})")

    # 6. Split Column
    with st.expander("Split Column"):
        split_col = st.selectbox("Column to split:", df.columns.tolist(), key="split_col")
        split_delim = st.text_input("Delimiter:", value=",", key="split_delim")
        do_split = st.checkbox("Apply split", key="split")
        if do_split:
            df = transform_split_column(df, split_col, split_delim)
            transforms_applied.append(f"Split column '{split_col}' by '{split_delim}'")

    # 7. Fix Data Types
    if analysis["mixed_types"]:
        with st.expander(f"Fix Data Types — {len(analysis['mixed_types'])} columns with mixed types"):
            fix_cols = st.multiselect("Convert to numeric:", analysis["mixed_types"],
                                       default=analysis["mixed_types"], key="fix_cols")
            do_fix = st.checkbox("Apply type fix", key="fix_types")
            if do_fix and fix_cols:
                df = transform_fix_types(df, fix_cols)
                transforms_applied.append(f"Fixed types ({', '.join(str(c) for c in fix_cols)})")

    # 8. Conditional Flagging
    with st.expander("Conditional Flagging"):
        flag_col = st.selectbox("Column to check:", df.columns.tolist(), key="flag_col")
        flag_op = st.selectbox("Operator:", [">", "<", "="], key="flag_op")
        flag_val = st.text_input("Value:", key="flag_val")
        do_flag = st.checkbox("Apply flagging", key="flag")
        if do_flag and flag_val:
            df = transform_conditional_flag(df, flag_col, flag_op, flag_val)
            transforms_applied.append(f"Flagged: {flag_col} {flag_op} {flag_val}")

    # 9. VLOOKUP Merge
    with st.expander("VLOOKUP Merge (upload second file)"):
        vlookup_file = st.file_uploader("Upload lookup file:", type=["xlsx", "xls", "csv"], key="vlookup")
        if vlookup_file:
            try:
                if vlookup_file.name.endswith(".csv"):
                    df_lookup = pd.read_csv(vlookup_file)
                else:
                    df_lookup = pd.read_excel(vlookup_file)
                main_key = st.selectbox("Match column (your data):", df.columns.tolist(), key="vl_main")
                lookup_key = st.selectbox("Match column (lookup file):", df_lookup.columns.tolist(), key="vl_lookup")
                merge_cols = st.multiselect("Columns to bring in:", [c for c in df_lookup.columns if c != lookup_key], key="vl_merge")
                do_vlookup = st.checkbox("Apply VLOOKUP merge", key="vlookup_go")
                if do_vlookup and merge_cols:
                    df = transform_vlookup(df, df_lookup, main_key, lookup_key, merge_cols)
                    transforms_applied.append(f"VLOOKUP merge on '{main_key}' <- '{lookup_key}'")
            except Exception as e:
                st.warning(f"Could not read lookup file: {e}")

    # ─── PREVIEW & DOWNLOAD ───
    st.markdown("---")
    if transforms_applied:
        st.markdown("### Transformations Applied")
        for i, t in enumerate(transforms_applied, 1):
            st.markdown(f"**{i}.** {t}")

        col_before, col_after = st.columns(2)
        with col_before:
            st.markdown(f"**Before** ({len(original_df):,} rows)")
            st.dataframe(original_df.head(20), use_container_width=True, height=300)
        with col_after:
            st.markdown(f"**After** ({len(df):,} rows)")
            st.dataframe(df.head(20), use_container_width=True, height=300)

        # Audit log
        audit_df = create_audit_log(original_df, df, transforms_applied)

        # Download
        st.markdown("---")
        excel_data = to_excel_download(df, audit_df)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="Download Transformed Excel",
            data=excel_data,
            file_name=f"cellshift_output_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )
    else:
        st.markdown("### Data Preview")
        st.dataframe(df.head(50), use_container_width=True, height=400)
        st.info("Select transformations above to see before/after comparison")

    # Footer
    st.markdown("""<div class="footer">
        Cellshift &copy; 2026 | Built for Surrey Businesses<br>
        Your data stays private — nothing is stored on our servers
    </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
