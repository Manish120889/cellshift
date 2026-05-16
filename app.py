"""
Cellshift — AI-Native Business Automation Platform
Production v2.0 — Real integrations, real persistence, real exports.
Built for Surrey, BC small businesses. Zero-investment infrastructure.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io, re, json, hashlib, smtplib, base64, os
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from fpdf import FPDF
import calendar

# ─── PAGE CONFIG ───
st.set_page_config(
    page_title="Cellshift | AI Business Automation",
    page_icon="⚡", layout="wide", initial_sidebar_state="expanded"
)

# ─── PERSISTENCE ───
DATA_DIR = os.path.join(os.path.dirname(__file__), ".cellshift_data")
os.makedirs(DATA_DIR, exist_ok=True)

def save_json(name, data):
    with open(os.path.join(DATA_DIR, f"{name}.json"), "w") as f:
        json.dump(data, f, indent=2, default=str)

def load_json(name, default=None):
    p = os.path.join(DATA_DIR, f"{name}.json")
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return default if default is not None else {}

# ─── TIER LIMITS ───
TIER_LIMITS = {
    "Free": {"actions_per_day": 15, "max_file_mb": 10, "batch": False, "templates": 3, "modules": ["Transform", "Dashboard"]},
    "Pro": {"actions_per_day": 999, "max_file_mb": 50, "batch": True, "templates": 50, "modules": "all"},
    "Business": {"actions_per_day": 999, "max_file_mb": 200, "batch": True, "templates": 999, "modules": "all"},
}

# ─── SURREY BUSINESS DATA ───
SURREY_INDUSTRIES = {
    "Construction": {"gst_rate": 0.05, "wcb_rate": 0.0312, "permits": ["Business License", "Building Permit", "Electrical Permit", "Plumbing Permit"],
        "risks": ["WorkSafeBC audits", "Permit delays", "Lien claims"], "avg_revenue": "$500K-$2M"},
    "Retail": {"gst_rate": 0.05, "pst_rate": 0.07, "permits": ["Business License", "Signage Permit", "Food Handling (if applicable)"],
        "risks": ["Inventory shrinkage", "PST audit", "Lease renewal"], "avg_revenue": "$200K-$800K"},
    "Healthcare": {"gst_rate": 0.05, "permits": ["Business License", "Health Authority Registration", "Professional Licensing"],
        "risks": ["Licensing renewal", "PHIPA compliance", "Insurance gaps"], "avg_revenue": "$300K-$1.5M"},
    "Food & Restaurant": {"gst_rate": 0.05, "pst_rate": 0.10, "permits": ["Business License", "Food Premises Permit", "Liquor License (if applicable)", "Fraser Health Inspection"],
        "risks": ["Health inspection failure", "Staff turnover", "Food cost inflation"], "avg_revenue": "$300K-$1M"},
    "Professional Services": {"gst_rate": 0.05, "permits": ["Business License", "Professional Designation"],
        "risks": ["E&O claims", "Scope creep", "AR aging"], "avg_revenue": "$150K-$500K"},
    "Real Estate": {"gst_rate": 0.05, "permits": ["Business License", "BCFSA Registration", "FINTRAC Registration"],
        "risks": ["Market downturn", "FINTRAC audit", "Commission disputes"], "avg_revenue": "$200K-$2M"},
    "Transportation": {"gst_rate": 0.05, "permits": ["Business License", "NSC Safety Certificate", "CVSE Operating Authority"],
        "risks": ["Fuel cost spikes", "Driver shortages", "CVSE audit"], "avg_revenue": "$300K-$1.5M"},
    "Technology": {"gst_rate": 0.05, "permits": ["Business License", "SR&ED Eligibility (optional)"],
        "risks": ["Client concentration", "IP disputes", "Talent retention"], "avg_revenue": "$100K-$1M"},
}

# ─── CSS ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
:root {
    --bg-primary: #0d1117; --bg-secondary: #161b22; --bg-tertiary: #1c2333;
    --border: #21262d; --text-primary: #e6edf3; --text-secondary: #8b949e;
    --accent-blue: #58a6ff; --accent-purple: #7c3aed; --accent-pink: #f472b6;
    --accent-green: #4ade80; --accent-orange: #fb923c; --accent-red: #f87171;
}
* { font-family: 'Inter', sans-serif; }
.main > div { padding-top: 0.3rem; }
.stApp { background: var(--bg-primary); }
section[data-testid="stSidebar"] { background: var(--bg-secondary) !important; border-right: 1px solid var(--border); }
div[data-testid="stExpander"] { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
.stTabs [data-baseweb="tab-list"] { gap: 0; background: var(--bg-secondary); border-radius: 10px; padding: 4px; }
.stTabs [data-baseweb="tab"] { background: transparent; color: var(--text-secondary); border-radius: 8px; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #2E75B6, #7c3aed) !important; color: white !important; }
.hero-title { font-size: 2.6rem; font-weight: 800; letter-spacing: -0.04em;
    background: linear-gradient(135deg, #58a6ff 0%, #7c3aed 50%, #f472b6 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0; line-height: 1.1; }
.hero-sub { font-size: 1.1rem; color: var(--text-secondary); margin-bottom: 1rem; font-weight: 300; }
.hero-tagline { font-size: 0.85rem; color: var(--accent-blue); font-weight: 500;
    background: rgba(88,166,255,0.08); border: 1px solid rgba(88,166,255,0.15);
    display: inline-block; padding: 0.3rem 0.8rem; border-radius: 20px; margin-bottom: 0.8rem; }
.card { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 14px;
    padding: 1.3rem; margin-bottom: 1rem; transition: all 0.3s cubic-bezier(0.4,0,0.2,1); }
.card:hover { border-color: var(--accent-blue); transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(88,166,255,0.1); }
.card-sm { padding: 1rem; margin-bottom: 0.6rem; }
.card-glow { border-color: var(--accent-purple); box-shadow: 0 0 20px rgba(124,58,237,0.15); }
.card h4 { color: var(--text-primary); margin: 0 0 0.3rem 0; font-size: 1rem; }
.card p { color: var(--text-secondary); margin: 0; font-size: 0.85rem; line-height: 1.5; }
.stat-box { background: var(--bg-secondary); border: 1px solid var(--border);
    border-radius: 12px; padding: 1rem; text-align: center; }
.stat-num { font-size: 1.8rem; font-weight: 700;
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.stat-label { font-size: 0.7rem; color: var(--text-secondary); text-transform: uppercase;
    letter-spacing: 0.08em; margin-top: 0.3rem; }
.badge { display: inline-block; font-size: 0.68rem; padding: 0.2rem 0.6rem;
    border-radius: 20px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }
.badge-free { background: rgba(34,197,94,0.12); color: var(--accent-green); border: 1px solid rgba(34,197,94,0.25); }
.badge-pro { background: rgba(124,58,237,0.12); color: #a78bfa; border: 1px solid rgba(124,58,237,0.25); }
.badge-biz { background: rgba(88,166,255,0.12); color: var(--accent-blue); border: 1px solid rgba(88,166,255,0.25); }
.module-card { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 14px;
    padding: 1.5rem; text-align: center; cursor: pointer; transition: all 0.3s; min-height: 140px; }
.module-card:hover { border-color: var(--accent-blue); transform: translateY(-3px);
    box-shadow: 0 12px 35px rgba(88,166,255,0.12); }
.module-icon { font-size: 2.2rem; margin-bottom: 0.6rem; }
.module-name { font-weight: 600; color: var(--text-primary); font-size: 0.95rem; }
.module-desc { color: var(--text-secondary); font-size: 0.78rem; margin-top: 0.3rem; }
.pip-step { padding: 0.35rem 0.8rem; border-radius: 20px; font-size: 0.75rem; font-weight: 500; display: inline-block; margin: 0.2rem; }
.pip-done { background: rgba(34,197,94,0.12); color: var(--accent-green); border: 1px solid rgba(34,197,94,0.2); }
.invoice-box { background: #ffffff; color: #333; border-radius: 12px; padding: 2rem; margin: 1rem 0; }
.invoice-table { width: 100%; border-collapse: collapse; }
.invoice-table th { text-align: left; padding: 0.5rem; border-bottom: 1px solid #e2e8f0; font-size: 0.85rem; }
.invoice-table td { padding: 0.5rem; border-bottom: 1px solid #f1f5f9; font-size: 0.85rem; }
.footer { text-align: center; padding: 1.5rem 0 1rem; color: #484f58; font-size: 0.78rem;
    border-top: 1px solid var(--border); margin-top: 2rem; }
.footer a { color: var(--accent-blue); text-decoration: none; }
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2E75B6, #7c3aed) !important;
    border: none !important; border-radius: 10px !important; font-weight: 600 !important; }
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important; box-shadow: 0 6px 20px rgba(88,166,255,0.3) !important; }
.stDownloadButton > button {
    background: var(--bg-secondary) !important; border: 1px solid var(--border) !important;
    border-radius: 10px !important; color: var(--text-primary) !important; }
.stDownloadButton > button:hover { border-color: var(--accent-blue) !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# SESSION STATE + PERSISTENCE
# ══════════════════════════════════════════════════════════
def init_session():
    defaults = {
        "authenticated": False, "user": None, "user_tier": "Free",
        "page": "Home", "action_count_today": 0,
        "action_date": datetime.now().strftime("%Y-%m-%d"),
        "history": [], "templates": {},
        "users_db": load_json("users_db", {}),
        "invoices": load_json("invoices", []),
        "compliance_items": load_json("compliance_items", []),
        "feedback": [],
        "admin_stats": load_json("admin_stats", {"total_signups": 0, "total_actions": 0, "files_processed": 0, "active_users": []}),
        "smtp_config": load_json("smtp_config", {"host": "", "port": 587, "email": "", "password": "", "configured": False}),
        "transform_history": load_json("transform_history", []),
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    if st.session_state.action_date != datetime.now().strftime("%Y-%m-%d"):
        st.session_state.action_count_today = 0
        st.session_state.action_date = datetime.now().strftime("%Y-%m-%d")

init_session()

def persist():
    """Save critical state to disk for cross-session persistence."""
    save_json("users_db", st.session_state.users_db)
    save_json("invoices", st.session_state.invoices)
    save_json("compliance_items", st.session_state.compliance_items)
    save_json("admin_stats", st.session_state.admin_stats)
    save_json("smtp_config", st.session_state.smtp_config)
    save_json("transform_history", st.session_state.transform_history)

def track_action(name):
    st.session_state.action_count_today += 1
    st.session_state.admin_stats["total_actions"] += 1
    entry = {"time": datetime.now().strftime("%H:%M:%S"), "date": datetime.now().strftime("%Y-%m-%d"),
             "action": name, "user": st.session_state.user.get("email", "guest") if st.session_state.user else "guest"}
    st.session_state.history.append(entry)
    st.session_state.transform_history.append(entry)
    if len(st.session_state.transform_history) > 500:
        st.session_state.transform_history = st.session_state.transform_history[-500:]
    persist()


# ══════════════════════════════════════════════════════════
# AUTH (persistent)
# ══════════════════════════════════════════════════════════
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def register_user(email, pw, name, company="", industry=""):
    if email in st.session_state.users_db:
        return False, "Email already registered"
    st.session_state.users_db[email] = {
        "password": hash_pw(pw), "name": name, "company": company,
        "industry": industry, "tier": "Free", "created": datetime.now().isoformat(),
    }
    st.session_state.admin_stats["total_signups"] += 1
    persist()
    return True, "Account created"

def login_user(email, pw):
    user = st.session_state.users_db.get(email)
    if user and user["password"] == hash_pw(pw):
        st.session_state.authenticated = True
        st.session_state.user = {"email": email, "name": user["name"], "company": user["company"], "industry": user.get("industry", "")}
        st.session_state.user_tier = user["tier"]
        if email not in st.session_state.admin_stats.get("active_users", []):
            if not isinstance(st.session_state.admin_stats.get("active_users"), list):
                st.session_state.admin_stats["active_users"] = []
            st.session_state.admin_stats["active_users"].append(email)
        persist()
        return True
    return False

def show_auth():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="hero-tagline">AI-Powered Business Automation for Surrey, BC</div>', unsafe_allow_html=True)
        st.markdown('<p class="hero-title">Cellshift</p>', unsafe_allow_html=True)
        st.markdown('<p class="hero-sub">Stop wrestling with spreadsheets, invoices, and compliance.<br>Let AI handle it in 60 seconds.</p>', unsafe_allow_html=True)
        tab_login, tab_register = st.tabs(["Log In", "Create Account"])
        with tab_login:
            with st.form("login"):
                email = st.text_input("Email", placeholder="you@company.com")
                pw = st.text_input("Password", type="password")
                if st.form_submit_button("Log In", use_container_width=True, type="primary"):
                    if email and pw:
                        if login_user(email, pw): st.rerun()
                        else: st.error("Invalid credentials")
            st.markdown("---")
            if st.button("Try Free — No Account Needed", use_container_width=True):
                st.session_state.authenticated = True
                st.session_state.user = {"email": "guest@cellshift.ca", "name": "Guest", "company": "", "industry": ""}
                st.session_state.user_tier = "Free"
                st.rerun()
        with tab_register:
            with st.form("register"):
                name = st.text_input("Full Name")
                company = st.text_input("Company Name")
                industry = st.selectbox("Industry", list(SURREY_INDUSTRIES.keys()))
                reg_email = st.text_input("Email", key="re")
                reg_pw = st.text_input("Password (6+ chars)", type="password", key="rp")
                reg_pw2 = st.text_input("Confirm Password", type="password", key="rp2")
                agree = st.checkbox("I agree to Terms of Service and Privacy Policy")
                if st.form_submit_button("Create Free Account", use_container_width=True, type="primary"):
                    if not all([name, reg_email, reg_pw]): st.warning("Fill all fields")
                    elif len(reg_pw) < 6: st.warning("Password too short")
                    elif reg_pw != reg_pw2: st.error("Passwords don't match")
                    elif not agree: st.warning("Accept terms to continue")
                    else:
                        ok, msg = register_user(reg_email, reg_pw, name, company, industry)
                        if ok: login_user(reg_email, reg_pw); st.rerun()
                        else: st.error(msg)


# ══════════════════════════════════════════════════════════
# ANALYSIS ENGINE
# ══════════════════════════════════════════════════════════
def analyze_df(df):
    a = {"rows": len(df), "cols": len(df.columns), "duplicates": int(df.duplicated().sum()),
         "blank_cells": int(df.isnull().sum().sum()), "blank_rows": int(df.isnull().all(axis=1).sum()),
         "numeric_cols": list(df.select_dtypes(include="number").columns),
         "text_cols": list(df.select_dtypes(include="object").columns),
         "date_cols": [], "mixed_types": [], "wide_format": False,
         "memory_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)}
    for col in df.columns:
        sample = df[col].dropna().head(20)
        if sample.empty: continue
        dc = sum(1 for v in sample if re.search(r"\d{4}[-/]\d{1,2}[-/]\d{1,2}|[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4}", str(v)))
        if dc > len(sample) * 0.5: a["date_cols"].append(col)
    for col in a["text_cols"]:
        sample = df[col].dropna().head(50)
        nl = sum(1 for v in sample if str(v).replace(".", "").replace("-", "").isdigit())
        if 0 < nl < len(sample) and nl > len(sample) * 0.3: a["mixed_types"].append(col)
    if len(a["numeric_cols"]) > 5 and len(a["numeric_cols"]) > len(df.columns) * 0.4: a["wide_format"] = True
    return a


# ══════════════════════════════════════════════════════════
# AUTO-TRANSFORM ENGINE
# ══════════════════════════════════════════════════════════
def auto_transform(df, analysis):
    result = df.copy(); actions = []
    b = len(result); result = result.dropna(how="all")
    if len(result) < b: actions.append(f"Removed {b - len(result)} blank rows")
    bc = [c for c in result.columns if result[c].isnull().all()]
    if bc: result = result.drop(columns=bc); actions.append(f"Removed {len(bc)} empty columns")
    b = len(result); result = result.drop_duplicates()
    if len(result) < b: actions.append(f"Removed {b - len(result)} duplicate rows")
    for col in result.select_dtypes(include="object").columns:
        result[col] = result[col].astype(str).str.strip().replace("nan", np.nan)
    actions.append("Trimmed whitespace from all text columns")
    for col in analysis.get("date_cols", []):
        try:
            p = pd.to_datetime(result[col], errors="coerce", dayfirst=False)
            m = p.isna() & result[col].notna()
            if m.any(): p[m] = pd.to_datetime(result[col][m], errors="coerce", dayfirst=True)
            if p.notna().sum() > 0:
                result[col] = p.dt.strftime("%Y-%m-%d")
                actions.append(f"Standardized dates in '{col}'")
        except: pass
    for col in analysis.get("mixed_types", []):
        try: result[col] = pd.to_numeric(result[col], errors="coerce"); actions.append(f"Fixed data type: '{col}' -> numeric")
        except: pass
    # Standardize column names
    old_cols = result.columns.tolist()
    result.columns = [re.sub(r'[^\w\s]', '', str(c)).strip().replace(' ', '_') for c in result.columns]
    if result.columns.tolist() != old_cols: actions.append("Standardized column names")
    if not actions: actions.append("Data already clean")
    return result, actions


# ══════════════════════════════════════════════════════════
# CORE TRANSFORMS
# ══════════════════════════════════════════════════════════
def t_dedup(df, cols=None): return df.drop_duplicates(subset=cols) if cols else df.drop_duplicates()
def t_blanks(df, mode="rows"):
    if mode == "rows": return df.dropna(how="all")
    elif mode == "any": return df.dropna(how="any")
    elif mode == "cols": return df.dropna(axis=1, how="all")
    return df.fillna("")
def t_unpivot(df, ids, vals): return pd.melt(df, id_vars=ids, value_vars=vals, var_name="Attribute", value_name="Value")
def t_pivot(df, idx, col, val, agg="sum"): return pd.pivot_table(df, index=idx, columns=col, values=val, aggfunc=agg).reset_index()
def t_dates(df, cols, fmt="%Y-%m-%d"):
    r = df.copy()
    for c in cols:
        p = pd.to_datetime(r[c], errors="coerce", dayfirst=False)
        m = p.isna() & r[c].notna()
        if m.any(): p[m] = pd.to_datetime(r[c][m], errors="coerce", dayfirst=True)
        r[c] = p.dt.strftime(fmt)
    return r
def t_split(df, col, delim=","): 
    r = df.copy(); s = r[col].astype(str).str.split(delim, expand=True)
    for i, c in enumerate(s.columns): r[f"{col}_part{i+1}"] = s[c].str.strip()
    return r
def t_fix_types(df, cols):
    r = df.copy()
    for c in cols: r[c] = pd.to_numeric(r[c], errors="coerce")
    return r
def t_flag(df, col, op, val, label="FLAGGED"):
    r = df.copy()
    try:
        v = float(val); nc = pd.to_numeric(r[col], errors="coerce")
        ops = {">": nc > v, "<": nc < v, ">=": nc >= v, "<=": nc <= v, "=": nc == v, "!=": nc != v}
        r["FLAG"] = np.where(ops.get(op, nc == v), label, "")
    except: r["FLAG"] = np.where(r[col].astype(str).str.strip() == str(val).strip(), label, "")
    return r
def t_vlookup(main, lookup, mk, lk, cols):
    sub = lookup[[lk] + cols].drop_duplicates(subset=[lk])
    return main.merge(sub, left_on=mk, right_on=lk, how="left", suffixes=("", "_lookup"))
def t_find_replace(df, col, find, replace, regex=False):
    r = df.copy(); r[col] = r[col].astype(str).str.replace(find, replace, regex=regex); return r
def t_calc(df, name, op, a, b=None):
    r = df.copy(); na = pd.to_numeric(r[a], errors="coerce")
    if op in ["add", "subtract", "multiply", "divide", "pct"] and b:
        nb = pd.to_numeric(r[b], errors="coerce")
        if op == "add": r[name] = na + nb
        elif op == "subtract": r[name] = na - nb
        elif op == "multiply": r[name] = na * nb
        elif op == "divide": r[name] = na / nb.replace(0, np.nan)
        elif op == "pct": r[name] = (na / nb.replace(0, np.nan) * 100).round(2)
    elif op == "upper": r[name] = r[a].astype(str).str.upper()
    elif op == "lower": r[name] = r[a].astype(str).str.lower()
    elif op == "trim": r[name] = r[a].astype(str).str.strip()
    elif op == "len": r[name] = r[a].astype(str).str.len()
    elif op == "round": r[name] = na.round(2)
    elif op == "abs": r[name] = na.abs()
    return r
def t_filter(df, col, op, val):
    try:
        v = float(val); nc = pd.to_numeric(df[col], errors="coerce")
        ops = {">": nc > v, "<": nc < v, ">=": nc >= v, "<=": nc <= v, "=": nc == v, "!=": nc != v}
        return df[ops.get(op, nc == v)]
    except:
        if op == "contains": return df[df[col].astype(str).str.contains(str(val), case=False, na=False)]
        elif op == "=": return df[df[col].astype(str).str.strip() == str(val).strip()]
        elif op == "!=": return df[df[col].astype(str).str.strip() != str(val).strip()]
    return df


# ══════════════════════════════════════════════════════════
# EXPORT HELPERS
# ══════════════════════════════════════════════════════════
def to_excel(df, audit=None):
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as w:
        df.to_excel(w, sheet_name="Data", index=False)
        if audit is not None and not audit.empty: audit.to_excel(w, sheet_name="Audit", index=False)
        pd.DataFrame({"Info": ["Cellshift v2.0", datetime.now().strftime("%Y-%m-%d %H:%M"), f"{len(df)} rows"]}).to_excel(w, sheet_name="Meta", index=False)
    return out.getvalue()

def to_csv(df): return df.to_csv(index=False).encode("utf-8")
def to_json_bytes(df): return df.to_json(orient="records", indent=2).encode("utf-8")

def load_file(f):
    try:
        if f.name.endswith(".csv"): return pd.read_csv(f), None
        try: return pd.read_excel(f, engine="openpyxl"), None
        except: f.seek(0); return pd.read_excel(f, engine="xlrd"), None
    except Exception as e: return None, str(e)

def import_gsheet(url):
    try:
        sid = url.split("/d/")[1].split("/")[0]
        return pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv"), None
    except Exception as e: return None, str(e)


# ══════════════════════════════════════════════════════════
# REAL PDF INVOICE GENERATOR
# ══════════════════════════════════════════════════════════
class InvoicePDF(FPDF):
    def header(self): pass
    def footer(self):
        self.set_y(-15); self.set_font("Helvetica", "I", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 10, f"Generated by Cellshift | {datetime.now().strftime('%Y-%m-%d %H:%M')}", align="C")

def generate_invoice_pdf(inv):
    pdf = InvoicePDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    # Header bar
    pdf.set_fill_color(30, 58, 95)
    pdf.rect(0, 0, 210, 45, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_xy(15, 10)
    pdf.cell(0, 10, inv["from"]["name"] or "Your Business")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_xy(15, 22)
    pdf.cell(0, 5, inv["from"]["addr"])
    if inv["from"]["gst"]:
        pdf.set_xy(15, 28); pdf.cell(0, 5, f"GST: {inv['from']['gst']}")
    if inv["from"]["pst"]:
        pdf.set_xy(15, 34); pdf.cell(0, 5, f"PST: {inv['from']['pst']}")

    # Invoice title
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_xy(130, 8)
    pdf.cell(65, 12, "INVOICE", align="R")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_xy(130, 22); pdf.cell(65, 5, f"#{inv['number']}", align="R")
    pdf.set_xy(130, 28); pdf.cell(65, 5, f"Date: {inv['date']}", align="R")
    pdf.set_xy(130, 34); pdf.cell(65, 5, f"Due: {inv['due']}", align="R")

    # Bill To
    pdf.set_text_color(50, 50, 50)
    pdf.set_xy(15, 55)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "BILL TO:")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_xy(15, 62); pdf.cell(0, 5, inv["to"]["name"])
    pdf.set_xy(15, 68); pdf.cell(0, 5, inv["to"]["company"])
    pdf.set_xy(15, 74); pdf.cell(0, 5, inv["to"]["addr"])
    pdf.set_xy(15, 80); pdf.cell(0, 5, inv["to"]["email"])

    # Terms
    pdf.set_xy(130, 55)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(65, 6, f"Terms: {inv['terms']}", align="R")

    # Line items table
    y = 95
    pdf.set_fill_color(240, 245, 250)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_xy(15, y)
    pdf.cell(90, 8, "  Description", border=1, fill=True)
    pdf.cell(25, 8, "Qty", border=1, fill=True, align="C")
    pdf.cell(30, 8, "Rate", border=1, fill=True, align="R")
    pdf.cell(30, 8, "Amount", border=1, fill=True, align="R")
    y += 8

    pdf.set_font("Helvetica", "", 9)
    for item in inv["items"]:
        if y > 250: pdf.add_page(); y = 20
        pdf.set_xy(15, y)
        pdf.cell(90, 7, f"  {item['desc'][:45]}", border="LR")
        pdf.cell(25, 7, f"{item['qty']:.0f}", border="LR", align="C")
        pdf.cell(30, 7, f"${item['rate']:,.2f}", border="LR", align="R")
        pdf.cell(30, 7, f"${item['total']:,.2f}", border="LR", align="R")
        y += 7

    # Totals
    pdf.set_xy(15, y); pdf.cell(175, 0.5, "", border="T")
    y += 5
    pdf.set_font("Helvetica", "", 10)
    pdf.set_xy(120, y); pdf.cell(40, 7, "Subtotal:", align="R"); pdf.cell(30, 7, f"${inv['subtotal']:,.2f}", align="R"); y += 7
    pdf.set_xy(120, y); pdf.cell(40, 7, "GST (5%):", align="R"); pdf.cell(30, 7, f"${inv['gst']:,.2f}", align="R"); y += 7
    if inv.get("pst", 0) > 0:
        pst_pct = inv.get("pst_rate", 0)
        pdf.set_xy(120, y); pdf.cell(40, 7, f"PST ({pst_pct}%):", align="R"); pdf.cell(30, 7, f"${inv['pst']:,.2f}", align="R"); y += 7

    # Total highlight
    pdf.set_fill_color(30, 58, 95); pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_xy(120, y + 2); pdf.cell(40, 10, "TOTAL (CAD):", align="R", fill=True); pdf.cell(30, 10, f"${inv['total']:,.2f}", align="R", fill=True)
    pdf.set_text_color(50, 50, 50)

    # Notes
    y += 22
    if y > 250: pdf.add_page(); y = 20
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_xy(15, y)
    pdf.multi_cell(175, 5, inv.get("notes", ""))

    return pdf.output()


# ══════════════════════════════════════════════════════════
# REAL SMTP EMAIL
# ══════════════════════════════════════════════════════════
def send_email(to_addr, subject, body, attachment=None, att_name=None):
    cfg = st.session_state.smtp_config
    if not cfg.get("configured"): return False, "SMTP not configured. Go to Settings > Email Configuration."
    try:
        msg = MIMEMultipart()
        msg["From"] = cfg["email"]; msg["To"] = to_addr; msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        if attachment and att_name:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment)
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={att_name}")
            msg.attach(part)
        with smtplib.SMTP(cfg["host"], int(cfg["port"])) as server:
            server.starttls()
            server.login(cfg["email"], cfg["password"])
            server.sendmail(cfg["email"], to_addr, msg.as_string())
        return True, "Email sent successfully"
    except Exception as e: return False, str(e)


# ══════════════════════════════════════════════════════════
# MODULE: HOME / DASHBOARD
# ══════════════════════════════════════════════════════════
def page_home():
    st.markdown('<div class="hero-tagline">AI-Powered Business Automation</div>', unsafe_allow_html=True)
    st.markdown('<p class="hero-title">Cellshift</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-sub">Everything your Surrey business needs to automate operations — data cleanup, invoicing, compliance, reporting — powered by AI.</p>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    stats = st.session_state.admin_stats
    with c1: st.markdown(f'<div class="stat-box"><div class="stat-num">{stats["total_actions"]}</div><div class="stat-label">Actions Run</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="stat-box"><div class="stat-num">{stats["files_processed"]}</div><div class="stat-label">Files Processed</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="stat-box"><div class="stat-num">{len(st.session_state.invoices)}</div><div class="stat-label">Invoices Created</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="stat-box"><div class="stat-num">{st.session_state.action_count_today}</div><div class="stat-label">Today\'s Actions</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Automation Modules")
    modules = [
        ("⚡", "Data Transform", "Clean, transform, and merge Excel/CSV with one-click AI automation"),
        ("📄", "Invoice Generator", "Create GST/PST invoices — export as PDF, Excel, or email directly"),
        ("📊", "Report Builder", "Auto-generate business reports with interactive Plotly charts"),
        ("✅", "Compliance Tracker", "Track Surrey permits, BC tax deadlines, and business risks"),
        ("📧", "Email Drafter", "AI-drafted emails with real SMTP sending and PDF attachments"),
        ("🤖", "AI Assistant", "Ask questions about your data in plain English — get instant answers"),
    ]
    cols = st.columns(3)
    for i, (icon, name, desc) in enumerate(modules):
        with cols[i % 3]:
            st.markdown(f'<div class="module-card"><div class="module-icon">{icon}</div><div class="module-name">{name}</div><div class="module-desc">{desc}</div></div>', unsafe_allow_html=True)

    # Activity chart
    if st.session_state.transform_history:
        st.markdown("---")
        st.markdown("### Activity Overview")
        hist_df = pd.DataFrame(st.session_state.transform_history[-100:])
        if "date" in hist_df.columns:
            daily = hist_df.groupby("date").size().reset_index(name="actions")
            fig = px.bar(daily, x="date", y="actions", title="Daily Actions",
                        color_discrete_sequence=["#58a6ff"])
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                            font_color="#8b949e", xaxis_title="", yaxis_title="Actions",
                            margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig, use_container_width=True)

    if st.session_state.history:
        st.markdown("### Recent Activity")
        for h in reversed(st.session_state.history[-5:]):
            st.markdown(f'<div class="card card-sm"><p><strong>{h["time"]}</strong> — {h["action"]}</p></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# MODULE: DATA TRANSFORM
# ══════════════════════════════════════════════════════════
def page_transform():
    st.markdown("### ⚡ Data Transform")
    st.markdown("Upload your file and let AI auto-clean it, or choose manual transformations.")

    src = st.radio("Import:", ["File Upload", "Google Sheets"], horizontal=True, label_visibility="collapsed")
    df = None
    if src == "File Upload":
        uf = st.file_uploader("Drop Excel/CSV", type=["xlsx", "xls", "csv"], accept_multiple_files=TIER_LIMITS[st.session_state.user_tier]["batch"])
        if uf:
            if isinstance(uf, list) and len(uf) > 1:
                dfs = []
                for f in uf:
                    d, e = load_file(f)
                    if d is not None: d["_source"] = f.name; dfs.append(d)
                if dfs: df = pd.concat(dfs, ignore_index=True); st.success(f"Batch: {len(dfs)} files, {len(df):,} rows")
            else:
                f = uf[0] if isinstance(uf, list) else uf
                df, e = load_file(f)
                if e: st.error(e); return
    else:
        url = st.text_input("Google Sheet URL:", placeholder="https://docs.google.com/spreadsheets/d/...")
        if url: df, e = import_gsheet(url); (st.error(e) if e else None)

    if df is None: st.info("Upload a file or paste a Google Sheets URL to get started."); return

    original = df.copy()
    st.session_state.admin_stats["files_processed"] += 1
    analysis = analyze_df(df)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    for col, num, label in [(c1, f"{analysis['rows']:,}", "Rows"), (c2, str(analysis['cols']), "Columns"),
        (c3, str(analysis['duplicates']), "Duplicates"), (c4, str(analysis['blank_cells']), "Blanks"),
        (c5, str(analysis['memory_mb']), "MB"), (c6, f"{round((1 - analysis['blank_cells'] / max(1, analysis['rows'] * analysis['cols'])) * 100)}%", "Complete")]:
        with col: st.markdown(f'<div class="stat-box"><div class="stat-num">{num}</div><div class="stat-label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""<div class="card card-glow" style="text-align:center;">
        <h4>🤖 AI Auto-Transform</h4>
        <p>One click to automatically clean, deduplicate, fix types, standardize dates, and optimize your data.</p>
    </div>""", unsafe_allow_html=True)

    if st.button("Run Auto-Transform", type="primary", use_container_width=True):
        with st.spinner("AI analyzing and transforming your data..."):
            df, actions = auto_transform(df, analysis)
            track_action("Auto-Transform")
            st.markdown("#### Auto-Transform Results")
            for a_item in actions:
                st.markdown(f'<span class="pip-step pip-done">✓ {a_item}</span>', unsafe_allow_html=True)
            st.success(f"Done! {len(original)} rows → {len(df)} rows | {len(actions)} optimizations applied")

    st.markdown("---")
    st.markdown("### Manual Transformations")
    transforms_applied = []

    with st.expander(f"Remove Duplicates ({analysis['duplicates']} found)" if analysis['duplicates'] > 0 else "Remove Duplicates"):
        dc = st.multiselect("Columns (empty=all):", df.columns.tolist(), key="dc")
        if st.checkbox("Apply", key="dd"): b = len(df); df = t_dedup(df, dc if dc else None); transforms_applied.append(f"Dedup: {b - len(df)} removed")

    with st.expander(f"Clean Blanks ({analysis['blank_cells']} cells)"):
        bm = st.radio("Mode:", ["Remove blank rows", "Remove any incomplete rows", "Remove blank columns", "Fill with empty"], key="bm")
        if st.checkbox("Apply", key="db"):
            mm = {"Remove blank rows": "rows", "Remove any incomplete rows": "any", "Remove blank columns": "cols", "Fill with empty": "fill"}
            df = t_blanks(df, mm[bm]); transforms_applied.append(f"Blanks: {bm}")

    if analysis["date_cols"]:
        with st.expander(f"Standardize Dates ({len(analysis['date_cols'])} columns)"):
            sdc = st.multiselect("Columns:", analysis["date_cols"], default=analysis["date_cols"], key="sdc")
            fmt = st.selectbox("Format:", ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%d-%b-%Y"], key="dfmt")
            if st.checkbox("Apply", key="sd") and sdc: df = t_dates(df, sdc, fmt); transforms_applied.append(f"Dates -> {fmt}")

    with st.expander("Split Column"):
        sc = st.selectbox("Column:", df.columns.tolist(), key="sc"); sd = st.text_input("Delimiter:", ",", key="sdl")
        if st.checkbox("Apply", key="ds"): df = t_split(df, sc, sd); transforms_applied.append(f"Split '{sc}'")

    with st.expander("Conditional Flag"):
        fc = st.selectbox("Column:", df.columns.tolist(), key="fc"); fo = st.selectbox("Op:", [">", "<", ">=", "<=", "=", "!="], key="fo")
        fv = st.text_input("Value:", key="fv"); fl = st.text_input("Label:", "FLAGGED", key="fl")
        if st.checkbox("Apply", key="df") and fv: df = t_flag(df, fc, fo, fv, fl); transforms_applied.append(f"Flag: {fc} {fo} {fv}")

    with st.expander("Find & Replace"):
        frc = st.selectbox("Column:", df.columns.tolist(), key="frc"); frf = st.text_input("Find:", key="frf")
        frr = st.text_input("Replace:", key="frr"); frx = st.checkbox("Regex", key="frx")
        if st.checkbox("Apply", key="dfr") and frf: df = t_find_replace(df, frc, frf, frr, frx); transforms_applied.append(f"Replace in '{frc}'")

    with st.expander("Calculated Column"):
        cn = st.text_input("Name:", "Calculated", key="cn")
        co = st.selectbox("Op:", ["add", "subtract", "multiply", "divide", "pct", "upper", "lower", "trim", "len", "round", "abs"], key="co")
        ca = st.selectbox("Column A:", df.columns.tolist(), key="ca")
        cb = st.selectbox("Column B:", df.columns.tolist(), key="cb") if co in ["add", "subtract", "multiply", "divide", "pct"] else None
        if st.checkbox("Apply", key="dca"): df = t_calc(df, cn, co, ca, cb); transforms_applied.append(f"Calc: {cn}")

    with st.expander("Filter Rows"):
        fic = st.selectbox("Column:", df.columns.tolist(), key="fic"); fio = st.selectbox("Op:", [">", "<", ">=", "<=", "=", "!=", "contains"], key="fio")
        fiv = st.text_input("Value:", key="fiv")
        if st.checkbox("Apply", key="dfi") and fiv: df = t_filter(df, fic, fio, fiv); transforms_applied.append(f"Filter applied")

    with st.expander("VLOOKUP Merge"):
        vf = st.file_uploader("Lookup file:", type=["xlsx", "xls", "csv"], key="vf")
        if vf:
            dl, e = load_file(vf)
            if dl is not None:
                vm = st.selectbox("Your key:", df.columns.tolist(), key="vm"); vl = st.selectbox("Lookup key:", dl.columns.tolist(), key="vl")
                vc = st.multiselect("Bring in:", [c for c in dl.columns if c != vl], key="vc")
                if st.checkbox("Apply", key="dv") and vc: df = t_vlookup(df, dl, vm, vl, vc); transforms_applied.append("VLOOKUP merge")

    with st.expander("Pivot / Aggregate"):
        if len(df.columns) >= 3:
            pi = st.selectbox("Group by:", df.columns.tolist(), key="pi"); pc = st.selectbox("Columns:", df.columns.tolist(), index=min(1, len(df.columns) - 1), key="pc")
            nc = df.select_dtypes(include="number").columns.tolist()
            if nc:
                pv = st.selectbox("Values:", nc, key="pv"); pa = st.selectbox("Agg:", ["sum", "mean", "count", "max", "min"], key="pa")
                if st.checkbox("Apply", key="dp"):
                    try: df = t_pivot(df, pi, pc, pv, pa); transforms_applied.append(f"Pivot: {pi} x {pc}")
                    except Exception as e: st.warning(str(e))

    if transforms_applied:
        st.markdown("---")
        for t in transforms_applied: track_action(t)
        st.markdown("### Results")
        c1, c2 = st.columns(2)
        with c1: st.markdown(f"**Before** ({len(original):,} rows)"); st.dataframe(original.head(15), use_container_width=True, height=250)
        with c2: st.markdown(f"**After** ({len(df):,} rows)"); st.dataframe(df.head(15), use_container_width=True, height=250)

    st.markdown("### Data Preview" if not transforms_applied else "")
    if not transforms_applied: st.dataframe(df.head(30), use_container_width=True, height=350)

    st.markdown("---")
    st.markdown("### Export")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    c1, c2, c3 = st.columns(3)
    with c1: st.download_button("Download Excel", to_excel(df), f"cellshift_{ts}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    with c2: st.download_button("Download CSV", to_csv(df), f"cellshift_{ts}.csv", "text/csv", use_container_width=True)
    with c3: st.download_button("Download JSON", to_json_bytes(df), f"cellshift_{ts}.json", "application/json", use_container_width=True)


# ══════════════════════════════════════════════════════════
# MODULE: INVOICE GENERATOR (PDF + Excel + Email)
# ══════════════════════════════════════════════════════════
def page_invoice():
    st.markdown("### 📄 Invoice Generator")
    st.markdown("Create professional GST/PST-compliant invoices — export as **PDF**, Excel, or email directly to clients.")

    industry = st.session_state.user.get("industry", "Professional Services")
    tax_info = SURREY_INDUSTRIES.get(industry, SURREY_INDUSTRIES["Professional Services"])

    with st.form("invoice"):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**From**")
            from_name = st.text_input("Business Name", value=st.session_state.user.get("company", ""))
            from_addr = st.text_input("Address", placeholder="123 King George Blvd, Surrey BC")
            from_gst = st.text_input("GST Number", placeholder="123456789 RT0001")
            from_pst = st.text_input("PST Number (if applicable)", placeholder="PST-1234-5678")
        with c2:
            st.markdown("**To**")
            to_name = st.text_input("Client Name"); to_company = st.text_input("Client Company")
            to_addr = st.text_input("Client Address"); to_email = st.text_input("Client Email")

        inv_num = st.text_input("Invoice #", value=f"INV-{datetime.now().strftime('%Y%m%d')}-{len(st.session_state.invoices) + 1:03d}")
        inv_date = st.date_input("Date", value=datetime.now())
        due_date = st.date_input("Due Date", value=datetime.now() + timedelta(days=30))
        terms = st.selectbox("Payment Terms", ["Net 30", "Net 15", "Net 60", "Due on Receipt"])

        st.markdown("**Line Items**")
        num_items = st.number_input("Number of items:", 1, 20, 3)
        items = []
        for i in range(int(num_items)):
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1: desc = st.text_input(f"Description {i + 1}", key=f"id{i}")
            with c2: qty = st.number_input(f"Qty {i + 1}", 0.0, 99999.0, 1.0, key=f"iq{i}")
            with c3: rate = st.number_input(f"Rate ($) {i + 1}", 0.0, 999999.0, 0.0, key=f"ir{i}")
            if desc and rate > 0: items.append({"desc": desc, "qty": qty, "rate": rate, "total": round(qty * rate, 2)})

        notes = st.text_area("Notes / Terms", value="Thank you for your business. Payment via e-Transfer or cheque.")
        submitted = st.form_submit_button("Generate Invoice", type="primary", use_container_width=True)

    if submitted and items:
        subtotal = sum(i["total"] for i in items)
        gst = round(subtotal * tax_info.get("gst_rate", 0.05), 2)
        pst = round(subtotal * tax_info.get("pst_rate", 0), 2)
        pst_rate = int(tax_info.get("pst_rate", 0) * 100)
        total = round(subtotal + gst + pst, 2)

        invoice_data = {
            "number": inv_num, "date": str(inv_date), "due": str(due_date), "terms": terms,
            "from": {"name": from_name, "addr": from_addr, "gst": from_gst, "pst": from_pst},
            "to": {"name": to_name, "company": to_company, "addr": to_addr, "email": to_email},
            "items": items, "subtotal": subtotal, "gst": gst, "pst": pst, "pst_rate": pst_rate, "total": total, "notes": notes,
        }
        st.session_state.invoices.append(invoice_data)
        track_action(f"Invoice #{inv_num}")

        # Render HTML preview
        items_html = "".join(f'<tr><td>{it["desc"]}</td><td style="text-align:right">{it["qty"]:.0f}</td><td style="text-align:right">${it["rate"]:,.2f}</td><td style="text-align:right">${it["total"]:,.2f}</td></tr>' for it in items)
        st.markdown(f"""<div class="invoice-box">
            <div style="display:flex;justify-content:space-between;border-bottom:2px solid #2E75B6;padding-bottom:1rem;margin-bottom:1rem;">
                <div><h2 style="color:#1B2A4A;margin:0;">{from_name or 'Your Business'}</h2><p style="color:#64748b;margin:0;">{from_addr}</p>
                    {'<p style="color:#64748b;margin:0;">GST: '+from_gst+'</p>' if from_gst else ''}
                    {'<p style="color:#64748b;margin:0;">PST: '+from_pst+'</p>' if from_pst else ''}</div>
                <div style="text-align:right;"><h2 style="color:#2E75B6;margin:0;">INVOICE</h2><p style="margin:0;"><strong>{inv_num}</strong></p>
                    <p style="color:#64748b;margin:0;">Date: {inv_date} | Due: {due_date} | {terms}</p></div>
            </div>
            <div style="margin-bottom:1.5rem;"><strong>Bill To:</strong><br>{to_name}<br>{to_company}<br>{to_addr}<br>{to_email}</div>
            <table class="invoice-table"><thead><tr><th>Description</th><th style="text-align:right">Qty</th><th style="text-align:right">Rate</th><th style="text-align:right">Amount</th></tr></thead>
            <tbody>{items_html}</tbody>
            <tfoot><tr><td colspan="3" style="text-align:right;padding-top:1rem;"><strong>Subtotal</strong></td><td style="text-align:right;padding-top:1rem;">${subtotal:,.2f}</td></tr>
                <tr><td colspan="3" style="text-align:right;"><strong>GST (5%)</strong></td><td style="text-align:right;">${gst:,.2f}</td></tr>
                {'<tr><td colspan="3" style="text-align:right;"><strong>PST ('+str(pst_rate)+'%)</strong></td><td style="text-align:right;">$'+f"{pst:,.2f}"+'</td></tr>' if pst > 0 else ''}
                <tr style="background:#f0f7ff;"><td colspan="3" style="text-align:right;font-size:1.1rem;"><strong>TOTAL (CAD)</strong></td><td style="text-align:right;font-size:1.1rem;"><strong>${total:,.2f}</strong></td></tr>
            </tfoot></table>
            <div style="margin-top:1.5rem;padding-top:1rem;border-top:1px solid #e2e8f0;color:#64748b;font-size:0.85rem;">{notes}</div>
        </div>""", unsafe_allow_html=True)

        # Export options
        st.markdown("---")
        st.markdown("### Export Invoice")
        c1, c2, c3 = st.columns(3)

        # PDF export
        pdf_bytes = generate_invoice_pdf(invoice_data)
        with c1: st.download_button("📥 Download PDF", pdf_bytes, f"invoice_{inv_num}.pdf", "application/pdf", use_container_width=True)

        # Excel export
        inv_df = pd.DataFrame(items); inv_df.columns = ["Description", "Quantity", "Unit Rate", "Line Total"]
        tax_rows = pd.DataFrame([{"Description": "SUBTOTAL", "Quantity": "", "Unit Rate": "", "Line Total": subtotal},
            {"Description": "GST (5%)", "Quantity": "", "Unit Rate": "", "Line Total": gst}])
        if pst > 0: tax_rows = pd.concat([tax_rows, pd.DataFrame([{"Description": f"PST ({pst_rate}%)", "Quantity": "", "Unit Rate": "", "Line Total": pst}])])
        tax_rows = pd.concat([tax_rows, pd.DataFrame([{"Description": "TOTAL", "Quantity": "", "Unit Rate": "", "Line Total": total}])])
        full_inv = pd.concat([inv_df, tax_rows], ignore_index=True)
        with c2: st.download_button("📥 Download Excel", to_excel(full_inv), f"invoice_{inv_num}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

        # Email invoice
        with c3:
            if to_email and st.session_state.smtp_config.get("configured"):
                if st.button("📧 Email to Client", use_container_width=True):
                    body = f"Hi {to_name},\n\nPlease find attached Invoice #{inv_num} for ${total:,.2f} CAD.\n\nDue: {due_date}\nTerms: {terms}\n\n{notes}\n\nBest regards,\n{from_name}"
                    ok, msg = send_email(to_email, f"Invoice #{inv_num} — {from_name}", body, pdf_bytes, f"invoice_{inv_num}.pdf")
                    if ok: st.success(f"Invoice emailed to {to_email}")
                    else: st.error(msg)
            else:
                st.info("Configure SMTP in Settings to email invoices" if not st.session_state.smtp_config.get("configured") else "Add client email to enable sending")

        st.success(f"Invoice {inv_num} generated — ${total:,.2f} CAD")

    # Invoice history
    if st.session_state.invoices:
        st.markdown("---")
        st.markdown("### Invoice History")
        inv_hist = pd.DataFrame([{"#": i["number"], "To": i["to"]["name"], "Company": i["to"]["company"],
            "Total": f"${i['total']:,.2f}", "Date": i["date"], "Due": i["due"]} for i in st.session_state.invoices])
        st.dataframe(inv_hist, use_container_width=True, hide_index=True)

        # Revenue chart
        if len(st.session_state.invoices) > 1:
            rev_df = pd.DataFrame([{"Date": i["date"], "Amount": i["total"]} for i in st.session_state.invoices])
            fig = px.bar(rev_df, x="Date", y="Amount", title="Invoice Revenue",
                        color_discrete_sequence=["#7c3aed"])
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#8b949e")
            st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════
# MODULE: REPORT BUILDER (with Plotly)
# ══════════════════════════════════════════════════════════
def page_reports():
    st.markdown("### 📊 Report Builder")
    st.markdown("Upload data and generate instant business reports with interactive charts.")

    uf = st.file_uploader("Upload data file:", type=["xlsx", "xls", "csv"], key="rpt_file")
    if not uf: st.info("Upload an Excel/CSV file to generate reports."); return

    df, e = load_file(uf)
    if e: st.error(e); return

    analysis = analyze_df(df)
    track_action("Report Builder")

    report_type = st.selectbox("Report Type:", ["Executive Summary", "Column Analysis", "Distribution Report", "Trend Analysis", "Correlation Matrix"])

    if report_type == "Executive Summary":
        st.markdown(f"#### Executive Summary — {uf.name}")
        st.markdown(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')} | **Rows:** {analysis['rows']:,} | **Columns:** {analysis['cols']}")

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Rows", f"{analysis['rows']:,}")
        with c2: st.metric("Duplicates", analysis['duplicates'])
        with c3: st.metric("Missing Cells", analysis['blank_cells'])
        with c4: st.metric("Completeness", f"{round((1 - analysis['blank_cells'] / max(1, analysis['rows'] * analysis['cols'])) * 100)}%")

        # Data types pie chart
        type_counts = {"Numeric": len(analysis["numeric_cols"]), "Text": len(analysis["text_cols"]),
                       "Date": len(analysis["date_cols"]), "Mixed": len(analysis["mixed_types"])}
        type_counts = {k: v for k, v in type_counts.items() if v > 0}
        if type_counts:
            fig = px.pie(values=list(type_counts.values()), names=list(type_counts.keys()),
                        title="Column Types", color_discrete_sequence=["#58a6ff", "#7c3aed", "#4ade80", "#fb923c"])
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#8b949e")
            st.plotly_chart(fig, use_container_width=True)

        if analysis["numeric_cols"]:
            st.markdown("#### Numeric Summary")
            st.dataframe(df[analysis["numeric_cols"]].describe().round(2), use_container_width=True)

        # Column detail
        type_df = pd.DataFrame([{"Column": c, "Type": str(df[c].dtype), "Non-Null": df[c].notna().sum(),
            "Unique": df[c].nunique(), "Sample": str(df[c].dropna().iloc[0])[:40] if not df[c].dropna().empty else "N/A"} for c in df.columns])
        st.dataframe(type_df, use_container_width=True, hide_index=True)

    elif report_type == "Column Analysis":
        col = st.selectbox("Select column:", df.columns.tolist())
        st.markdown(f"#### Analysis: {col}")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Unique Values", df[col].nunique())
        with c2: st.metric("Missing", f"{df[col].isnull().sum()} ({round(df[col].isnull().sum() / max(1, len(df)) * 100, 1)}%)")
        with c3: st.metric("Most Common", str(df[col].mode().iloc[0])[:20] if not df[col].mode().empty else "N/A")

        vc = df[col].value_counts().head(20).reset_index()
        vc.columns = [col, "Count"]
        fig = px.bar(vc, x=col, y="Count", title=f"Top Values: {col}", color_discrete_sequence=["#58a6ff"])
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#8b949e")
        st.plotly_chart(fig, use_container_width=True)

    elif report_type == "Distribution Report":
        nc = analysis["numeric_cols"]
        if nc:
            col = st.selectbox("Numeric column:", nc)
            stats = df[col].describe()
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.metric("Mean", f"{stats['mean']:,.2f}")
            with c2: st.metric("Median", f"{stats['50%']:,.2f}")
            with c3: st.metric("Std Dev", f"{stats['std']:,.2f}")
            with c4: st.metric("Range", f"{stats['max'] - stats['min']:,.2f}")

            fig = px.histogram(df, x=col, nbins=30, title=f"Distribution: {col}", color_discrete_sequence=["#7c3aed"])
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#8b949e")
            st.plotly_chart(fig, use_container_width=True)

            fig2 = px.box(df, y=col, title=f"Box Plot: {col}", color_discrete_sequence=["#4ade80"])
            fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#8b949e")
            st.plotly_chart(fig2, use_container_width=True)
        else: st.warning("No numeric columns found")

    elif report_type == "Trend Analysis":
        dc = analysis["date_cols"]; nc = analysis["numeric_cols"]
        if dc and nc:
            date_col = st.selectbox("Date column:", dc); val_col = st.selectbox("Value column:", nc)
            agg = st.selectbox("Aggregation:", ["sum", "mean", "count"])
            temp = df.copy(); temp[date_col] = pd.to_datetime(temp[date_col], errors="coerce"); temp = temp.dropna(subset=[date_col])
            trend = temp.groupby(temp[date_col].dt.to_period("M"))[val_col].agg(agg).reset_index()
            trend[date_col] = trend[date_col].astype(str)
            fig = px.line(trend, x=date_col, y=val_col, title=f"Trend: {val_col} ({agg})", markers=True, color_discrete_sequence=["#58a6ff"])
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#8b949e")
            st.plotly_chart(fig, use_container_width=True)
        else: st.warning("Need at least one date and one numeric column")

    elif report_type == "Correlation Matrix":
        nc = analysis["numeric_cols"]
        if len(nc) >= 2:
            corr = df[nc].corr().round(2)
            fig = px.imshow(corr, text_auto=True, title="Correlation Matrix",
                           color_continuous_scale="RdBu_r", aspect="auto")
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#8b949e")
            st.plotly_chart(fig, use_container_width=True)
        else: st.warning("Need at least 2 numeric columns")

    st.download_button("Export Report Data", to_excel(df), f"report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)


# ══════════════════════════════════════════════════════════
# MODULE: COMPLIANCE TRACKER
# ══════════════════════════════════════════════════════════
def page_compliance():
    st.markdown("### ✅ Surrey Business Compliance Tracker")

    industry = st.session_state.user.get("industry", "Professional Services")
    if not industry or industry not in SURREY_INDUSTRIES:
        industry = st.selectbox("Select your industry:", list(SURREY_INDUSTRIES.keys()))

    info = SURREY_INDUSTRIES[industry]
    st.markdown(f"**Industry:** {industry} | **GST:** {info['gst_rate'] * 100:.0f}% | **PST:** {info.get('pst_rate', 0) * 100:.0f}% | **Revenue Range:** {info.get('avg_revenue', 'N/A')}")

    # Risk alerts
    st.markdown("---")
    st.markdown("#### ⚠️ Industry Risks")
    for risk in info.get("risks", []):
        st.markdown(f'<div class="card card-sm"><p>⚠️ {risk}</p></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Required Permits & Licenses")
    for permit in info["permits"]:
        key = f"comp_{permit}"
        if key not in st.session_state: st.session_state[key] = False
        st.session_state[key] = st.checkbox(permit, value=st.session_state[key], key=f"cb_{key}")

    completed = sum(1 for p in info["permits"] if st.session_state.get(f"comp_{p}", False))
    total_p = len(info["permits"])
    pct = round(completed / max(1, total_p) * 100)
    st.progress(pct / 100)
    st.markdown(f"**{completed}/{total_p} completed ({pct}%)**")

    st.markdown("---")
    st.markdown("#### BC Tax Calendar — Key Dates")
    tax_dates = [
        ("GST/HST Filing", "Quarterly — Apr 30, Jul 31, Oct 31, Jan 31", "CRA", "quarterly"),
        ("PST Filing", "Monthly or Quarterly — depends on revenue", "BC Gov", "monthly"),
        ("T2 Corporate Tax", "6 months after fiscal year-end", "CRA", "annual"),
        ("WorkSafeBC Premium", "Quarterly — Mar 20, Jun 20, Sep 20, Dec 20", "WorkSafeBC", "quarterly"),
        ("Surrey Business License Renewal", "Annually — renewal date on license", "City of Surrey", "annual"),
        ("Payroll Remittance", "Monthly — 15th of following month", "CRA", "monthly"),
        ("T4/T4A Filing", "February 28 annually", "CRA", "annual"),
    ]

    now = datetime.now()
    for name, deadline, authority, freq in tax_dates:
        urgency = ""
        if freq == "monthly" and now.day > 10: urgency = " 🔴"
        elif freq == "quarterly" and now.month in [3, 6, 9, 12] and now.day > 15: urgency = " 🟡"
        st.markdown(f'<div class="card card-sm"><h4>{name}{urgency}</h4><p>{deadline} — <em>{authority}</em></p></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Custom Compliance Items")
    with st.form("add_compliance"):
        ci_name = st.text_input("Item name:"); ci_due = st.date_input("Due date:"); ci_note = st.text_input("Notes:")
        if st.form_submit_button("Add Item"):
            if ci_name:
                st.session_state.compliance_items.append({"name": ci_name, "due": str(ci_due), "notes": ci_note, "done": False})
                track_action(f"Compliance: {ci_name}"); st.rerun()

    for i, item in enumerate(st.session_state.compliance_items):
        c1, c2 = st.columns([4, 1])
        with c1:
            due = datetime.strptime(item["due"], "%Y-%m-%d") if item.get("due") else None
            overdue = " 🔴 OVERDUE" if due and due < datetime.now() and not item.get("done") else ""
            st.checkbox(f"{item['name']} (due: {item['due']}){overdue}", value=item.get("done", False), key=f"ci_{i}")
        with c2:
            if st.button("Remove", key=f"cir_{i}"): st.session_state.compliance_items.pop(i); persist(); st.rerun()


# ══════════════════════════════════════════════════════════
# MODULE: EMAIL DRAFTER (with real SMTP)
# ══════════════════════════════════════════════════════════
def page_email():
    st.markdown("### 📧 Email Drafter")
    smtp_ok = st.session_state.smtp_config.get("configured", False)
    if smtp_ok:
        st.markdown(f'<span class="pip-step pip-done">✓ SMTP Connected: {st.session_state.smtp_config["email"]}</span>', unsafe_allow_html=True)
    else:
        st.info("Configure SMTP in Settings to send emails directly. You can still draft and copy emails below.")

    category = st.selectbox("Email Type:", [
        "Invoice Follow-Up (Overdue)", "New Client Welcome", "Project Proposal",
        "Meeting Follow-Up", "Payment Confirmation", "Service Quote",
        "Appointment Reminder", "Review Request", "Partnership Inquiry", "Custom"])

    company = st.session_state.user.get("company", "Your Business")
    name = st.session_state.user.get("name", "Your Name")

    templates = {
        "Invoice Follow-Up (Overdue)": {"subject": "Friendly Reminder — Invoice #{inv_num} Past Due",
            "body": f"Hi {{{{client_name}}}},\n\nI hope this message finds you well. I wanted to follow up regarding Invoice #{{{{inv_num}}}} for ${{{{amount}}}} that was due on {{{{due_date}}}}.\n\nIf payment has already been sent, please disregard this message. Otherwise, could you let me know when we can expect payment?\n\nThank you for your continued business.\n\nBest regards,\n{name}\n{company}"},
        "New Client Welcome": {"subject": f"Welcome to {company}",
            "body": f"Hi {{{{client_name}}}},\n\nWelcome to {company}! We're thrilled to have you on board.\n\nHere's what happens next:\n1. We'll schedule an onboarding call this week\n2. You'll receive access to our client portal\n3. We'll begin work on your project within 48 hours\n\nLooking forward to working together!\n\nBest,\n{name}\n{company}"},
        "Project Proposal": {"subject": f"Proposal: {{{{project_name}}}} — {company}",
            "body": f"Hi {{{{client_name}}}},\n\nThank you for the conversation about {{{{project_name}}}}. Based on our discussion, here's our proposal:\n\nScope: {{{{scope_description}}}}\nTimeline: {{{{timeline}}}}\nInvestment: ${{{{price}}}} + GST\n\nPayment Terms: 50% upfront, 50% on completion\n\nThis proposal is valid for 30 days.\n\nBest regards,\n{name}\n{company}"},
        "Meeting Follow-Up": {"subject": f"Follow-Up: Our Meeting on {{{{date}}}}",
            "body": f"Hi {{{{client_name}}}},\n\nThank you for taking the time to meet today. Here's a summary of what we discussed:\n\n- {{{{topic_1}}}}\n- {{{{topic_2}}}}\n- {{{{topic_3}}}}\n\nNext steps: {{{{next_steps}}}}\n\nPlease let me know if I missed anything.\n\nBest,\n{name}\n{company}"},
        "Payment Confirmation": {"subject": f"Payment Received — Thank You!",
            "body": f"Hi {{{{client_name}}}},\n\nThis confirms we've received your payment of ${{{{amount}}}} for Invoice #{{{{inv_num}}}}.\n\nThank you for your prompt payment.\n\nBest regards,\n{name}\n{company}"},
        "Service Quote": {"subject": f"Quote: {{{{service_name}}}} — {company}",
            "body": f"Hi {{{{client_name}}}},\n\nThank you for your inquiry about {{{{service_name}}}}. Here's our quote:\n\nService: {{{{service_name}}}}\nEstimated Cost: ${{{{price}}}} + GST\nTimeline: {{{{timeline}}}}\n\nThis quote is valid for 14 days.\n\nBest regards,\n{name}\n{company}"},
        "Appointment Reminder": {"subject": f"Reminder: Your Appointment on {{{{date}}}}",
            "body": f"Hi {{{{client_name}}}},\n\nJust a friendly reminder about your appointment:\n\nDate: {{{{date}}}}\nTime: {{{{time}}}}\nLocation: {{{{location}}}}\n\nPlease let us know if you need to reschedule.\n\nBest,\n{name}\n{company}"},
        "Review Request": {"subject": f"How was your experience with {company}?",
            "body": f"Hi {{{{client_name}}}},\n\nThank you for choosing {company}. We hope you're happy with our service!\n\nWould you mind leaving us a quick review? It helps other Surrey businesses find us.\n\n{{{{review_link}}}}\n\nThank you so much!\n\nBest,\n{name}\n{company}"},
        "Partnership Inquiry": {"subject": f"Partnership Opportunity — {company}",
            "body": f"Hi {{{{contact_name}}}},\n\nI'm {name} from {company}, based in Surrey, BC. I came across your business and I think there could be a great opportunity for us to collaborate.\n\n{{{{partnership_details}}}}\n\nWould you be open to a quick call this week?\n\nBest regards,\n{name}\n{company}"},
    }

    to_addr = st.text_input("Recipient Email:", placeholder="client@example.com")

    if category != "Custom" and category in templates:
        tpl = templates[category]
        subject = st.text_input("Subject:", value=tpl["subject"])
        edited = st.text_area("Email Body (edit placeholders in {{braces}}):", value=tpl["body"], height=350)
    else:
        subject = st.text_input("Subject:")
        tone = st.selectbox("Tone:", ["Professional", "Friendly", "Formal", "Urgent"])
        context = st.text_area("What's this email about?", height=100)
        edited = st.text_area("Draft your email:", height=300)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Copy to Clipboard", type="primary", use_container_width=True):
            track_action(f"Email: {category}")
            st.code(f"Subject: {subject}\n\n{edited}", language=None)
            st.success("Email drafted — copy the text above.")
    with c2:
        if smtp_ok and to_addr:
            if st.button("📧 Send Email", use_container_width=True):
                ok, msg = send_email(to_addr, subject, edited)
                if ok: track_action(f"Email sent: {to_addr}"); st.success(f"Sent to {to_addr}")
                else: st.error(msg)


# ══════════════════════════════════════════════════════════
# MODULE: AI ASSISTANT
# ══════════════════════════════════════════════════════════
def page_assistant():
    st.markdown("### 🤖 AI Data Assistant")
    st.markdown("Upload data and ask questions in plain English.")

    uf = st.file_uploader("Upload data:", type=["xlsx", "xls", "csv"], key="ai_file")
    if not uf: st.info("Upload a file to start asking questions."); return

    df, e = load_file(uf)
    if e: st.error(e); return

    analysis = analyze_df(df)
    st.dataframe(df.head(10), use_container_width=True, height=200)
    st.caption(f"{len(df):,} rows × {len(df.columns)} columns | Numeric: {', '.join(analysis['numeric_cols'][:5])}")

    # Quick buttons
    st.markdown("**Quick Questions:**")
    qc1, qc2, qc3, qc4 = st.columns(4)
    quick_q = None
    with qc1:
        if st.button("📊 Summary", use_container_width=True): quick_q = "summary"
    with qc2:
        if st.button("🔢 Totals", use_container_width=True): quick_q = "total all"
    with qc3:
        if st.button("📈 Top 5", use_container_width=True): quick_q = "show top 5"
    with qc4:
        if st.button("❓ Quality", use_container_width=True): quick_q = "data quality"

    q = st.text_input("Ask a question:", placeholder="e.g., What's the total revenue? How many unique customers?")
    if quick_q: q = quick_q

    if q:
        track_action(f"AI: {q[:50]}")
        q_lower = q.lower()
        try:
            if "quality" in q_lower or "health" in q_lower:
                st.markdown("#### Data Quality Report")
                total_cells = analysis["rows"] * analysis["cols"]
                completeness = round((1 - analysis["blank_cells"] / max(1, total_cells)) * 100, 1)
                dup_rate = round(analysis["duplicates"] / max(1, analysis["rows"]) * 100, 1)
                c1, c2, c3, c4 = st.columns(4)
                with c1: st.metric("Completeness", f"{completeness}%")
                with c2: st.metric("Duplicate Rate", f"{dup_rate}%")
                with c3: st.metric("Missing Cells", analysis["blank_cells"])
                with c4: st.metric("Mixed Types", len(analysis["mixed_types"]))

                issues = []
                if completeness < 90: issues.append(f"Data is only {completeness}% complete — consider cleaning blanks")
                if dup_rate > 5: issues.append(f"{dup_rate}% duplicate rows detected — consider deduplication")
                if analysis["mixed_types"]: issues.append(f"Mixed data types in: {', '.join(analysis['mixed_types'])}")
                if issues:
                    st.warning("Issues found:")
                    for issue in issues: st.markdown(f"- {issue}")
                else: st.success("Data quality looks good!")

            elif any(w in q_lower for w in ["total", "sum"]):
                nc = df.select_dtypes(include="number").columns
                matched = False
                for col in nc:
                    if col.lower() in q_lower:
                        st.success(f"**Total {col}:** {df[col].sum():,.2f}")
                        matched = True; break
                if not matched:
                    for col in nc: st.markdown(f"- **{col}:** {df[col].sum():,.2f}")

            elif any(w in q_lower for w in ["average", "mean", "avg"]):
                nc = df.select_dtypes(include="number").columns
                matched = False
                for col in nc:
                    if col.lower() in q_lower:
                        st.success(f"**Average {col}:** {df[col].mean():,.2f}")
                        matched = True; break
                if not matched:
                    for col in nc: st.markdown(f"- **{col} avg:** {df[col].mean():,.2f}")

            elif any(w in q_lower for w in ["how many", "count", "unique"]):
                if "unique" in q_lower:
                    for col in df.columns:
                        if col.lower() in q_lower:
                            st.success(f"**Unique {col}:** {df[col].nunique()}")
                            break
                    else: st.success(f"**Total rows:** {len(df):,}")
                else: st.success(f"**Row count:** {len(df):,}")

            elif any(w in q_lower for w in ["max", "highest", "largest", "top", "best"]):
                n = 5
                for word in q_lower.split():
                    try: n = int(word); break
                    except: pass
                nc = df.select_dtypes(include="number").columns
                if len(nc) > 0:
                    col = nc[0]
                    for c in nc:
                        if c.lower() in q_lower: col = c; break
                    st.dataframe(df.nlargest(n, col), use_container_width=True, hide_index=True)

            elif any(w in q_lower for w in ["min", "lowest", "smallest", "bottom"]):
                nc = df.select_dtypes(include="number").columns
                if len(nc) > 0:
                    col = nc[0]
                    for c in nc:
                        if c.lower() in q_lower: col = c; break
                    st.success(f"**Lowest {col}:** {df[col].min():,.2f}")
                    st.dataframe(df.loc[[df[col].idxmin()]], use_container_width=True, hide_index=True)

            elif any(w in q_lower for w in ["group", "by", "breakdown", "per"]):
                text_cols = df.select_dtypes(include="object").columns
                num_cols = df.select_dtypes(include="number").columns
                if len(text_cols) > 0 and len(num_cols) > 0:
                    group_col = text_cols[0]
                    for c in text_cols:
                        if c.lower() in q_lower: group_col = c; break
                    result = df.groupby(group_col)[num_cols[0]].agg(["sum", "mean", "count"]).round(2)
                    st.dataframe(result, use_container_width=True)
                    fig = px.bar(result.reset_index(), x=group_col, y="sum", title=f"{num_cols[0]} by {group_col}",
                                color_discrete_sequence=["#58a6ff"])
                    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#8b949e")
                    st.plotly_chart(fig, use_container_width=True)

            elif any(w in q_lower for w in ["chart", "plot", "graph", "visualize"]):
                nc = df.select_dtypes(include="number").columns
                if len(nc) >= 1:
                    col = nc[0]
                    fig = px.histogram(df, x=col, title=f"Distribution: {col}", color_discrete_sequence=["#7c3aed"])
                    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#8b949e")
                    st.plotly_chart(fig, use_container_width=True)

            elif any(w in q_lower for w in ["show", "display", "list"]):
                n = 10
                for word in q_lower.split():
                    try: n = int(word); break
                    except: pass
                st.dataframe(df.head(n), use_container_width=True, hide_index=True)

            elif "summary" in q_lower or "describe" in q_lower or "overview" in q_lower:
                st.markdown(f"**{len(df):,} rows** × **{len(df.columns)} columns** | Memory: {analysis['memory_mb']} MB")
                if analysis["numeric_cols"]:
                    st.dataframe(df[analysis["numeric_cols"]].describe().round(2), use_container_width=True)

            else:
                st.markdown("Here's what I found in your data:")
                st.markdown(f"- **{len(df):,} rows** × **{len(df.columns)} columns**")
                for col in df.select_dtypes(include="number").columns[:5]:
                    st.markdown(f"- **{col}**: sum={df[col].sum():,.2f}, avg={df[col].mean():,.2f}")
                st.caption("Try: 'total revenue', 'how many unique customers', 'top 5 by amount', 'data quality', 'chart sales'")
        except Exception as ex:
            st.warning(f"Couldn't process: {ex}")
            st.caption("Try: 'total', 'average', 'count unique', 'top 5', 'group by', 'chart'")


# ══════════════════════════════════════════════════════════
# SETTINGS (with SMTP config)
# ══════════════════════════════════════════════════════════
def page_settings():
    st.markdown("### Settings")
    user = st.session_state.user

    st.markdown(f"**Account:** {user['name']} ({user['email']})")
    tier = st.session_state.user_tier
    badge_cls = {"Free": "badge-free", "Pro": "badge-pro", "Business": "badge-biz"}.get(tier, "badge-free")
    st.markdown(f'<span class="badge {badge_cls}">{tier}</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Profile")
    new_name = st.text_input("Name:", value=user.get("name", ""))
    new_company = st.text_input("Company:", value=user.get("company", ""))
    new_industry = st.selectbox("Industry:", list(SURREY_INDUSTRIES.keys()),
        index=list(SURREY_INDUSTRIES.keys()).index(user.get("industry", "Professional Services")) if user.get("industry") in SURREY_INDUSTRIES else 0)
    if st.button("Save Profile"):
        st.session_state.user.update({"name": new_name, "company": new_company, "industry": new_industry})
        if user["email"] in st.session_state.users_db:
            st.session_state.users_db[user["email"]].update({"name": new_name, "company": new_company, "industry": new_industry})
        persist(); st.success("Saved")

    st.markdown("---")
    st.markdown("#### 📧 Email Configuration (SMTP)")
    st.caption("Connect your email to send invoices and emails directly from Cellshift.")
    cfg = st.session_state.smtp_config
    with st.form("smtp_config"):
        smtp_host = st.text_input("SMTP Host:", value=cfg.get("host", ""), placeholder="smtp.gmail.com")
        smtp_port = st.number_input("Port:", value=int(cfg.get("port", 587)), min_value=1, max_value=65535)
        smtp_email = st.text_input("Email:", value=cfg.get("email", ""), placeholder="you@gmail.com")
        smtp_pw = st.text_input("App Password:", type="password", placeholder="16-character app password (not your login password)")
        st.caption("For Gmail: Enable 2FA → Create App Password at myaccount.google.com/apppasswords")
        if st.form_submit_button("Save & Test Connection"):
            if all([smtp_host, smtp_email, smtp_pw]):
                try:
                    with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
                        server.starttls()
                        server.login(smtp_email, smtp_pw)
                    st.session_state.smtp_config = {"host": smtp_host, "port": smtp_port, "email": smtp_email, "password": smtp_pw, "configured": True}
                    persist(); st.success("SMTP connected successfully! You can now send emails from Cellshift.")
                except Exception as e:
                    st.error(f"Connection failed: {e}")
            else: st.warning("Fill all SMTP fields")

    st.markdown("---")
    st.markdown("#### Upgrade Plan")
    c1, c2, c3 = st.columns(3)
    plans = [
        (c1, "Free", "$0/mo", ["15 actions/day", "10MB files", "Transform + Dashboard"]),
        (c2, "Pro", "$29/mo", ["Unlimited actions", "All 6 modules", "Batch processing", "50MB files", "PDF invoices", "SMTP email"]),
        (c3, "Business", "$79/mo", ["Everything in Pro", "200MB files", "Priority support", "Custom integrations", "API access"]),
    ]
    for col, name, price, feats in plans:
        with col:
            cur = " (Current)" if tier == name else ""
            st.markdown(f"**{name}{cur}** — {price}")
            for f in feats: st.markdown(f"- {f}")
            if name != tier and name != "Free":
                if st.button(f"Upgrade to {name}", key=f"up_{name}"):
                    st.session_state.user_tier = name
                    if user["email"] in st.session_state.users_db:
                        st.session_state.users_db[user["email"]]["tier"] = name
                    persist(); st.success(f"Upgraded to {name}!"); st.rerun()

    st.markdown("---")
    st.markdown("#### Data Management")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Export All Data"):
            all_data = {"users": len(st.session_state.users_db), "invoices": st.session_state.invoices,
                       "compliance": st.session_state.compliance_items, "history": st.session_state.transform_history[-100:]}
            st.download_button("Download", json.dumps(all_data, indent=2, default=str).encode(), "cellshift_export.json", "application/json")
    with c2:
        st.caption(f"Invoices: {len(st.session_state.invoices)} | Compliance items: {len(st.session_state.compliance_items)}")

    st.markdown("---")
    if st.button("Log Out"):
        st.session_state.authenticated = False; st.session_state.user = None; st.rerun()


# ══════════════════════════════════════════════════════════
# ADMIN DASHBOARD
# ══════════════════════════════════════════════════════════
def page_admin():
    st.markdown("### 👑 Admin Dashboard")
    s = st.session_state.admin_stats
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Signups", s["total_signups"])
    with c2: st.metric("Total Actions", s["total_actions"])
    with c3: st.metric("Files Processed", s["files_processed"])
    active = len(s["active_users"]) if isinstance(s["active_users"], list) else 0
    with c4: st.metric("Active Users", active)

    if st.session_state.users_db:
        st.markdown("#### Users")
        users_list = [{"Email": e, "Name": d["name"], "Company": d.get("company", ""), "Tier": d["tier"],
            "Industry": d.get("industry", ""), "Joined": d["created"][:10]} for e, d in st.session_state.users_db.items()]
        st.dataframe(pd.DataFrame(users_list), use_container_width=True, hide_index=True)

        # Tier distribution
        if len(users_list) > 1:
            tier_df = pd.DataFrame(users_list)
            fig = px.pie(tier_df, names="Tier", title="User Tiers", color_discrete_sequence=["#4ade80", "#7c3aed", "#58a6ff"])
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#8b949e")
            st.plotly_chart(fig, use_container_width=True)

    if st.session_state.transform_history:
        st.markdown("#### Activity Log")
        hist_df = pd.DataFrame(st.session_state.transform_history[-50:])
        st.dataframe(hist_df, use_container_width=True, hide_index=True)

        # Activity over time
        if "date" in hist_df.columns and len(hist_df) > 1:
            daily = hist_df.groupby("date").size().reset_index(name="actions")
            fig = px.area(daily, x="date", y="actions", title="Actions Over Time", color_discrete_sequence=["#58a6ff"])
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#8b949e")
            st.plotly_chart(fig, use_container_width=True)

    if st.session_state.invoices:
        st.markdown("#### Invoice Summary")
        inv_df = pd.DataFrame([{"#": i["number"], "To": i["to"]["name"], "Total": f"${i['total']:,.2f}", "Date": i["date"]} for i in st.session_state.invoices])
        st.dataframe(inv_df, use_container_width=True, hide_index=True)
        total_rev = sum(i["total"] for i in st.session_state.invoices)
        st.metric("Total Invoiced Revenue", f"${total_rev:,.2f} CAD")


# ══════════════════════════════════════════════════════════
# MAIN ROUTER
# ══════════════════════════════════════════════════════════
def main():
    if not st.session_state.authenticated:
        show_auth(); return

    with st.sidebar:
        st.markdown('<p class="hero-title" style="font-size:1.4rem;">Cellshift</p>', unsafe_allow_html=True)
        tier = st.session_state.user_tier
        badge_cls = {"Free": "badge-free", "Pro": "badge-pro", "Business": "badge-biz"}.get(tier, "badge-free")
        st.markdown(f'<span class="badge {badge_cls}">{tier}</span> &nbsp; {st.session_state.user["name"]}', unsafe_allow_html=True)
        st.markdown("---")

        pages = ["Home", "Transform", "Invoices", "Reports", "Compliance", "Email", "AI Assistant", "Settings"]
        if st.session_state.user.get("email") in ["manishmba9909@gmail.com", "admin@cellshift.ca", "guest@cellshift.ca"]:
            pages.append("Admin")

        icons = {"Home": "🏠", "Transform": "⚡", "Invoices": "📄", "Reports": "📊",
                 "Compliance": "✅", "Email": "📧", "AI Assistant": "🤖", "Settings": "⚙️", "Admin": "👑"}
        page = st.radio("", pages, format_func=lambda x: f"{icons.get(x, '')} {x}", label_visibility="collapsed")

        st.markdown("---")
        limit = TIER_LIMITS[tier]['actions_per_day']
        used = st.session_state.action_count_today
        st.progress(min(used / limit, 1.0))
        st.caption(f"Actions: {used}/{limit} today")
        if st.session_state.smtp_config.get("configured"):
            st.markdown(f'<span class="pip-step pip-done" style="font-size:0.65rem;">✓ SMTP</span>', unsafe_allow_html=True)
        st.markdown("---")
        st.caption("Built for Surrey, BC businesses")
        st.caption("Cellshift v2.0 | Production")

    route = {"Home": page_home, "Transform": page_transform, "Invoices": page_invoice,
             "Reports": page_reports, "Compliance": page_compliance, "Email": page_email,
             "AI Assistant": page_assistant, "Settings": page_settings, "Admin": page_admin}
    route.get(page, page_home)()

    st.markdown("""<div class="footer">
        Cellshift &copy; 2026 | AI Business Automation for Surrey, BC<br>
        <a href="https://manish120889.github.io/cellshift/privacy_policy.html">Privacy</a> |
        <a href="https://manish120889.github.io/cellshift/terms_of_service.html">Terms</a> |
        support@cellshift.ca
    </div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
