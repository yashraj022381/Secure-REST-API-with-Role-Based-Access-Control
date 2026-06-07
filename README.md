# 🔐 Secure-REST-API-with-Role-Based-Access-Control
Authentication &amp; authorization system for enterprise APIs. 

A production-ready REST API built with Flask featuring JWT authentication, bcrypt password hashing, and Role-Based Access Control (RBAC).

1. ## 🌐 Live API
**Base URL:** `https://secure-rest-api-with-role-based-access.onrender.com`

  > ⚠️ Free tier — first request may take 30-60 seconds to wake up.

2. ## 🚀 Quick Test
```bash
curl https://secure-rest-api-with-role-based-access.onrender.com/api/health
```

3. ## 🛠️ Tech Stack
  - **Python** — Flask framework
  - **PostgreSQL** — Database
  - **JWT** — Authentication tokens
  - **bcrypt** — Password hashing
  - **RBAC** — Role-Based Access Control
  - **Render** — Cloud deployment

4. ## 📋 API Endpoints

  (i) ### 🔓 Public (No token needed)
   | Method | Endpoint | Description |
   |--------|----------|-------------|
   | GET | `/api/health` | Health check |
   | POST | `/api/auth/register` | Register new user |
   | POST | `/api/auth/login` | Login and get tokens |
   | POST | `/api/auth/refresh` | Refresh access token |

 (ii) ### 🔒 Protected (Token required)
   | Method | Endpoint | Description | Role |
   |--------|----------|-------------|------|
   | GET | `/api/auth/me` | Get my profile | Any |
   | POST | `/api/auth/logout` | Logout | Any |
   | PUT | `/api/users/profile` | Update profile | Any |
   | POST | `/api/users/change-password` | Change password | Any |
   | GET | `/api/products/` | List products | viewer+ |
   | POST | `/api/products/` | Create product | editor+ |
   | DELETE | `/api/products/<id>` | Delete product | admin |
   | GET | `/api/admin/users` | List all users | admin |
   | GET | `/api/admin/roles` | List all roles | admin |
   | POST | `/api/admin/users/<id>/roles` | Assign role | admin |

5. ## 🧪 Test with Postman

  [![Run in Postman](https://run.pstmn.io/button.svg)](YOUR_POSTMAN_LINK)

   ### Quick Login Test
   ```bash
   curl -X POST \
     https://secure-rest-api-with-role-based-access.onrender.com/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"email":"admin@example.com","password":"Admin1234!"}'
   ```

6. ## 🔑 Roles & Permissions

   | Role | Permissions |
   |------|-------------|
   | viewer | read:products |
   | editor | read:products, write:products, read:users |
   | admin | All permissions |

7. ## ⚙️ Run Locally

  ```bash
  # Clone the repo
  git clone https://github.com/YOURUSERNAME/secure-api.git
  cd secure-api

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Set environment variables
copy .env.example .env
# Edit .env with your database URL and secret key

# Run
python run.py
```

8. ## 🏗️ Project Structure

   secure_api/
   ├── app/
   │   ├── models/
   │   │   ├── user.py       # User model with bcrypt
   │   │   ├── role.py       # Role & Permission models
   │   │   └── token.py      # JWT blacklist model
   │   ├── routes/
   │   │   ├── auth.py       # Login, register, logout
   │   │   ├── users.py      # Profile management
   │   │   ├── admin.py      # Admin controls
   │   │   └── products.py   # Protected resource
   │   ├── middleware/
   │   │   └── auth_middleware.py  # JWT & RBAC decorators
   │   └── utils/
   │       └── jwt_handler.py      # Token generation
   │   ├── init.py
   │   ├── config.py
   ├── tests/
        ├── test_auth.py
   ├── config.py             # App configuration
   ├── .env.example          
   ├── seed.py
   ├── seed_data.py
   ├── run.py                # Entry point
   └── requirements.txt

