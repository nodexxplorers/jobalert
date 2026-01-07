# JobAlert 🚀

JobAlert is a powerful, automated job aggregation platform designed to help freelancers and professionals find opportunities instantly. It scrapes job listings from Twitter/X in real-time, filters them based on user preferences, and delivers instant notifications via Email and Telegram.

![JobAlert Dashboard](frontend/public/logos.png)

## 🌟 Key Features

-   **Real-time Job Scraping**: Automatically scans Twitter/X for job postings across 30+ categories (Video Editing, Web Dev, Marketing, etc.).
-   **Smart Filtering**: Uses keywords to match jobs specifically to your skills and interests.
-   **Instant Notifications**: Get alerted via Email, or Telegram the moment a relevant job is found.
-   **User Dashboard**: A clean, modern interface to view, save, and manage job listings.
-   **Biometric Login**: Secure and quick access using FaceID/TouchID (WebAuthn).
-   **Admin Controls**: Comprehensive admin dashboard for managing users, monitoring scraper health, and viewing system analytics.
-   **Mobile Friendly**: Fully responsive design for on-the-go access.

## 🏗️ Architecture

The project is built as a monorepo with a distinct separation of concerns:

-   **Frontend**: React (Vite) + TypeScript + Tailwind CSS
-   **Backend**: FastAPI (Python) + SQLAlchemy + PostgreSQL
-   **Scheduler**: APScheduler for automated background scraping tasks

## � Project Structure

A high-level overview of the codebase organization:

```
jobalert/
├── backend/                # Python/FastAPI Backend
│   ├── app/
│   │   ├── api/            # API Route definitions
│   │   ├── core/           # Config, DB connection, Security
│   │   ├── models/         # SQLAlchemy Database Models
│   │   ├── schemas/        # Pydantic Schemas (Data Validation)
│   │   ├── services/       # Business Logic (Scraper, Notifications)
│   │   └── main.py         # App Entry Point
│   ├── alembic/            # Database Migrations
│   └── requirements.txt    # Python Dependencies
│
├── frontend/               # React/Vite Frontend
│   ├── src/
│   │   ├── components/     # Reusable UI Components
│   │   ├── pages/          # Main Application Views (Routes)
│   │   ├── services/       # API Client & Auth Services
│   │   ├── hooks/          # Custom React Hooks
│   │   └── types/          # TypeScript Definitions
│   └── package.json        # Frontend Dependencies
│
└── README.md               # Project Documentation
```

## 🛠️ Technologies Used

-   **Backend Framework**: FastAPI (High performance async web framework)
-   **Database**: PostgreSQL
-   **ORM**: SQLAlchemy (Async)
-   **Browser Automation**: Playwright / Selenium (for scraping)
-   **Frontend Library**: React 18
-   **Styling**: Tailwind CSS, Lucide React (Icons)
-   **State Management**: React Hooks & Context API
-   **Authentication**: OAuth2 (Google/Twitter) + JWT
-   **Scheduling**: APScheduler

## �🚀 Getting Started

### Prerequisites

-   **Node.js** (v18+)
-   **Python** (v3.10+)
-   **PostgreSQL** (running locally or a cloud instance)
-   **Google/Twitter Developer Accounts** (for OAuth and scraping)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/jobalert.git
cd jobalert
```

### 2. Backend Setup

 Navigate to the backend directory:
 ```bash
 cd backend
 ```

 Create a virtual environment:
 ```bash
 python -m venv venv
 source venv/bin/activate  # On Windows: venv\Scripts\activate
 ```

 Install dependencies:
 ```bash
 pip install -r requirements.txt
 ```

 Configure Environment Variables:
 Create a `.env` file in the `backend/` directory. You can use `.env.example` as a reference.
 **Required variables:**
 - `DATABASE_URL`: Connection string for your PostgreSQL database.
 - `SECRET_KEY`: Random string for security.
 - `TWITTER_USERNAME` / `TWITTER_PASSWORD`: For the scraper service.
 - `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`: For Google OAuth.

 Run Database Migrations:
 ```bash
 alembic upgrade head
 ```

 Start the Server:
 ```bash
 uvicorn app.main:app --reload
 ```
 The API will be available at `http://localhost:8000`.

### 3. Frontend Setup

 Navigate to the frontend directory:
 ```bash
 cd frontend
 ```

 Install dependencies:
 ```bash
 npm install
 ```

 Configure Environment Variables:
 Create a `.env` file in the `frontend/` directory.
 - `VITE_API_URL`: URL of your backend (e.g., `http://localhost:8000`).

 Start the Development Server:
 ```bash
 npm run dev
 ```
 The application will open at `http://localhost:5173`.

## 📖 Usage Guide

1.  **Sign Up**: Create an account via the registration page. You can use Email or quick connect with Twitter/Google.
2.  **Onboarding**: Select your preferred job categories (e.g., "Software Developer", "Graphic Designer").
3.  **Dashboard**:
    -   **Latest Jobs**: View the stream of new jobs matching your criteria.
    -   **Saved Jobs**: Bookmark interesting roles to apply later.
    -   **Filters**: Use the sidebar to refine by keywords, job type, or payment status.
4.  **Settings**:
    -   **Alerts**: Configure your Email and Telegram notification preferences.
    -   **Keywords**: Add specific positive/negative keywords to fine-tune your feed.
5.  **Admin** (for authorized users):
    -   Monitor system status.
    -   Trigger manual scrapes.
    -   View user growth analytics.

## 🔒 Security

-   **Authentication**: JWT-based auth flow with secure HTTP-only cookies.
-   **Passwords**: Hashed using bcrypt.
-   **Biometrics**: WebAuthn implemented for secure, password-less login.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1.  Fork the project
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## ❓ Troubleshooting

**Q: The scraper isn't finding any jobs.**
A: Ensure your `TWITTER_USERNAME` and `TWITTER_PASSWORD` in `backend/.env` are correct. Twitter aggressively blocks unauthenticated scraping. Check `backend/app.log` or the console output for specific errors.

**Q: I can't connect my Google Account.**
A: Verify that the `GOOGLE_REDIRECT_URI` in your Google Cloud Console matches exactly with what is in your `.env` file (usually `http://localhost:8000/api/auth/google/callback`).

**Q: Database connection failed.**
A: Make sure your PostgreSQL server is running and the `DATABASE_URL` is correct. You might need to install `psycopg2` or `asyncpg`.

