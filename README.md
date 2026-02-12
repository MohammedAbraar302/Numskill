# NumSkillsPro - Python Backend Setup Guide

## Overview
NumSkillsPro has been converted from a Firebase-based application to a secure Python Flask backend with a SQLite database. User credentials are now securely stored locally on your server.

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Windows, macOS, or Linux

## Quick Setup (Windows)

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

Or run the provided setup script:
```bash
setup.bat
```

### 2. Initialize Database & Run Server
```bash
python app.py
```

The server will start on `http://localhost:5000`

### 3. Access the Application
Open your browser and navigate to:
```
file:///c:/Users/abraa/OneDrive/Desktop/Numskill/index.html
```

Or serve it with a local server:
```bash
python -m http.server 8000
# Then visit http://localhost:8000
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Create a new account
- `POST /api/auth/login` - Login with credentials
- `GET /api/auth/verify` - Verify JWT token
- `GET /api/auth/profile` - Get current user profile

### Assessment Management
- `POST /api/assessment/profile` - Save candidate profile
- `GET /api/assessment/profile` - Get candidate profile
- `GET /api/assessment/questions/<module>` - Get module questions
- `POST /api/assessment/score` - Save assessment score
- `GET /api/assessment/scores` - Get all scores
- `POST /api/assessment/checklist` - Save checklist responses
- `GET /api/assessment/checklist` - Get checklist responses
- `POST /api/assessment/game-score` - Save game score
- `GET /api/assessment/game-scores` - Get all game scores
- `GET /api/assessment/report` - Get complete report

## Database Schema

### Users Table
- id (primary key)
- username (unique)
- email (unique)
- password_hash (bcrypt encrypted)
- created_at
- updated_at

### Candidate Profiles Table
- id (primary key)
- user_id (foreign key)
- child_name
- child_age
- parent_name
- created_at
- updated_at

### Assessment Scores Table
- id (primary key)
- user_id (foreign key)
- module_name (magnitude, estimation, facts, sequencing, spatial, memory, consolidated)
- score
- total_questions
- percentage
- answers_json (JSON storage)
- created_at

### Checklist Responses Table
- id (primary key)
- user_id (foreign key)
- responses_json (JSON storage)
- total_score
- created_at

### Game Scores Table
- id (primary key)
- user_id (foreign key)
- game_name (neon_runner, aqua_math, fact_match)
- score
- created_at

## Security Features

1. **Password Hashing**: Uses bcrypt for secure password storage
2. **JWT Tokens**: Stateless session management with JWT
3. **CORS Support**: Cross-origin requests configured
4. **Input Validation**: All inputs validated server-side
5. **Secure Database**: SQLite with proper foreign keys

## Environment Variables

Create a `.env` file in the root directory:

```
FLASK_ENV=development
DEBUG=True
DATABASE_URL=sqlite:///numskill.db
JWT_SECRET_KEY=your-super-secret-key-change-in-production-12345
```

For production, change:
- `FLASK_ENV=production`
- `DEBUG=False`
- Use a strong `JWT_SECRET_KEY`
- Use PostgreSQL for `DATABASE_URL`

## Frontend Configuration

The HTML file (`index.html`) is configured to communicate with the API at `http://localhost:5000/api`. 

To change the API endpoint, modify the script tag in `index.html`:
```javascript
<script>
    window.API_BASE_URL = 'http://your-server-url/api';
</script>
```

## File Structure

```
Numskill/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── models.py              # Database models
├── auth.py                # Authentication routes
├── assessment.py          # Assessment routes
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── numskill.db            # SQLite database (auto-created)
├── index.html             # Frontend application
└── setup.bat              # Windows setup script
```

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, change it in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Database Issues
Delete `numskill.db` to reset the database:
```bash
del numskill.db
python app.py
```

### CORS Errors
Ensure Flask-CORS is installed:
```bash
pip install Flask-CORS
```

### JWT Token Issues
Make sure `JWT_SECRET_KEY` is set in `.env`

## Example Usage

### Register a New User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"teacher1","email":"teacher@school.com","password":"secure123"}'
```

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"teacher1","password":"secure123"}'
```

### Save Candidate Profile
```bash
curl -X POST http://localhost:5000/api/assessment/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "child_name":"John Doe",
    "child_age":8,
    "parent_name":"Jane Doe"
  }'
```

## Support

For issues or questions, refer to the Flask documentation:
- Flask: https://flask.palletsprojects.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- Flask-JWT-Extended: https://flask-jwt-extended.readthedocs.io/

## License
All rights reserved. Educational use only.
