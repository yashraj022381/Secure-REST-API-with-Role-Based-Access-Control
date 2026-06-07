# 🔐 Secure-REST-API-with-Role-Based-Access-Control
Authentication &amp; authorization system for enterprise APIs. 

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=json-web-tokens&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)

A production-ready REST API built with Flask featuring JWT authentication, bcrypt password hashing, and Role-Based Access Control (RBAC).

1. ## 📸 Screenshots

2. ## 🌐 Live API
   
**Base URL:** `https://secure-rest-api-with-role-based-access.onrender.com`

  > ⚠️ Free tier — first request may take 30-60 seconds to wake up.

3. ## 🚀 Quick Test
   
   ```bash
  curl https://secure-rest-api-with-role-based-access.onrender.com/api/health
    ```
    
4. ## 📬 Test with Postman

   [![Run in Postman](https://y-g-jagdale98-4591827.postman.co/workspace/Yashraj's-Workspace~bde62ced-531c-4a70-8112-19a6b136917d/example/55454576-3deac117-8546-48e1-b45e-a2e7b39f6bf6?action=share&source=copy-link&creator=55454576)

    Download the Postman Collection:
    Secure API - Postman Collection

   ### Quick Login Test
   ```bash
   curl -X POST \
     https://secure-rest-api-with-role-based-access.onrender.com/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"email":"admin@example.com","password":"Admin1234!"}'
   ```
5. 🔐 Features:
    
   ✅ JWT Authentication (access + refresh tokens)
   ✅ bcrypt password hashing
   ✅ Role-Based Access Control (viewer/editor/admin)
   ✅ Token blacklisting on logout
   ✅ Account lockout after failed attempts
   ✅ PostgreSQL database
   ✅ Deployed on Render
   
6. ## 🛠️ Tech Stack
   
  - **Python** — Flask framework
  - **PostgreSQL** — Database
  - **JWT** — Authentication tokens
  - **bcrypt** — Password hashing
  - **ORM** - SQLAlchemy
  - **RBAC** — Role-Based Access Control
  - **Render** — Cloud deployment


7. ## 📋 API Endpoints

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


8. ## 🔑 Roles & Permissions

   | Role | Permissions |
   |------|-------------|
   | viewer | read:products |
   | editor | read:products, write:products, read:users |
   | admin | All permissions |


9. ## ⚙️ Run Locally

  ```bash
  # Clone the repo
  git clone https://github.com/YOURUSERNAME/secure-api.git
  cd secure-api

  i) # Create virtual environment
     python -m venv venv
     venv\Scripts\activate  # Windows
     source venv/bin/activate  # Mac/Linux

  ii) # Install dependencies
      pip install -r requirements.txt

 iii) # Set environment variables
      copy .env.example .env
      # Edit .env with your database URL and secret key

  vi) # Run
      python run.py
  ```

10. ## 🏗️ Project Structure

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

11. 📄 License
    This project is open-source and available under the MIT License.

    Made with ❤️ for learning secure API development
