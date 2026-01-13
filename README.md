# OneHR 2.0 API - Backend Service

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![PostgreSQL](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)

Professional backend API service for **OneHR 2.0 Client & Document Management**. Built with FastAPI and optimized for serverless deployment on AWS Lambda.

## 🚀 Key Features

- **Client & CRM**: Full lifecycle management for clients, including detailed profiles and onboarding status.
- **Contact Management**: Associate multiple contacts with roles (Primary, Timesheet Approver, etc.) to each client.
- **Document System**: Secure document uploads and storage using AWS S3 with metadata tracking in PostgreSQL.
- **Contracts & POs**: Management of client contracts, addendums, and Purchase Orders with real-time budget tracking.
- **Compliance Tracking**: Per-client and per-employee requirement management.
- **Hybrid Database Support**: Dynamically adapts to different database schema variations (e.g., `onehr` vs `postgres` schemas).

## 🛠 Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Runtime**: Python 3.9+ 
- **Database**: PostgreSQL (AWS RDS)
- **Deployment**: AWS Lambda via [Mangum](https://mangum.io/)
- **Storage**: AWS S3
- **Security**: JWT & AWS Secrets Manager

## 📂 Project Structure

- `app.py`: Main FastAPI application entry point.
- `requirements.txt`: Project dependencies.
- `localhost_server.py`: Local development server for testing.
- `.gitignore`: Configured for Python and AWS deployments.

## ⚙️ Setup & Installation

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/pavanbon/Onehr-Client.git
   cd Onehr-Client
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run locally:**
   ```bash
   python localhost_server.py
   ```
   The API will be available at `http://localhost:5000`. Access Swagger UI at `http://localhost:5000/docs`.

### Deployment to AWS Lambda

This project is configured to run on AWS Lambda. Use the provided tools (if any) or package the application with `mangum` to deploy.

## 🛡 Security

The API uses `HTTPBearer` authentication. Ensure all requests include a valid JWT token in the `Authorization` header.

```bash
Authorization: Bearer <your_token>
```

---
*Maintained by the OneHR Development Team.*
