# 🏙️ MultiVision AI — Smart City & Industrial Security Dashboard

> **Tam teşekküllü, üretim hazır Streamlit uygulaması**  
> YOLOv8 · PaddleOCR · ByteTrack · Real-time Video Analytics

---

## 📦 Özellikler

### 🏭 Modül 1 — Endüstriyel Ambalaj OCR & Kalite Kontrol
- PNG/JPG yükleme
- YOLOv8 ile ambalaj ROI tespiti (`best.pt` → fallback `yolov8n.pt`)
- PaddleOCR ile metin çıkarımı
- Regex ile **Ürün Adı** ve **Gramaj** tespiti
- Sonuçları **Excel (.xlsx)** olarak indirme

### 🚦 Modül 2 — Akıllı Trafik & Yaya Takibi (Line Crossing)
- MP4/AVI/MOV video yükleme
- YOLOv8 + ByteTrack ID tabanlı takip (`model.track(persist=True)`)
- Sanal yatay çizgi (Virtual Line) mantığı
- **Araç** ve **Yaya** sayacı (ID bazlı, çift sayım yok)
- Canlı FPS ve frame sayacı

### 🔥 Modül 3 — Erken Uyarı Yangın & Duman Tespiti
- Video veya Görsel yükleme
- `fire`, `flame`, `smoke`, `duman` sınıfı tespitinde **ACİL DURUM** uyarısı
- Kırmızı kalın bounding box + animasyonlu alarm paneli
- Güvenli durum: **🟢 BÖLGE GÜVENLİ** yeşil panel

---

## 🚀 Kurulum & Çalıştırma

### 1. Sanal Ortam Oluşturun (Önerilir)
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
```

### 2. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

> **Not:** PaddleOCR büyük bir kütüphanedir (~500 MB). GPU'nuz varsa:
> ```bash
> pip install paddlepaddle-gpu
> ```

### 3. Uygulamayı Başlatın
```bash
streamlit run app.py
```

Tarayıcıda otomatik açılır: `http://localhost:8501`

---

## 🧠 Özel Model Kullanımı

Kendi YOLOv8 modelinizi kullanmak için `best.pt` dosyanızı proje kök dizinine koyun:

```
MultiVision AI/
├── app.py
├── best.pt          ← Buraya koyun
├── requirements.txt
└── README.md
```

Model bulunamazsa otomatik olarak `yolov8n.pt` (COCO pretrained) indirilir.

---

## ⚙️ Konfigürasyon

Sol menü (Sidebar) üzerinden:

| Ayar | Açıklama | Varsayılan |
|------|----------|-----------|
| Confidence Eşiği | Tespit güven eşiği | 0.40 |
| IoU Eşiği (NMS) | Non-maximum suppression eşiği | 0.45 |

---

## 🗂️ Proje Yapısı

```
MultiVision AI/
├── app.py              # Ana uygulama (tüm modüller)
├── best.pt             # Özel YOLOv8 modeli (opsiyonel)
├── requirements.txt    # Python bağımlılıkları
└── README.md           # Bu dosya
```

---

## 🛠️ Teknik Mimari

```
app.py
├── GLOBAL_CSS          — Dark Mode UI sistemi
├── load_yolo_model()   — @st.cache_resource ile YOLO yükleme
├── load_ocr_engine()   — @st.cache_resource ile PaddleOCR yükleme
├── check_dependencies()— Bağımlılık kontrolü
├── render_sidebar()    — Sol panel, modül geçişi, config
├── module_ocr_quality()— Modül 1: OCR & Kalite Kontrol
├── module_traffic()    — Modül 2: Trafik Takibi
├── module_fire_detection()— Modül 3: Yangın Tespiti
└── main()              — Routing
```

---

## 📋 Gereksinimler

- Python 3.9+
- Windows / Linux / macOS
- Minimum 8 GB RAM (PaddleOCR için)
- GPU opsiyonel (CPU'da da çalışır, daha yavaş)

---

## 📄 Lisans

MIT License — Serbest kullanım, değiştirme ve dağıtım.
