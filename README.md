# 🧊 MyFridge - AI-Powered Kitchen Assistant

**Demo 1 (D1)** - A smart fridge inventory app with AI-powered meal planning for students.

![MyFridge](https://img.shields.io/badge/Status-Demo%201-blue)
![Stack](https://img.shields.io/badge/Stack-FastAPI%20%2B%20React-green)

## 🎯 Features

- ✅ **Inventory Management** - Track what's in your fridge, freezer, and pantry
- ✅ **Expiration Tracking** - Visual warnings for expiring and expired items
- ✅ **AI Chef Chat** - Ask for recipes based on your available ingredients
- ✅ **Smart Suggestions** - AI prioritizes soon-to-expire items in recipes

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key (optional, for AI features)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment (copy and edit)
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run the server
uvicorn app.main:app --reload
```

Backend runs at: http://localhost:8000

API docs: http://localhost:8000/docs

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

Frontend runs at: http://localhost:5173

## 📁 Project Structure

```
MyFridge/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── main.py         # App entry point
│   │   ├── models.py       # Database models
│   │   ├── schemas.py      # Pydantic schemas
│   │   ├── database.py     # DB connection
│   │   ├── routes/         # API endpoints
│   │   │   ├── inventory.py
│   │   │   └── chat.py
│   │   └── services/       # Business logic
│   │       ├── inventory_service.py
│   │       └── ai_chef.py
│   └── requirements.txt
│
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── api/           # API client
│   │   └── App.jsx
│   └── package.json
│
└── README.md
```

## 🔌 API Endpoints

### Inventory

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/inventory/` | Get all items |
| POST | `/api/inventory/` | Add new item |
| GET | `/api/inventory/{id}` | Get single item |
| PUT | `/api/inventory/{id}` | Update item |
| DELETE | `/api/inventory/{id}` | Delete item |
| GET | `/api/inventory/expiring?days=3` | Get expiring items |
| GET | `/api/inventory/expired` | Get expired items |

### AI Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/` | Send message to AI Chef |
| GET | `/api/chat/meal-plan` | Get AI meal plan |
| GET | `/api/chat/quick-recipe?meal_type=dinner` | Quick recipe suggestion |

## 🛠️ Tech Stack

- **Backend**: FastAPI, SQLAlchemy, SQLite, OpenAI API
- **Frontend**: React 18, Vite, React Router, Lucide Icons
- **Styling**: CSS Modules with custom dark theme

## 🚢 Deployment

### Railway (Backend)

1. Push to GitHub
2. Connect repo to Railway
3. Add environment variables (`OPENAI_API_KEY`)
4. Deploy!

### Vercel (Frontend)

1. Push to GitHub
2. Import project to Vercel
3. Set build command: `npm run build`
4. Set output directory: `dist`
5. Add environment variable for API URL if needed
6. Deploy!

## 📝 Demo Script

1. **Show empty fridge** - "Your fridge is empty!"
2. **Add items** - Milk, eggs, chicken, vegetables with expiry dates
3. **Show expiry warnings** - Items turn yellow/red as they expire
4. **Chat with AI Chef** - "What can I cook for dinner?"
5. **Get meal plan** - AI suggests recipes using available ingredients

## 🔮 Future Roadmap (D2+)

- [ ] Voice input for adding items
- [ ] Receipt scanning (OCR)
- [ ] Push notifications for expiring items
- [ ] User accounts & authentication
- [ ] Mobile app (React Native)
- [ ] Barcode scanning

---

Built with 💙 for students who want to cook smarter

