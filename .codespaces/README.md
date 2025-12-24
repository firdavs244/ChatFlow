# GitHub Codespaces uchun qo'shimcha ma'lumotlar

## 🎯 Codespaces'da ishga tushirish

### Avtomatik ishga tushish

1. Repository'da **"Code"** tugmasini bosing
2. **"Codespaces"** tab'ini tanlang
3. **"Create codespace on main"** tugmasini bosing
4. 2-3 daqiqada barcha service'lar ishga tushadi

### Port Forwarding

Codespaces avtomatik ravishda quyidagi portlarni forward qiladi:
- **3000** - Frontend (Next.js)
- **8000** - Backend API (FastAPI)
- **9001** - MinIO Console
- **3001** - Grafana

### Terminal orqali ishga tushirish

Agar avtomatik ishga tushmasa:

```bash
# Environment faylini yaratish (agar yo'q bo'lsa)
cp .env.codespaces .env

# Konteynerlarni ishga tushirish
docker compose -f docker-compose.codespaces.yml up -d

# Loglarni ko'rish
docker compose -f docker-compose.codespaces.yml logs -f

# Konteynerlarni to'xtatish
docker compose -f docker-compose.codespaces.yml down
```

### Ma'lumotlar bazasini tekshirish

```bash
# PostgreSQL'ga ulanish
docker compose -f docker-compose.codespaces.yml exec postgres psql -U chatflow -d chatflow_db

# Redis'ga ulanish
docker compose -f docker-compose.codespaces.yml exec redis redis-cli -a redis_secure_password_2024
```

### Frontend va Backend'ni alohida ishga tushirish

Agar Docker Compose ishlamasa, alohida ham ishga tushirish mumkin:

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Troubleshooting

**Port allaqachon ishlatilmoqda:**
```bash
# Port'ni topish va o'chirish
lsof -ti:8000 | xargs kill -9
```

**Docker images qayta build qilish:**
```bash
docker compose -f docker-compose.codespaces.yml build --no-cache
docker compose -f docker-compose.codespaces.yml up -d
```

**Loglarni tozalash:**
```bash
docker compose -f docker-compose.codespaces.yml down -v
docker compose -f docker-compose.codespaces.yml up -d
```

