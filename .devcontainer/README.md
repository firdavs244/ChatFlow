# ChatFlow - GitHub Codespaces Setup

Bu loyiha GitHub Codespaces'da ishga tushirish uchun tayyorlangan.

## 🚀 Quick Start

1. **Codespace yaratish:**
   - GitHub repository'da "Code" tugmasini bosing
   - "Codespaces" tab'ini tanlang
   - "Create codespace on main" tugmasini bosing

2. **Kutish:**
   - Codespace yuklanishini kuting (2-3 daqiqa)
   - Barcha konteynerlar avtomatik ishga tushadi

3. **Foydalanish:**
   - Frontend: Ports tab'ida `3000` portini oching
   - Backend API: `8000` portida mavjud
   - MinIO Console: `9001` portida
   - Grafana: `3001` portida

## 📋 Ports

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | Next.js application |
| Backend API | 8000 | FastAPI REST API |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache & Pub/Sub |
| MinIO API | 9000 | S3 API |
| MinIO Console | 9001 | Web UI |
| Prometheus | 9090 | Metrics |
| Grafana | 3001 | Dashboards |

## 🔧 Manual Start (if needed)

Agar konteynerlar avtomatik ishga tushmasa:

```bash
docker compose -f docker-compose.codespaces.yml up -d
```

## 📝 Notes

- Barcha environment variables `.env.codespaces` faylida
- Portlar avtomatik forward qilinadi
- Database va Redis data Codespace'da saqlanadi

