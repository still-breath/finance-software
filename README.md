<div align="center">
<h1>💰 FINANCE DESKTOP APP</h1>
<h3>Personal Finance Management System with AI Categorization</h3>
<a href="#preview"><img src="./thumbnail.png" height="280" alt="finance-app-dashboard"></a>
</div>

<p align="center">
<a target="_blank" href="https://www.linkedin.com/in/syahrulahmad/"><img height="20" src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" /></a>
<a target="_blank" href="https://github.com/still-breath/finance-app-golang"><img height="20" src="https://img.shields.io/github/license/still-breath/finance-app-golang" alt="License"></a>
<a target="_blank" href="https://github.com/still-breath/finance-app-golang"><img height="20" src="https://img.shields.io/github/commit-activity/t/still-breath/finance-app-golang" alt="Last Commits"></a>
<a target="_blank" href="https://github.com/still-breath/finance-app-golang"><img height="20" src="https://img.shields.io/github/repo-size/still-breath/finance-app-golang" alt="Repo Size"></a>
</p>

<div align="center">
<h2>🔒 SECURITY / ENV SETUP</h2>
<p><strong>⚠️ Set required environment variables before running backend.</strong></p>
<p>� Minimal: <code>JWT_SECRET</code> · <code>DATABASE_DSN</code> · <code>AI_SERVICE_URL</code></p>
<p>�️ See <code>docker-compose.yml</code> & <code>init.sql</code> for DB context.</p>
</div>

<p align="center">
<a href="#-introduction--pendahuluan">Introduction</a> &nbsp;•&nbsp;
<a href="#-tech-stack">Tech Stack</a> &nbsp;•&nbsp;
<a href="#-preview">Preview</a> &nbsp;•&nbsp;
<a href="#-installation--usage">Install & Run</a> &nbsp;•&nbsp;
<a href="#-api-endpoints-core">API</a> &nbsp;•&nbsp;
<a href="#-ai-model-training">AI Training</a> &nbsp;•&nbsp;
<a href="#-issues--kontribusi">Issues</a> &nbsp;•&nbsp;
<a href="#-license">License</a> &nbsp;•&nbsp;
<a href="#-author">Author</a>
</p>

---

## 📄 Introduction / Pendahuluan

EN: A modern, container-friendly personal finance system. Primary interface is a **PyQt5 desktop app** powered by a **Go REST API** and a **Python AI categorizer** (ML + fallback keyword rules). Tracks income, expenses, categories, trends, and gives AI-based suggestions.

ID: Aplikasi manajemen keuangan pribadi dengan fokus **desktop PyQt5**. Backend Go (REST API + statistik). Layanan AI Python memberi saran kategori otomatis (model ML + fallback kata kunci). Mendukung pencatatan, laporan, tren bulanan, dan re-kategorisasi.

### Ecosystem
- 🖥️ PyQt5 Desktop (utama)
- 🧠 Python AI Categorizer (`categorizer-ai-service`)
- 🚀 Go Backend API (`finance-backend-go`)
- (Opsional / Legacy) React frontend (tidak diprioritaskan)

### 🎯 Key Features
| Area | Highlights |
|------|-----------|
| Auth | JWT login/register (desktop uses `/api/v1/auth/*`) |
| Transactions | CRUD, batch recategorize, create categories |
| AI | Logistic Regression TF‑IDF + keyword fallback, confidence score |
| Reports | Monthly & summary stats (`/api/v1/stats/*`) |
| UX | Ctrl+N/R/F, styled calendar, debounced search |
| Architecture | Go + Python + PyQt5, Docker ready |
| Resilience | Graceful AI fallback (no model → keyword) |

> If model files (`models/model.pkl`, `models/vectorizer.pkl`) missing, system uses keyword rules.

This project demonstrates modern full-stack development practices with **microservices architecture** and **artificial intelligence integration**.

---

## 💻 Tech Stack

Frameworks, Libraries, and Tools used in this project:

<p align="center">
<a target="_blank" href="https://www.riverbankcomputing.com/static/Docs/PyQt5/">
<img height="30" src="https://img.shields.io/badge/PyQt5-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PyQt5"/>
</a>
<a target="_blank" href="https://matplotlib.org/">
<img height="30" src="https://img.shields.io/badge/Matplotlib-11557c?style=for-the-badge&logo=plotly&logoColor=white" alt="Matplotlib"/>
</a>
</a>
</p>

<p align="center">
<a target="_blank" href="https://golang.org/">
<img height="30" src="https://img.shields.io/badge/Go-00ADD8?style=for-the-badge&logo=go&logoColor=white" alt="Go"/>
</a>
<a target="_blank" href="https://www.python.org/">
<img height="30" src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
</a>
</p>

<p align="center">
<a target="_blank" href="https://www.postgresql.org/">
<img height="30" src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
</a>
<a target="_blank" href="https://scikit-learn.org/">
<img height="30" src="https://img.shields.io/badge/scikit_learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" alt="scikit-learn"/>
</a>
<a target="_blank" href="https://www.docker.com/">
<img height="30" src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"/>
</a>
</p>

---

## 🖼️ Preview

<div align="center">
<img src="./preview.png" alt="Finance App Dashboard" width="80%">
</div>

### 🧩 Desktop Dashboard Highlights
- Financial Overview Cards (Income, Transactions, Categories, Averages)
- Monthly Trends Line Chart (horizontal x-axis labels)
- Last 6 Months Compact Table
- AI Suggestion Banner in Add Transaction dialog
- Styled Calendar (red weekends, white theme)

### ➕ Additional Capabilities
- Smart Categorization (Health, Education, Food, Shopping, etc.)
- Indonesian language support
- Keyboard Shortcuts (Ctrl+R refresh, Ctrl+N add, Ctrl+F search)
- Optimized Debounced Refresh
- Desktop-first UX (no browser required for main client)

### 📈 Indicative Targets (Local Dev)
- API latency: < 200 ms
- Model accuracy (sample data): ~90–95%
- Cold start desktop: < 2s (after services up)

> Actual metrics depend on dataset & environment.

---

## ⚙️ Installation & Usage

### 📋 Prerequisites
Needed for Desktop + Backend + AI:
1. Docker & Docker Compose (recommended)
2. Go 1.23+ (if not using docker for backend)
3. Python 3.10+ (AI + desktop)
4. Node.js 18+ (optional legacy frontend)

### 🔧 Step-by-Step Installation (All Services)

#### 1. Clone Repository
```bash
# Clone the repository
git clone https://github.com/still-breath/finance-app-golang.git
cd finance-app-golang
```

#### 2. Environment Variables
Create `.env`:
```env
JWT_SECRET=replace_with_strong_secret
DATABASE_DSN=postgres://postgres:postgres@db:5432/finance_db?sslmode=disable
AI_SERVICE_URL=http://categorizer-ai:5000
PORT=8080
```
Local (no docker):
```env
DATABASE_DSN=host=localhost user=postgres password=postgres dbname=finance_db port=5432 sslmode=disable
AI_SERVICE_URL=http://localhost:5000
```

#### 3. Run with Docker
```bash
docker-compose up --build
# or
docker-compose up -d --build
```
Starts: PostgreSQL · Go API · AI service. Run desktop separately.

#### 4. Local Dev (Manual)
```bash
# Backend
cd finance-backend-go
go mod download
go run .

# AI Service
cd ../categorizer-ai-service
pip install -r requirements.txt
python app.py

# (Optional) Train / retrain
python ../train.py

# Desktop (new shell)
python finance-desktop-app/main.py
```

### 🚀 Usage (Desktop)

#### Access Summary
| Component | URL / Command |
|-----------|---------------|
| Desktop (PyQt5) | `python finance-desktop-app/main.py` |
| Backend API | http://localhost:8080 |
| Backend Health | http://localhost:8080/health |
| AI Service | http://localhost:5000/health |
| Legacy React (optional) | http://localhost:5173 |

#### Using the Desktop Application:
1. Start Backend & AI (Docker or local)
2. Run Desktop App: `python finance-desktop-app/main.py`
3. Login / Register
4. Add Transactions (Ctrl+N)
5. Refresh / Search (Ctrl+R / Ctrl+F)
6. Open Reports tab for charts & 6‑month summary

### 📁 Project Structure (Simplified)
```
finance-software/
├── categorizer-ai-service/    # Flask AI service (/categorize, /health)
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── models/
├── data/                      # training_data.xlsx
├── finance-backend-go/        # Go API (/api/v1/...)
│   ├── main.go
│   ├── ai_client.go
│   ├── transaction_handlers.go
│   ├── additional_handlers.go
│   ├── handlers.go
│   ├── models.go
│   └── database.go
├── finance-desktop-app/       # PyQt5 desktop client
│   ├── main.py
│   ├── src/api/client.py
│   ├── src/ui/*
│   └── tests/*
├── models/                    # Alternate model artifact location
├── train.py                   # Training script
├── docker-compose.yml
├── init.sql
└── README.md
```

---

## 📡 API Endpoints (Core)

### 🔐 Auth
```bash
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/profile
```

### 💳 Transactions
```bash
GET    /api/v1/transactions
POST   /api/v1/transactions
GET    /api/v1/transactions/:id
PUT    /api/v1/transactions/:id
DELETE /api/v1/transactions/:id
PUT    /api/v1/transactions/:id/recategorize
POST   /api/v1/transactions/batch-recategorize
```

### 📊 Stats & Categories
```bash
GET /api/v1/stats/summary
GET /api/v1/stats/monthly
GET /api/v1/categories
POST /api/v1/categories
GET /api/v1/categories/stats
GET /api/v1/categories/suggest   # (if implemented)
```

### 🤖 AI Service (Direct)
```bash
POST /categorize
POST /categorize/batch
GET  /health
```

> Swagger not exposed yet (only /health). Add gin-swagger if needed.

---

## 🧠 AI Model Training

### 📚 Dataset
File: `data/training_data.xlsx` → columns: `description`, `category`.

### 🔄 Retrain
```bash
# Docker
docker-compose run --rm categorizer-ai python train.py
docker-compose restart categorizer-ai

# Local
python train.py         # writes models/*.pkl
```
Artifacts:
- models/model.pkl
- models/vectorizer.pkl
- models/metadata.pkl

### 🎯 Model Notes
- Logistic Regression TF‑IDF (unigram+bigram)
- Accuracy depends on dataset balance
- Indo + English mixed supported
- Keyword fallback ensures resilience

---

## 🚩 Issues / Kontribusi

If you encounter bugs or have problems, please report them by opening a **new issue** in this repository.

### 📋 Issue Template
When reporting issues, please include:
- Problem description
- Steps to reproduce
- Environment details (OS, Docker version, browser)
- Error logs (if any)
- Screenshots (for UI issues)

### 🔍 Troubleshooting
| Problem | Cause | Fix |
|---------|-------|-----|
| 401 Unauthorized | Missing / expired JWT | Re-login (desktop auto-handles token) |
| AI fallback only | model/vectorizer missing | Run training; ensure files in `categorizer-ai-service/models/` |
| DB init errors | Wrong DSN / container not ready | Check Postgres logs; confirm `DATABASE_DSN` |
| Slow first classify | Cold model load | Subsequent calls faster |
| No GUI on remote | No display server | Use local machine / X11 forwarding |

### Enhancement Ideas
- Add Swagger (`gin-swagger`)
- Budget planning & alerts
- PyInstaller packaging for desktop
- gRPC or async AI service
- Multi-user role & audit logs

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 📌 Author

<div align="center">
<h3>🧑‍💻 Syahrul Fathoni Ahmad</h3>
<p><em>Full Stack Developer | AI Engineer | Financial Technology Researcher</em></p>

<p>
<a target="_blank" href="https://www.linkedin.com/in/syahrulahmad/">
<img height="25" src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="linkedin" />
</a>
<a target="_blank" href="https://github.com/still-breath">
<img height="25" src="https://img.shields.io/badge/Github-000000?style=for-the-badge&logo=github&logoColor=white" alt="github"/>
</a>
<a target="_blank" href="https://syahrul-fathoni.vercel.app">
<img height="25" src="https://img.shields.io/badge/Portfolio-00BC8E?style=for-the-badge&logo=googlecloud&logoColor=white" alt="portfolio"/>
</a>
</p>
</div>

---

<div align="center">
<p><strong>⭐ Star this repo if helpful!</strong></p>
<p><em>Built for pragmatic personal finance + ML experimentation.</em></p>
</div>