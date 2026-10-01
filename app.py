# ============================================================
# AKILLI ŞEHİR VE GÜVENLİK YÖNETİM PANELİ
# Smart City & Industrial Security Dashboard
# ============================================================
# Modüller:
#   1. Endüstriyel Ambalaj OCR & Kalite Kontrol
#   2. Akıllı Trafik & Yaya Takip ve Sayımı (Line Crossing)
#   3. Erken Uyarı Yangın ve Duman Tespiti
# ============================================================

import streamlit as st
import cv2
import numpy as np
import pandas as pd
import tempfile
import os
import re
import time
import io
from pathlib import Path
from PIL import Image

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MultiVision AI | Smart City Dashboard",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════
# GLOBAL CSS
# ═══════════════════════════════════════════════════════════════════
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --bg-primary:    #0a0e1a;
    --bg-secondary:  #0f1624;
    --bg-card:       #131929;
    --bg-card-hover: #1a2238;
    --accent-blue:   #3b82f6;
    --accent-cyan:   #06b6d4;
    --accent-purple: #8b5cf6;
    --accent-green:  #10b981;
    --accent-orange: #f59e0b;
    --accent-red:    #ef4444;
    --text-primary:  #e2e8f0;
    --text-secondary:#94a3b8;
    --text-muted:    #64748b;
    --border:        #1e2d4a;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0f172a 50%, #0a0e1a 100%) !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1624 0%, #0a0e1a 100%) !important;
    border-right: 1px solid var(--border) !important;
}

.dashboard-header {
    background: linear-gradient(135deg, #0f1624 0%, #1a2238 50%, #0f1624 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.dashboard-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan), var(--accent-purple));
}
.dashboard-header h1 {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #e2e8f0, #94a3b8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 8px 0;
}
.dashboard-header p {
    color: var(--text-secondary);
    font-size: 0.95rem;
    margin: 0;
}
.header-badge {
    display: inline-block;
    background: rgba(59,130,246,0.15);
    border: 1px solid rgba(59,130,246,0.3);
    color: var(--accent-blue);
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    margin-right: 6px;
    margin-bottom: 10px;
}

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}
.kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
}
.kpi-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    border-radius: 0 0 12px 12px;
}
.kpi-card.blue::after   { background: var(--accent-blue); }
.kpi-card.cyan::after   { background: var(--accent-cyan); }
.kpi-card.green::after  { background: var(--accent-green); }
.kpi-card.red::after    { background: var(--accent-red); }
.kpi-card.purple::after { background: var(--accent-purple); }
.kpi-card.orange::after { background: var(--accent-orange); }
.kpi-card:hover { border-color: rgba(59,130,246,0.4); transform: translateY(-2px); }
.kpi-icon  { font-size: 1.8rem; margin-bottom: 8px; }
.kpi-value {
    font-size: 2rem;
    font-weight: 800;
    line-height: 1;
    font-family: 'JetBrains Mono', monospace;
}
.kpi-value.blue   { color: var(--accent-blue); }
.kpi-value.cyan   { color: var(--accent-cyan); }
.kpi-value.green  { color: var(--accent-green); }
.kpi-value.red    { color: var(--accent-red); }
.kpi-value.purple { color: var(--accent-purple); }
.kpi-value.orange { color: var(--accent-orange); }
.kpi-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 4px;
}

.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
    border-left: 4px solid var(--accent-blue);
    padding-left: 12px;
    margin: 24px 0 16px 0;
}

.panel {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
}

.alert-danger {
    background: rgba(239,68,68,0.15);
    border: 2px solid var(--accent-red);
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
    animation: pulse-red 1.5s ease-in-out infinite;
}
.alert-danger h2 {
    color: var(--accent-red);
    font-size: 1.4rem;
    font-weight: 800;
    margin: 0;
}
.alert-safe {
    background: rgba(16,185,129,0.12);
    border: 2px solid var(--accent-green);
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
}
.alert-safe h2 {
    color: var(--accent-green);
    font-size: 1.4rem;
    font-weight: 700;
    margin: 0;
}

@keyframes pulse-red {
    0%, 100% { box-shadow: 0 0 0 0 rgba(239,68,68,0.4); }
    50%       { box-shadow: 0 0 20px 8px rgba(239,68,68,0.15); }
}

.stButton > button {
    background: linear-gradient(135deg, var(--accent-blue), #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(59,130,246,0.4) !important;
}

div[data-testid="stFileUploader"] {
    background: var(--bg-card) !important;
    border: 2px dashed var(--border) !important;
    border-radius: 12px !important;
}
div[data-testid="stFileUploader"]:hover { border-color: var(--accent-blue) !important; }

.stTabs [data-baseweb="tab-list"] { background: var(--bg-card) !important; border-radius: 10px; padding: 4px; }
.stTabs [data-baseweb="tab"] { color: var(--text-secondary) !important; border-radius: 8px !important; }
.stTabs [aria-selected="true"] { background: var(--accent-blue) !important; color: white !important; }

.sidebar-logo {
    text-align: center;
    padding: 12px 0 20px 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 16px;
}
.sidebar-logo .logo-title {
    font-size: 1.1rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-cyan));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.sidebar-logo .logo-sub {
    font-size: 0.7rem;
    color: var(--text-muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.sys-status {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px 16px;
    margin-top: 8px;
}
.sys-status-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 0;
    font-size: 0.82rem;
    color: var(--text-secondary);
}
.sys-ok   { color: var(--accent-green); font-weight: 600; }
.sys-err  { color: var(--accent-red); font-weight: 600; }

.detection-info {
    background: rgba(59,130,246,0.1);
    border: 1px solid rgba(59,130,246,0.25);
    border-radius: 8px;
    padding: 12px 16px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: var(--text-secondary);
    white-space: pre-wrap;
}
</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# DEPENDENCY & MODEL LOADER
# ═══════════════════════════════════════════════════════════════════

@st.cache_resource(show_spinner=False)
def load_yolo_model(model_path: str = "best.pt"):
    """Load YOLOv8 model with fallback to yolov8n.pt."""
    try:
        from ultralytics import YOLO
        if os.path.exists(model_path):
            model = YOLO(model_path)
            return model, model_path, None
        model = YOLO("yolov8n.pt")
        return model, "yolov8n.pt", f"⚠️ '{model_path}' bulunamadı → 'yolov8n.pt' (COCO pretrained) kullanılıyor."
    except Exception as e:
        return None, None, str(e)


@st.cache_resource(show_spinner=False)
def load_ocr_engine():
    """Load PaddleOCR engine (cached)."""
    try:
        from paddleocr import PaddleOCR
        ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
        return ocr, None
    except ImportError:
        return None, "PaddleOCR kurulu değil. `pip install paddleocr paddlepaddle` komutunu çalıştırın."
    except Exception as e:
        return None, str(e)


def check_dependencies() -> dict:
    """Return availability of key libraries."""
    status = {}
    for lib in ["ultralytics", "paddleocr", "cv2", "pandas", "PIL"]:
        try:
            __import__(lib if lib != "PIL" else "PIL.Image")
            status[lib] = True
        except ImportError:
            status[lib] = False
    return status


# ═══════════════════════════════════════════════════════════════════
# HELPER UTILITIES
# ═══════════════════════════════════════════════════════════════════

def pil_to_cv(img: Image.Image) -> np.ndarray:
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def cv_to_pil(img: np.ndarray) -> Image.Image:
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))


def draw_bbox(img_bgr: np.ndarray, box, label: str,
              color=(59, 130, 246), thickness=2) -> np.ndarray:
    x1, y1, x2, y2 = map(int, box)
    cv2.rectangle(img_bgr, (x1, y1), (x2, y2), color, thickness)
    font_scale, font_thick = 0.6, 2
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thick)
    cv2.rectangle(img_bgr, (x1, y1 - th - 8), (x1 + tw + 6, y1), color, -1)
    cv2.putText(img_bgr, label, (x1 + 3, y1 - 4),
                cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thick)
    return img_bgr


def render_kpi_row(cards) -> None:
    html = '<div class="kpi-grid">'
    for (icon, value, label, color) in cards:
        html += f"""
        <div class="kpi-card {color}">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-value {color}">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def df_to_excel(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="OCR_Results")
    return buf.getvalue()


def extract_gramaj(text: str) -> str:
    """Regex-based weight extraction from OCR text."""
    patterns = [
        r'(\d+[\.,]?\d*)\s*(kg|KG|Kg)',
        r'(\d+[\.,]?\d*)\s*(g|gr|GR|gram|GRAM)(?!\w)',
        r'(\d+[\.,]?\d*)\s*(ml|ML|mL)',
        r'(\d+[\.,]?\d*)\s*(lt|LT|litre|liter|L)(?!\w)',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return f"{m.group(1)} {m.group(2).upper()}"
    return "Bulunamadı"


def extract_product_name(lines: list) -> str:
    """Heuristic: longest meaningful line as product name."""
    candidates = []
    for line in lines:
        stripped = line.strip()
        if len(stripped) > 4 and not re.fullmatch(r'[\d\s\.\,\-\/\(\)]+', stripped):
            candidates.append(stripped)
    if not candidates:
        return "Bulunamadı"
    candidates.sort(key=len, reverse=True)
    return candidates[0]


# ═══════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════

def render_sidebar(dep_status: dict):
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">
            <div style="font-size:2.5rem;">🏙️</div>
            <div class="logo-title">MultiVision AI</div>
            <div class="logo-sub">Smart City Dashboard</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 📂 Modül Seçimi")
        module = st.radio(
            "Aktif Modül",
            options=[
                "🏭  Ambalaj OCR & Kalite Kontrol",
                "🚦  Trafik & Yaya Takibi",
                "🔥  Yangın & Duman Tespiti",
            ],
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.markdown("#### ⚙️ Model Ayarları")
        conf_threshold = st.slider(
            "Confidence Eşiği",
            min_value=0.10, max_value=0.95, value=0.40, step=0.05,
            help="Tespit güven eşiği. Düşük = daha hassas, yüksek = daha seçici.",
        )
        iou_threshold = st.slider(
            "IoU Eşiği (NMS)",
            min_value=0.10, max_value=0.90, value=0.45, step=0.05,
        )

        st.markdown("---")
        st.markdown("#### 📡 Sistem Durumu")
        labels = {
            "ultralytics": "Ultralytics / YOLO",
            "paddleocr":   "PaddleOCR",
            "cv2":         "OpenCV",
            "pandas":      "Pandas",
            "PIL":         "Pillow",
        }
        sys_html = '<div class="sys-status">'
        for key, name in labels.items():
            ok = dep_status.get(key, False)
            dot   = "🟢" if ok else "🔴"
            cls   = "sys-ok" if ok else "sys-err"
            label = "Aktif" if ok else "Eksik"
            sys_html += (
                f'<div class="sys-status-item">'
                f'<span>{dot} {name}</span>'
                f'<span class="{cls}">{label}</span>'
                f'</div>'
            )
        sys_html += "</div>"
        st.markdown(sys_html, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(
            '<p style="text-align:center;font-size:0.72rem;color:#475569;">'
            'v2.0 · MultiVision AI<br>© 2026 Smart City Labs'
            "</p>",
            unsafe_allow_html=True,
        )

    return module, conf_threshold, iou_threshold


# ═══════════════════════════════════════════════════════════════════
# MODULE 1 — ENDÜSTRİYEL AMBALAJ OCR & KALİTE KONTROL
# ═══════════════════════════════════════════════════════════════════

def module_ocr_quality(conf_threshold: float, iou_threshold: float):
    st.markdown("""
    <div class="dashboard-header">
        <div>
            <span class="header-badge">MODÜL 1</span>
            <span class="header-badge" style="background:rgba(139,92,246,0.15);
              border-color:rgba(139,92,246,0.3);color:#8b5cf6;">OCR</span>
        </div>
        <h1>🏭 Endüstriyel Ambalaj OCR & Kalite Kontrol</h1>
        <p>YOLOv8 ile ambalaj tespiti → PaddleOCR metin çıkarımı → Regex ile Ürün Adı & Gramaj analizi</p>
    </div>
    """, unsafe_allow_html=True)

    kpi_ph = st.empty()
    kpi_ph.markdown("""
    <div class="kpi-grid">
        <div class="kpi-card purple"><div class="kpi-icon">📦</div>
            <div class="kpi-value purple">—</div><div class="kpi-label">Tespit Edilen ROI</div></div>
        <div class="kpi-card blue"><div class="kpi-icon">🔤</div>
            <div class="kpi-value blue">—</div><div class="kpi-label">OCR Satır Sayısı</div></div>
        <div class="kpi-card green"><div class="kpi-icon">⚖️</div>
            <div class="kpi-value green">—</div><div class="kpi-label">Gramaj</div></div>
        <div class="kpi-card cyan"><div class="kpi-icon">🏷️</div>
            <div class="kpi-value cyan">—</div><div class="kpi-label">Ürün Adı</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">📁 Görsel Yükle</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "PNG veya JPG formatında ambalaj görseli yükleyin",
        type=["png", "jpg", "jpeg"],
        key="ocr_uploader",
    )

    if uploaded is None:
        st.markdown("""
        <div class="panel" style="text-align:center;padding:48px;color:#475569;">
            <div style="font-size:3rem;margin-bottom:12px;">📷</div>
            <div style="font-size:1rem;font-weight:600;">Analiz için bir görsel yükleyin</div>
            <div style="font-size:0.85rem;margin-top:6px;">Desteklenen: PNG, JPG, JPEG</div>
        </div>
        """, unsafe_allow_html=True)
        return

    img_pil = Image.open(uploaded).convert("RGB")
    img_bgr = pil_to_cv(img_pil)
    h_orig, w_orig = img_bgr.shape[:2]

    col_orig, col_result = st.columns(2, gap="medium")
    with col_orig:
        st.markdown('<div class="section-title">🖼️ Orijinal Görsel</div>', unsafe_allow_html=True)
        st.image(img_pil, use_container_width=True)

    # ── YOLO Detection ──────────────────────────────────────────
    model, model_name, model_warn = load_yolo_model("best.pt")
    if model_warn:
        st.warning(model_warn)
    if model is None:
        st.error("❌ YOLO modeli yüklenemedi. `pip install ultralytics` komutunu çalıştırın.")
        return

    with st.spinner("🔍 YOLOv8 ile nesne tespiti yapılıyor..."):
        try:
            results = model.predict(
                source=img_bgr, conf=conf_threshold,
                iou=iou_threshold, verbose=False,
            )
        except Exception as e:
            st.error(f"❌ YOLO tahmin hatası: {e}")
            return

    result = results[0]
    img_annotated = img_bgr.copy()
    roi_crops     = []
    detection_log = []
    PURPLE = (139, 92, 246)

    if result.boxes is not None and len(result.boxes) > 0:
        for box in result.boxes:
            cls_id   = int(box.cls[0])
            cls_name = result.names.get(cls_id, str(cls_id))
            conf_val = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            draw_bbox(img_annotated, (x1, y1, x2, y2),
                      f"{cls_name} {conf_val:.2f}", PURPLE, 3)
            crop = img_bgr[max(0, y1):min(h_orig, y2), max(0, x1):min(w_orig, x2)]
            if crop.size > 0:
                roi_crops.append((cls_name, conf_val, crop, (x1, y1, x2, y2)))
            detection_log.append({
                "Sınıf": cls_name, "Güven": f"{conf_val:.2%}",
                "X1": x1, "Y1": y1, "X2": x2, "Y2": y2,
            })
    else:
        roi_crops.append(("full_image", 1.0, img_bgr.copy(), (0, 0, w_orig, h_orig)))
        cv2.rectangle(img_annotated, (4, 4), (w_orig - 4, h_orig - 4), PURPLE, 3)

    with col_result:
        st.markdown('<div class="section-title">🎯 Tespit Sonucu</div>', unsafe_allow_html=True)
        st.image(cv_to_pil(img_annotated), use_container_width=True)

    # ── OCR ─────────────────────────────────────────────────────
    ocr_engine, ocr_err = load_ocr_engine()
    if ocr_err:
        st.warning(f"⚠️ OCR motoru: {ocr_err}")

    all_ocr_results = []
    ocr_texts = []

    if ocr_engine and roi_crops:
        with st.spinner("🔤 PaddleOCR metinleri çıkarıyor..."):
            for cls_name, conf_val, crop, coords in roi_crops:
                try:
                    crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
                    ocr_out  = ocr_engine.ocr(crop_rgb, cls=True)
                    if ocr_out and ocr_out[0]:
                        for line in ocr_out[0]:
                            text  = line[1][0]
                            score = line[1][1]
                            all_ocr_results.append({
                                "Bölge": cls_name, "Metin": text,
                                "OCR Güven": f"{score:.2%}",
                                "Koordinatlar": str(coords),
                            })
                            ocr_texts.append(text)
                except Exception as e:
                    st.warning(f"OCR hatası ({cls_name}): {e}")
    elif not ocr_engine:
        st.info("💡 PaddleOCR bulunamadığından demo metin gösterilmektedir.")
        demo_texts = [
            "PREMIUM ORGANIC PACKAGE",
            "Net Weight: 500g",
            "Batch No: A2024-01",
            "EXP: 12/2026",
            "Produced by: Smart Factory Ltd.",
        ]
        for t in demo_texts:
            all_ocr_results.append({
                "Bölge": "full_image", "Metin": t,
                "OCR Güven": "N/A", "Koordinatlar": f"(0,0,{w_orig},{h_orig})",
            })
            ocr_texts.append(t)

    # ── Regex Extraction ────────────────────────────────────────
    combined_text = " ".join(ocr_texts)
    gramaj        = extract_gramaj(combined_text)
    product_name  = extract_product_name(ocr_texts)
    name_found    = "✅ Evet" if product_name != "Bulunamadı" else "❌ Hayır"

    kpi_ph.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card purple"><div class="kpi-icon">📦</div>
            <div class="kpi-value purple">{len(roi_crops)}</div><div class="kpi-label">Tespit Edilen ROI</div></div>
        <div class="kpi-card blue"><div class="kpi-icon">🔤</div>
            <div class="kpi-value blue">{len(ocr_texts)}</div><div class="kpi-label">OCR Satır Sayısı</div></div>
        <div class="kpi-card green"><div class="kpi-icon">⚖️</div>
            <div class="kpi-value green" style="font-size:1.1rem;">{gramaj}</div>
            <div class="kpi-label">Gramaj</div></div>
        <div class="kpi-card cyan"><div class="kpi-icon">🏷️</div>
            <div class="kpi-value cyan" style="font-size:1rem;">{name_found}</div>
            <div class="kpi-label">Ürün Adı Bulundu</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Results Tabs ─────────────────────────────────────────────
    st.markdown('<div class="section-title">📋 Analiz Sonuçları</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["🔤 OCR Çıktısı", "📦 Tespit Detayları", "📊 Ham Metin"])

    with tab1:
        if all_ocr_results:
            df_ocr = pd.DataFrame(all_ocr_results)
            st.dataframe(df_ocr, use_container_width=True)
            col_a, col_b = st.columns(2)
            col_a.metric("🏷️ Ürün Adı", product_name)
            col_b.metric("⚖️ Gramaj",    gramaj)
            excel_bytes = df_to_excel(df_ocr)
            st.download_button(
                label="⬇️  Excel Olarak İndir (.xlsx)",
                data=excel_bytes,
                file_name="ocr_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        else:
            st.warning("OCR metni çıkarılamadı.")

    with tab2:
        if detection_log:
            st.dataframe(pd.DataFrame(detection_log), use_container_width=True)
        else:
            st.info("Tespit bulunamadı; tüm görsel ROI olarak işlendi.")

    with tab3:
        raw_text = "\n".join(ocr_texts) if ocr_texts else "Metin yok"
        st.markdown(f'<div class="detection-info">{raw_text}</div>', unsafe_allow_html=True)

    # ── ROI Crops ────────────────────────────────────────────────
    if roi_crops:
        st.markdown('<div class="section-title">✂️ Kırpılan ROI Bölgeleri</div>', unsafe_allow_html=True)
        n_cols = min(len(roi_crops), 4)
        cols   = st.columns(n_cols)
        for i, (cls_name, conf_val, crop, _) in enumerate(roi_crops):
            with cols[i % n_cols]:
                st.image(cv_to_pil(crop),
                         caption=f"{cls_name} ({conf_val:.2%})",
                         use_container_width=True)


# ═══════════════════════════════════════════════════════════════════
# MODULE 2 — AKILLI TRAFİK & YAYA TAKİP VE SAYIMI
# ═══════════════════════════════════════════════════════════════════

VEHICLE_CLASSES = {"car", "bus", "truck", "motorcycle", "bicycle"}
PERSON_CLASS    = {"person"}

CLASS_COLORS = {
    "person":     (16,  185, 129),
    "car":        (59,  130, 246),
    "bus":        (245, 158, 11),
    "truck":      (239, 68,  68),
    "motorcycle": (168, 85,  247),
    "bicycle":    (6,   182, 212),
}
DEFAULT_COLOR = (148, 163, 184)


def _get_centroid(box) -> tuple:
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    return ((x1 + x2) // 2, (y1 + y2) // 2)


def module_traffic(conf_threshold: float, iou_threshold: float):
    st.markdown("""
    <div class="dashboard-header">
        <div>
            <span class="header-badge">MODÜL 2</span>
            <span class="header-badge" style="background:rgba(6,182,212,0.15);
              border-color:rgba(6,182,212,0.3);color:#06b6d4;">TRACKING</span>
        </div>
        <h1>🚦 Akıllı Trafik & Yaya Takibi (Line Crossing)</h1>
        <p>YOLOv8 Tracking → ID tabanlı saydırma → Sanal Çizgi Geçiş Sayacı</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Session state counters ───────────────────────────────────
    for key in ["traffic_vehicles", "traffic_persons"]:
        if key not in st.session_state:
            st.session_state[key] = 0
    if "traffic_crossed_ids"   not in st.session_state:
        st.session_state.traffic_crossed_ids   = set()
    if "traffic_prev_positions" not in st.session_state:
        st.session_state.traffic_prev_positions = {}

    kpi_ph = st.empty()

    def _refresh_kpi(fps_val: float = 0.0):
        v = st.session_state.traffic_vehicles
        p = st.session_state.traffic_persons
        kpi_ph.markdown(f"""
        <div class="kpi-grid">
            <div class="kpi-card cyan"><div class="kpi-icon">🚗</div>
                <div class="kpi-value cyan">{v}</div><div class="kpi-label">Araç Geçişi</div></div>
            <div class="kpi-card blue"><div class="kpi-icon">🚶</div>
                <div class="kpi-value blue">{p}</div><div class="kpi-label">Yaya Geçişi</div></div>
            <div class="kpi-card green"><div class="kpi-icon">📊</div>
                <div class="kpi-value green">{v + p}</div><div class="kpi-label">Toplam Geçiş</div></div>
            <div class="kpi-card orange"><div class="kpi-icon">⚡</div>
                <div class="kpi-value orange">{fps_val:.1f}</div><div class="kpi-label">FPS</div></div>
        </div>
        """, unsafe_allow_html=True)

    _refresh_kpi()

    st.markdown('<div class="section-title">🎞️ Video Yükle</div>', unsafe_allow_html=True)
    uploaded_video = st.file_uploader(
        "MP4 formatında trafik videosu yükleyin",
        type=["mp4", "avi", "mov"],
        key="traffic_uploader",
    )

    col_cfg, col_info = st.columns([1, 2])
    with col_cfg:
        max_frames   = st.number_input("İşlenecek Maks. Frame", 30, 3000, 300, 30)
        tracker_type = st.selectbox("Tracker", ["bytetrack.yaml", "botsort.yaml"])
        if st.button("🔄 Sayaçları Sıfırla", use_container_width=True):
            st.session_state.traffic_vehicles        = 0
            st.session_state.traffic_persons         = 0
            st.session_state.traffic_crossed_ids     = set()
            st.session_state.traffic_prev_positions  = {}
            st.rerun()

    with col_info:
        st.markdown("""
        <div class="panel">
            <div style="font-size:0.85rem;color:#94a3b8;">
                <strong style="color:#06b6d4;">📌 Nasıl Çalışır?</strong><br><br>
                • Video ortasına yatay sanal çizgi çizilir.<br>
                • Her nesne benzersiz ID ile takip edilir (ByteTrack).<br>
                • Çizginin <strong>altından üstüne</strong> geçen → sayılır.<br>
                • Aynı ID bir kez sayılır (tekrar sayılmaz).<br>
                • <strong style="color:#3b82f6;">Mavi çizgi</strong> = Sanal sınır
            </div>
        </div>
        """, unsafe_allow_html=True)

    if uploaded_video is None:
        st.markdown("""
        <div class="panel" style="text-align:center;padding:48px;color:#475569;">
            <div style="font-size:3rem;margin-bottom:12px;">🎥</div>
            <div style="font-size:1rem;font-weight:600;">Analiz için bir video yükleyin</div>
            <div style="font-size:0.85rem;margin-top:6px;">Desteklenen: MP4, AVI, MOV</div>
        </div>
        """, unsafe_allow_html=True)
        return

    model, _, model_warn = load_yolo_model("best.pt")
    if model_warn:
        st.warning(model_warn)
    if model is None:
        st.error("❌ YOLO modeli yüklenemedi.")
        return

    if not st.button("▶️  Analizi Başlat", use_container_width=True, type="primary"):
        st.info("▶️ Analizi başlatmak için butona basın.")
        return

    # Reset for new run
    st.session_state.traffic_vehicles        = 0
    st.session_state.traffic_persons         = 0
    st.session_state.traffic_crossed_ids     = set()
    st.session_state.traffic_prev_positions  = {}

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(uploaded_video.read())
        tmp_path = tmp.name

    cap       = cv2.VideoCapture(tmp_path)
    width     = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height    = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    line_y    = height // 2
    frame_idx = 0
    t_start   = time.time()

    st.markdown('<div class="section-title">📺 Canlı İşleme</div>', unsafe_allow_html=True)
    frame_display = st.empty()
    progress_bar  = st.progress(0, text="İşleniyor…")
    status_text   = st.empty()

    try:
        while cap.isOpened() and frame_idx < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            frame_idx += 1

            elapsed  = time.time() - t_start
            fps_live = frame_idx / elapsed if elapsed > 0 else 0.0

            try:
                track_results = model.track(
                    source=frame, conf=conf_threshold, iou=iou_threshold,
                    persist=True, tracker=tracker_type, verbose=False,
                )
            except Exception as e:
                status_text.warning(f"Tracking hatası (frame {frame_idx}): {e}")
                continue

            out_frame = frame.copy()

            # ── Virtual line ──────────────────────────────────
            cv2.line(out_frame, (0, line_y), (width, line_y), (59, 130, 246), 3)
            cv2.putText(out_frame, "VIRTUAL LINE", (10, line_y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (59, 130, 246), 2)

            tr = track_results[0]
            if tr.boxes is not None and tr.boxes.id is not None:
                for box, track_id in zip(tr.boxes, tr.boxes.id):
                    obj_id   = int(track_id)
                    cls_id   = int(box.cls[0])
                    cls_name = tr.names.get(cls_id, "unknown")
                    conf_val = float(box.conf[0])
                    cx, cy   = _get_centroid(box)
                    color    = CLASS_COLORS.get(cls_name, DEFAULT_COLOR)

                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(out_frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(out_frame,
                                f"ID{obj_id} {cls_name} {conf_val:.2f}",
                                (x1, y1 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
                    cv2.circle(out_frame, (cx, cy), 4, color, -1)

                    # ── Line Crossing Logic ───────────────────
                    prev_cy = st.session_state.traffic_prev_positions.get(obj_id)
                    if (prev_cy is not None
                            and obj_id not in st.session_state.traffic_crossed_ids
                            and prev_cy > line_y >= cy):
                        st.session_state.traffic_crossed_ids.add(obj_id)
                        if cls_name in VEHICLE_CLASSES:
                            st.session_state.traffic_vehicles += 1
                        elif cls_name in PERSON_CLASS:
                            st.session_state.traffic_persons  += 1
                    st.session_state.traffic_prev_positions[obj_id] = cy

            # ── Counter overlay ───────────────────────────────
            overlay = out_frame.copy()
            cv2.rectangle(overlay, (0, 0), (width, 80), (10, 14, 26), -1)
            cv2.addWeighted(overlay, 0.8, out_frame, 0.2, 0, out_frame)
            cv2.putText(out_frame, f"Arac: {st.session_state.traffic_vehicles}",
                        (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (6, 182, 212), 2)
            cv2.putText(out_frame, f"Yaya: {st.session_state.traffic_persons}",
                        (230, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (16, 185, 129), 2)
            cv2.putText(out_frame,
                        f"FPS: {fps_live:.1f}  Frame: {frame_idx}/{int(max_frames)}",
                        (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 116, 139), 1)

            frame_display.image(cv_to_pil(out_frame), use_container_width=True)
            progress_bar.progress(min(frame_idx / max_frames, 1.0),
                                  text=f"Frame {frame_idx} / {int(max_frames)} işleniyor…")
            _refresh_kpi(fps_live)

    except Exception as e:
        st.error(f"❌ Video işleme hatası: {e}")
    finally:
        cap.release()
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    progress_bar.progress(1.0, text="✅ İşlem tamamlandı!")
    status_text.success(
        f"✅ Tamamlandı! {frame_idx} frame işlendi. "
        f"Araç: {st.session_state.traffic_vehicles} | "
        f"Yaya: {st.session_state.traffic_persons}"
    )


# ═══════════════════════════════════════════════════════════════════
# MODULE 3 — ERKEN UYARI YANGIN & DUMAN TESPİTİ
# ═══════════════════════════════════════════════════════════════════

FIRE_CLASSES  = {"fire", "flame", "alev", "yangin", "yangın"}
SMOKE_CLASSES = {"smoke", "duman"}


def _is_fire_or_smoke(cls_name: str):
    name_l = cls_name.lower()
    if any(fc in name_l for fc in FIRE_CLASSES):
        return True, "fire"
    if any(sc in name_l for sc in SMOKE_CLASSES):
        return True, "smoke"
    return False, ""


def module_fire_detection(conf_threshold: float, iou_threshold: float):
    st.markdown("""
    <div class="dashboard-header">
        <div>
            <span class="header-badge">MODÜL 3</span>
            <span class="header-badge" style="background:rgba(239,68,68,0.15);
              border-color:rgba(239,68,68,0.3);color:#ef4444;">YANGIN</span>
        </div>
        <h1>🔥 Erken Uyarı Yangın & Duman Tespiti</h1>
        <p>YOLOv8 ile gerçek zamanlı Yangın / Duman tespiti → Acil durum uyarı sistemi</p>
    </div>
    """, unsafe_allow_html=True)

    kpi_ph = st.empty()

    def _refresh_fire_kpi(total: int, fire: int, smoke: int, status: str):
        rate    = (fire + smoke) / max(total, 1) * 100
        s_color = "red" if status == "ALARM" else "green"
        s_icon  = "🔴" if status == "ALARM" else "🟢"
        kpi_ph.markdown(f"""
        <div class="kpi-grid">
            <div class="kpi-card {s_color}"><div class="kpi-icon">{s_icon}</div>
                <div class="kpi-value {s_color}" style="font-size:1.1rem;">{status}</div>
                <div class="kpi-label">Sistem Durumu</div></div>
            <div class="kpi-card red"><div class="kpi-icon">🔥</div>
                <div class="kpi-value red">{fire}</div><div class="kpi-label">Alev Frame</div></div>
            <div class="kpi-card orange"><div class="kpi-icon">💨</div>
                <div class="kpi-value orange">{smoke}</div><div class="kpi-label">Duman Frame</div></div>
            <div class="kpi-card blue"><div class="kpi-icon">📈</div>
                <div class="kpi-value blue">{rate:.1f}%</div><div class="kpi-label">Tehlike Oranı</div></div>
        </div>
        """, unsafe_allow_html=True)

    _refresh_fire_kpi(0, 0, 0, "HAZIR")

    st.markdown('<div class="section-title">📡 Kaynak Seçimi</div>', unsafe_allow_html=True)
    source_mode = st.radio(
        "Kaynak",
        ["🎞️  Video Dosyası", "📷  Görsel Dosyası"],
        horizontal=True, label_visibility="collapsed",
    )

    model, _, model_warn = load_yolo_model("best.pt")
    if model_warn:
        st.warning(model_warn)
    if model is None:
        st.error("❌ YOLO modeli yüklenemedi.")
        return

    st.markdown("""
    <div class="panel">
        <div style="font-size:0.85rem;color:#94a3b8;">
            <strong style="color:#ef4444;">⚠️ Algılama Mantığı:</strong><br>
            • <code>fire</code>, <code>flame</code>, <code>smoke</code>, <code>duman</code>
              sınıfları → <strong>ACİL DURUM</strong> uyarısı.<br>
            • Özel model (<code>best.pt</code>) varsa çok daha doğru sonuç verir.<br>
            • COCO yolov8n ile test ederken conf_threshold'u düşürün.
        </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded = None
    if "Video" in source_mode:
        uploaded = st.file_uploader("MP4 video yükleyin", type=["mp4", "avi", "mov"],
                                    key="fire_video_uploader")
    else:
        uploaded = st.file_uploader("PNG/JPG görsel yükleyin", type=["png", "jpg", "jpeg"],
                                    key="fire_image_uploader")

    if uploaded is None:
        st.markdown("""
        <div class="panel" style="text-align:center;padding:48px;color:#475569;">
            <div style="font-size:3rem;margin-bottom:12px;">🔥</div>
            <div style="font-size:1rem;font-weight:600;">Analiz için dosya yükleyin</div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Image mode ───────────────────────────────────────────────
    if "Görsel" in source_mode:
        img_pil = Image.open(uploaded).convert("RGB")
        img_bgr = pil_to_cv(img_pil)
        h_img, w_img = img_bgr.shape[:2]

        with st.spinner("🔍 Yangın/Duman tespiti yapılıyor..."):
            try:
                results = model.predict(source=img_bgr, conf=conf_threshold,
                                        iou=iou_threshold, verbose=False)
            except Exception as e:
                st.error(f"❌ Tahmin hatası: {e}")
                return

        result       = results[0]
        out_img      = img_bgr.copy()
        fire_det     = False
        smoke_det    = False
        detected_lst = []

        if result.boxes is not None:
            for box in result.boxes:
                cls_id   = int(box.cls[0])
                cls_name = result.names.get(cls_id, "")
                conf_val = float(box.conf[0])
                is_d, d_type = _is_fire_or_smoke(cls_name)
                if is_d:
                    color = (0, 0, 255) if d_type == "fire" else (128, 0, 200)
                    thick = 4
                    fire_det  = fire_det  or (d_type == "fire")
                    smoke_det = smoke_det or (d_type == "smoke")
                else:
                    color, thick = (100, 200, 100), 2
                draw_bbox(out_img, box.xyxy[0], f"{cls_name} {conf_val:.2f}", color, thick)
                detected_lst.append((cls_name, conf_val, d_type or "safe"))

        col_img, col_st = st.columns([3, 2])
        with col_img:
            st.markdown('<div class="section-title">🖼️ Sonuç</div>', unsafe_allow_html=True)
            st.image(cv_to_pil(out_img), use_container_width=True)

        with col_st:
            st.markdown('<div class="section-title">📡 Durum</div>', unsafe_allow_html=True)
            if fire_det:
                st.markdown("""
                <div class="alert-danger">
                    <div style="font-size:3rem;">🔥</div>
                    <h2>⚠️ ACİL DURUM</h2>
                    <p style="color:#fca5a5;margin:8px 0 0 0;">YANGIN TESPİT EDİLDİ!</p>
                </div>""", unsafe_allow_html=True)
                _refresh_fire_kpi(1, 1, 0, "ALARM")
            elif smoke_det:
                st.markdown("""
                <div class="alert-danger">
                    <div style="font-size:3rem;">💨</div>
                    <h2>⚠️ DUMAN TESPİT EDİLDİ</h2>
                    <p style="color:#fca5a5;margin:8px 0 0 0;">Yangın riski mevcut!</p>
                </div>""", unsafe_allow_html=True)
                _refresh_fire_kpi(1, 0, 1, "ALARM")
            else:
                st.markdown("""
                <div class="alert-safe">
                    <div style="font-size:3rem;">✅</div>
                    <h2>🟢 BÖLGE GÜVENLİ</h2>
                    <p style="color:#6ee7b7;margin:8px 0 0 0;">Yangın / Duman tespit edilmedi.</p>
                </div>""", unsafe_allow_html=True)
                _refresh_fire_kpi(1, 0, 0, "GÜVENLİ")

            if detected_lst:
                st.markdown("#### 🎯 Tespitler")
                for cn, cv, dt in detected_lst:
                    icon = "🔥" if dt == "fire" else ("💨" if dt == "smoke" else "✅")
                    st.markdown(f"{icon} **{cn}** — `{cv:.2%}`")
        return

    # ── Video mode ───────────────────────────────────────────────
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(uploaded.read())
        tmp_path = tmp.name

    max_fr = st.slider("Maks. Frame Sayısı", 30, 2000, 500, 30, key="fire_max_frames")
    if not st.button("▶️  Yangın Tespitini Başlat", use_container_width=True, type="primary"):
        st.info("▶️ Analizi başlatmak için butona basın.")
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
        return

    cap       = cv2.VideoCapture(tmp_path)
    vid_w     = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    vid_h     = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_fr  = 0
    fire_cnt  = 0
    smoke_cnt = 0

    st.markdown('<div class="section-title">📺 Canlı İşleme</div>', unsafe_allow_html=True)
    frame_disp = st.empty()
    alarm_box  = st.empty()
    prog_fire  = st.progress(0)
    status_txt = st.empty()

    try:
        while cap.isOpened() and total_fr < max_fr:
            ret, frame = cap.read()
            if not ret:
                break
            total_fr += 1

            try:
                res = model.predict(source=frame, conf=conf_threshold,
                                    iou=iou_threshold, verbose=False)
            except Exception:
                continue

            out_f     = frame.copy()
            f_fire    = False
            f_smoke   = False

            if res[0].boxes is not None:
                for box in res[0].boxes:
                    cls_id   = int(box.cls[0])
                    cls_name = res[0].names.get(cls_id, "")
                    conf_val = float(box.conf[0])
                    is_d, d_type = _is_fire_or_smoke(cls_name)
                    if is_d:
                        color = (0, 0, 255) if d_type == "fire" else (80, 0, 200)
                        thick = 5
                        f_fire  = f_fire  or (d_type == "fire")
                        f_smoke = f_smoke or (d_type == "smoke")
                    else:
                        color, thick = (100, 200, 100), 2
                    draw_bbox(out_f, box.xyxy[0],
                              f"{cls_name} {conf_val:.2f}", color, thick)

            if f_fire:
                fire_cnt += 1
                cv2.rectangle(out_f, (0, 0), (vid_w - 1, vid_h - 1), (0, 0, 255), 12)
                cv2.putText(out_f, "!! YANGIN ALARM !!", (20, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 0, 255), 4)
                alarm_box.markdown("""
                <div class="alert-danger">
                    <h2>⚠️ ACİL DURUM: YANGIN / DUMAN TESPİT EDİLDİ!</h2>
                </div>""", unsafe_allow_html=True)
            elif f_smoke:
                smoke_cnt += 1
                cv2.rectangle(out_f, (0, 0), (vid_w - 1, vid_h - 1), (60, 0, 180), 8)
                cv2.putText(out_f, "!! DUMAN ALARM !!", (20, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.4, (60, 0, 180), 4)
                alarm_box.markdown("""
                <div class="alert-danger">
                    <h2>⚠️ DUMAN TESPİT EDİLDİ! Yangın riski mevcut.</h2>
                </div>""", unsafe_allow_html=True)
            else:
                alarm_box.markdown("""
                <div class="alert-safe">
                    <h2>🟢 BÖLGE GÜVENLİ</h2>
                </div>""", unsafe_allow_html=True)

            frame_disp.image(cv_to_pil(out_f), use_container_width=True)
            prog_fire.progress(min(total_fr / max_fr, 1.0))
            _refresh_fire_kpi(
                total_fr, fire_cnt, smoke_cnt,
                "ALARM" if (f_fire or f_smoke) else "GÜVENLİ",
            )

    except Exception as e:
        st.error(f"❌ Video işleme hatası: {e}")
    finally:
        cap.release()
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    prog_fire.progress(1.0)
    danger_rate = (fire_cnt + smoke_cnt) / max(total_fr, 1) * 100
    if fire_cnt > 0 or smoke_cnt > 0:
        status_txt.error(
            f"🔥 Analiz tamamlandı! {total_fr} frame incelendi. "
            f"Alev: {fire_cnt} | Duman: {smoke_cnt} | Tehlike: {danger_rate:.1f}%"
        )
    else:
        status_txt.success(
            f"✅ Analiz tamamlandı. {total_fr} frame incelendi. Herhangi bir tehlike tespit edilmedi."
        )


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    dep_status = check_dependencies()
    module, conf_threshold, iou_threshold = render_sidebar(dep_status)

    if "OCR" in module:
        module_ocr_quality(conf_threshold, iou_threshold)
    elif "Trafik" in module:
        module_traffic(conf_threshold, iou_threshold)
    elif "Yangın" in module:
        module_fire_detection(conf_threshold, iou_threshold)


if __name__ == "__main__":
    main()
