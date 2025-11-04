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
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
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
- Run `python manage.py runserver` for development server
- Run `python manage.py test` for running tests

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

## Contributing

1. Create a new branch
2. Make your changes
3. Submit a pull request

## License

[MIT License](LICENSE)