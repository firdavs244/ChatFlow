# 🚀 ChatFlow - Professional Real-time Chat Application

<div align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
</div>

<br />

Professional darajadagi real-time chat ilovasi - Telegram, WhatsApp, Messenger uslubida.

## ✨ Xususiyatlar

### 💬 Messaging
- ✅ Real-time xabar almashish (WebSocket)
- ✅ Shaxsiy chatlar (1-to-1)
- ✅ Guruhli chatlar
- ✅ Kanallar (broadcast)
- ✅ Xabarga javob berish (Reply)
- ✅ Xabarni tahrirlash va o'chirish
- ✅ Emoji reaktsiyalar
- ✅ Typing indicator (yozmoqda...)
- ✅ Read receipts (o'qildi belgilari)
- ✅ Xabarlarni qidirish

### 📎 Media & Files
- ✅ Rasm, video, audio yuklash
- ✅ Fayl almashish (PDF, ZIP, etc.)
- ✅ MinIO bilan S3-compatible storage
- ✅ Thumbnail generation

### 👥 Users & Groups
- ✅ Foydalanuvchi profili
- ✅ Online/Offline status
- ✅ Last seen (oxirgi faollik)
- ✅ Guruh yaratish va boshqarish
- ✅ Admin/Member rollar
- ✅ Invite link orqali qo'shilish

### 🔐 Security
- ✅ JWT authentication
- ✅ Password hashing (bcrypt)
- ✅ Rate limiting
- ✅ CORS protection

### 📊 Monitoring
- ✅ Prometheus metrics
- ✅ Grafana dashboards
- ✅ Health checks

## 🏗️ Arxitektura

```
┌─────────────────────────────────────────────────────────────────┐
│                         NGINX (Load Balancer)                   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐     ┌─────────────────┐     ┌───────────────┐
│   Frontend    │     │     Backend     │     │    MinIO      │
│   (Next.js)   │     │    (FastAPI)    │     │  (S3 Storage) │
└───────────────┘     └────────┬────────┘     └───────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  PostgreSQL   │     │     Redis     │     │    Celery     │
│   (Database)  │     │ (Cache/PubSub)│     │   (Tasks)     │
└───────────────┘     └───────────────┘     └───────────────┘
```

## 🛠️ Texnologiyalar

| Komponent | Texnologiya |
|-----------|-------------|
| **Backend** | FastAPI, Python 3.12, SQLAlchemy 2.0 |
| **Frontend** | Next.js 14, React 18, TypeScript |
| **Database** | PostgreSQL 16 |
| **Cache** | Redis 7 |
| **File Storage** | MinIO (S3-compatible) |
| **Task Queue** | Celery + Redis |
| **Reverse Proxy** | Nginx |
| **Monitoring** | Prometheus + Grafana |
| **Containerization** | Docker + Docker Compose |

## 🚀 Ishga tushirish

### 📦 Variant 1: GitHub Codespaces (Tavsiya etiladi)

**Eng oson usul - bir necha bosqich:**

1. GitHub repository'da **"Code"** tugmasini bosing
2. **"Codespaces"** tab'ini tanlang
3. **"Create codespace on main"** tugmasini bosing
4. 2-3 daqiqada barcha service'lar avtomatik ishga tushadi
5. Ports tab'ida portlarni oching va foydalaning

**Ports:**
- Frontend: `3000`
- Backend API: `8000`
- MinIO Console: `9001`
- Grafana: `3001`

**Qo'shimcha ma'lumot:** `.devcontainer/README.md` fayliga qarang

---

### 🐳 Variant 2: Docker Compose (Local)

**Talablar:**
- Docker va Docker Compose
- Git

**1. Repozitoriyani clone qilish:**
```bash
git clone https://github.com/firdavs244/ChatFlow.git
cd ChatFlow
```

**2. Environment faylini yaratish:**
```bash
cp .env.example .env  # yoki manual yarating
```

**3. Docker Compose orqali ishga tushirish:**
```bash
# Development mode
docker-compose up -d

# Loglarni ko'rish
docker-compose logs -f
```

### 3. Ilovaga kirish

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| **Backend API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |
| **MinIO Console** | http://localhost:9001 |
| **Grafana** | http://localhost:3001 |
| **Prometheus** | http://localhost:9090 |

### Default credentials

**MinIO:**
- Username: `chatflow_minio`
- Password: `minio_secure_password_2024`

**Grafana:**
- Username: `admin`
- Password: `chatflow_grafana_2024`

## 📁 Loyiha tuzilmasi

```
chat-app/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── core/           # Config, security, database
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── routers/        # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── websocket/      # WebSocket handlers
│   │   └── main.py         # Application entry
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                # Next.js frontend
│   ├── src/
│   │   ├── app/            # Next.js app router
│   │   ├── components/     # React components
│   │   ├── lib/            # Utilities, API client
│   │   ├── store/          # Zustand state management
│   │   └── types/          # TypeScript types
│   ├── Dockerfile
│   └── package.json
│
├── nginx/                   # Nginx configuration
├── monitoring/              # Prometheus & Grafana
├── docker-compose.yml       # Docker orchestration
└── .env                     # Environment variables
```

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Ro'yxatdan o'tish |
| POST | `/api/v1/auth/login` | Kirish |
| POST | `/api/v1/auth/refresh` | Token yangilash |
| POST | `/api/v1/auth/logout` | Chiqish |
| GET | `/api/v1/auth/me` | Joriy foydalanuvchi |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/search` | Foydalanuvchilarni qidirish |
| GET | `/api/v1/users/{id}` | Profil olish |
| PUT | `/api/v1/users/me` | Profilni yangilash |

### Chats
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/chats/` | Chatlar ro'yxati |
| POST | `/api/v1/chats/` | Yangi chat yaratish |
| GET | `/api/v1/chats/{id}` | Chat ma'lumotlari |
| PUT | `/api/v1/chats/{id}` | Chatni yangilash |
| DELETE | `/api/v1/chats/{id}` | Chatni o'chirish |

### Messages
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/messages/chat/{id}` | Xabarlar ro'yxati |
| POST | `/api/v1/messages/` | Xabar yuborish |
| PUT | `/api/v1/messages/{id}` | Xabarni tahrirlash |
| DELETE | `/api/v1/messages/{id}` | Xabarni o'chirish |
| POST | `/api/v1/messages/{id}/reactions` | Reaktsiya qo'shish |

### WebSocket
```
ws://localhost:8000/ws?token=<access_token>
```

**Events:**
- `message.new` - Yangi xabar
- `message.update` - Xabar yangilandi
- `message.delete` - Xabar o'chirildi
- `typing.start` / `typing.stop` - Typing indicator
- `user.online` / `user.offline` - Online status

## 🧪 Development

### Backend development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend development
```bash
cd frontend
npm install
npm run dev
```

## 📈 Kelajakdagi rejalar

- [ ] Voice/Video qo'ng'iroqlar (WebRTC)
- [ ] End-to-end encryption
- [ ] Message scheduling
- [ ] Bots API
- [ ] Mobile apps (React Native)
- [ ] Desktop apps (Electron)

## 📝 License

MIT License

---

<div align="center">
  <p></p>
</div>

