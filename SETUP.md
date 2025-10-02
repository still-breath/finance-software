# Finance App Go

Personal Finance Management Application dengan AI-powered transaction categorization.

## 🚧 Setup Requirements

**PENTING**: Aplikasi ini memerlukan konfigurasi khusus sebelum bisa dijalankan. Ikuti langkah setup di bawah ini.

## 📋 Prerequisites

- Docker & Docker Compose
- Python 3.11+ (untuk training model)
- Go 1.19+ (untuk development)

## 🔧 Setup Instructions

### 1. Clone Repository
```bash
git clone https://github.com/still-breath/finance-app-go.git
cd finance-app-go
```

### 2. Setup Configuration Files
```bash
# Copy template files
cp docker-compose.example.yml docker-compose.yml
cp finance-backend-go/.env.example finance-backend-go/.env
cp categorizer-ai-service/.env.example categorizer-ai-service/.env
```

### 3. Configure Environment Variables

#### Edit `finance-backend-go/.env`:
```bash
# WAJIB diganti untuk keamanan!
JWT_SECRET=your-very-secure-jwt-secret-here
DATABASE_DSN=host=postgres user=postgres password=YOUR_SECURE_DB_PASSWORD dbname=finance_db port=5432 sslmode=disable TimeZone=Asia/Jakarta
```

#### Edit `docker-compose.yml`:
Ganti semua password default:
```yaml
POSTGRES_PASSWORD: YOUR_SECURE_DB_PASSWORD
```

### 4. Train AI Model (REQUIRED)
```bash
python train.py
```
File model akan dibuat di folder `models/`

### 5. Run Application
```bash
docker-compose up --build
```

## 🔐 Security Configuration

**PENTING**: Sebelum menjalankan, pastikan mengganti:

- ✅ JWT_SECRET dengan nilai yang aman (minimum 32 karakter)
- ✅ Database password di semua tempat
- ✅ Semua placeholder password

## 📚 API Endpoints

Setelah aplikasi berjalan:
- **Backend API**: http://localhost:8080
- **AI Service**: http://localhost:5000
- **Database**: localhost:5432
- **Health Check**: http://localhost:8080/health

### Authentication
```bash
# Register
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}'

# Login
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}'
```

## 🛠 Development

### Backend (Go)
```bash
cd finance-backend-go
go mod download
go run .
```

### AI Service (Python)
```bash
cd categorizer-ai-service
pip install -r requirements.txt
python app.py
```

## 🚀 Production Deployment

1. Set environment variables:
   - `GIN_MODE=release`
   - `FLASK_ENV=production`
2. Gunakan strong passwords dan secrets
3. Setup SSL certificates
4. Configure firewall rules
5. Setup monitoring dan logging

## 📄 Project Structure

```
├── finance-backend-go/      # Go REST API
├── categorizer-ai-service/  # Python AI Service
├── finance-frontend/        # React Frontend (optional)
├── models/                  # AI Models (generated)
├── data/                    # Training data
└── init.sql                 # Database schema
```

## ⚠️ Troubleshooting

### Database Connection Issues
```bash
# Check if containers are running
docker-compose ps

# Check logs
docker-compose logs postgres
docker-compose logs finance-backend
```

### AI Service Issues
```bash
# Retrain model
python train.py

# Check AI service logs
docker-compose logs categorizer-ai
```

## 📝 License

Private Project - All Rights Reserved

---

**Note**: File konfigurasi dengan password dan secret tidak disertakan dalam repository untuk keamanan. Ikuti setup instructions di atas.