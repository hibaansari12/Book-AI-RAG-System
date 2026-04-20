# 📚 Book AI RAG System

This project is a **Django REST Framework-based backend system** that combines a book database with an **AI-powered Retrieval-Augmented Generation (RAG) pipeline**.

It allows users to:

- Store and manage books  
- Index books into text chunks for AI retrieval  
- Ask natural language questions about books  
- Generate AI-based insights (summary, genre, sentiment)  
- Maintain chat history of Q&A interactions  

---

# 🚀 Key Features

## 📖 Book Management
- Add, view, and manage books  
- Store metadata: title, author, rating, description, reviews  

---

## 🧠 AI-Powered RAG System
- Splits books into intelligent chunks  
- Enables semantic-style question answering  
- Retrieves relevant book context for user queries  

---

## 💬 AI Chat System
Ask questions like:
- “What is Dune about?”  
- “What is the theme of Atomic Habits?”  

- Stores chat history with source tracking  

---

## 🤖 AI Insights Generator
Auto-generates:
- Book summaries  
- Genre classification  
- Sentiment analysis  

---

## ⚡ Batch Processing
- Bulk indexing and AI processing of multiple books  

---

# 🏗️ Tech Stack

- **Backend:** Django, Django REST Framework  
- **Database:** SQLite / PostgreSQL  
- **AI Layer:** OpenAI API / LM Studio (local LLM support)  
- **Caching:** Django cache system  
- **RAG Pipeline:** Custom chunk-based retrieval system  

## Installation 
##**Backend setup**
```css
1. Clone the repository:

git clone https://github.com/yourusername/stock-api.git
cd stock-api
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows
.venv\Scripts\activate
# Linux / Mac
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

#Create MySQL DB
mysql -u root -p
CREATE DATABASE book_insight_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

#Create .env file
(paste inside backend/.env)

DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=book_insight_db
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306
OPENAI_API_KEY=your-openai-key
LM_STUDIO_URL=http://localhost:1234/v1

REDIS_URL=redis://127.0.0.1:6379/1

#Migrate DB
python manage.py makemigrations books ai_engine scraper
python manage.py migrate

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```
##**Frontend setup**
```css
# 1. Install dependencies
cd frontend
npm install
# 2. Create environment file
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=[localhost](http://localhost:8000/api)
EOF
# 3. Start development server
npm run dev
```
**##API Documentation**
## 📚 Book APIs

| Endpoint | Method | Description |
|------------------------------------|--------|----------------------------|
| `/api/books/`                      | GET    | List all books (paginated) |
| `/api/books/{id}/`                 | GET    | Get book details           |
| `/api/books/`                      | POST   | Create/upload new book     |
| `/api/books/{id}/recommendations/` | GET    | Get related books          |
| `/api/books/bulk/`                 | POST   | Bulk upload books          |
| `/api/books/chat-history/`         | GET    | Get Q&A history            |

---
**##AI API**
|Endpoint                   |	Method	| Description |
|---------------------------|--------|-----------------------------|
|/api/ai/ask/	              |POST	|RAG question answering          |
|/api/ai/generate-insights/	|POST	|Generate AI insights for a book |
|/api/ai/index-book/	      |POST	|Index book for RAG              |
|/api/ai/batch-process/	    |POST	|Process multiple books          |
---

##**Scraper API**
|Endpoint                 |	Method	|Description|
|-------------------------|---------|-------------------------|
|/api/scraper/scrape/	    |POST     |	Trigger book scraping    |
|/api/scraper/bulk-scrape/|	POST    |	Multi-query bulk scraping|
---

