
# 🃏 Absurdly Correct

> **An absurd, questionably correct card game to enjoy with friends.**

---

## 🔥 Demo
![Screenshot 2025-04-13 at 16-40-48 Vite React](https://github.com/user-attachments/assets/ccdc5c1c-ea58-4e6a-9b28-47ee15e59d4f)
![Screenshot 2025-04-13 at 16-40-28 Vite React](https://github.com/user-attachments/assets/fc06ef1f-ff0a-4c33-9fe7-cfdb76b3a5eb)
![Screenshot 2025-04-13 at 16-39-56 Vite React](https://github.com/user-attachments/assets/5a146bc1-b6ad-48a0-a000-6482b2b72b1b)
![Screenshot 2025-04-13 at 16-39-37 Vite React](https://github.com/user-attachments/assets/0dfb1bac-5be8-4670-b717-202804a7b700)
![Screenshot 2025-04-13 at 16-40-11 Vite React](https://github.com/user-attachments/assets/cd11d043-752e-41db-860c-186c8745f21e)

---

## 🚀 Tech Stack

- **Frontend**: React + TypeScript + Vite
- **Backend**: FastAPI + WebSockets
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy + asyncpg
- **Testing**: Pytest + pytest-asyncio
- **DevOps**: Docker + Docker Compose

---

## 📦 Local Installation (without Docker)

```bash
# 1. Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# 2. Frontend
cd ../frontend
npm install
npm run dev
```

---

## 🐳 Docker Compose Setup

```bash
docker-compose up --build
```

Access:
- Frontend: [http://localhost:3000](http://localhost:3000)
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Database: PostgreSQL on `localhost:5432` (user: `absurdly`, password: `correct`)

---

## 🎮 How to Play

1. Run the project (locally or via Docker)
2. Open the frontend in your browser
3. Create a new game or join an existing one
4. Players receive white cards and answer black card prompts
5. The host selects the best answer – most absurd humor wins 💀

---

## 🧪 Running Tests

To run backend tests:

```bash
cd backend
pytest
```

Test coverage includes:
- REST API (creating/deleting cards)
- Game logic (rounds, votes, player management)
- WebSockets (real-time multiplayer game state)

---

## 🗂️ Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api 
│   │   │    ├── core/   
│   │   │    ├── db/           
│   │   │    ├── game/ 
│   │   │    ├── routes/           
│   │   │    └── schemas/         
│   │   │    
│   │   └── main.py       # FastAPI app
│   ├── tests/            # Pytest test suite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── public/
│   ├── src/
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🙋 Author

Created out of love for absurdity and FastAPI ✨  
Feel free to reach out via GitHub Issues.
