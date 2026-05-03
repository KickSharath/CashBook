# CashBook Application

A full-stack application for managing personal finances with an Angular frontend and Python backend.

## Project Structure

```
CashBook/
├── CashBook_Frontend/    # Angular application
└── CashBook_Backend/     # Python backend
```

## Frontend (Angular)

Located in `CashBook_Frontend/`

### Prerequisites
- Node.js (v16 or higher)
- npm (v8 or higher)
- Angular CLI

### Setup
```bash
cd CashBook_Frontend
npm install
ng serve
```

The application will be available at `http://localhost:4200`

## Backend (Python)

Located in `CashBook_Backend/`

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment

### Setup
```bash
cd CashBook_Backend
`python -m venv venv
`source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## Development

### Frontend Development
- Run `ng serve` for development server
- Run `ng build` to build the project
- Run `ng test` to execute unit tests
- Run `ng e2e` to execute end-to-end tests

### Backend Development
- Activate virtual environment  
- Run `uvicorn main:app --reload` for development server  
- Access API at `http://127.0.0.1:8000`  
- Use `/docs` for interactive API testing (if enabled)  

## Environment Variables

### Frontend
Create `.env` file in `CashBook_Frontend/`:
```
API_URL=http://localhost:8000
```

### Backend
Create `.env` file in `CashBook_Backend/`:
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
```

## License

[MIT License](LICENSE)
