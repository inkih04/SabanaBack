# 🌾 Sabana - Issue Management System

Backend repository for the **Sabana** project - A web application inspired by Taiga's issue management system.

## 📋 Project Overview

**Sabana** is a comprehensive issue management system developed for the **ASW (Aplicaciones y Servicios Web)** course. The application provides two main interfaces:

### 🔧 Dual Architecture
- ** REST API**: Complete API for frontend integration and external applications
- **🌐 Classic Web Interface**: Traditional web application with Google OAuth authentication

### ✨ Key Features
- **Issue Management**: Create, organize, and filter issues efficiently
- **Advanced Filtering**: Sort and categorize issues by various criteria
- **File Attachments**: Support for file uploads and attachments (previously powered by AWS S3)
- **Google Authentication**: Secure login system using Google OAuth
- **Responsive Design**: User-friendly interface inspired by Taiga's issue tracker

## 👥 Team Members
- [David Mas](https://github.com/PatoPro121) - Full Stack Developer
- [Pol Sancho](https://github.com/PolSB968) - Backend Developer
- [David Sanz](https://github.com/DavidSanzMartinez) - Frontend Developer
- [Víctor Díez](https://github.com/inkih04) - Project Lead & Full Stack Developer

## 🛠️ Technologies Used

### Backend
- **Python 3.x** - Primary programming language
- **Django** - Web framework and REST API
- **Django REST Framework** - API development
- **Swagger/OpenAPI** - API documentation
- **SQLite** - Database (development/production)
- **Docker** - Containerization

### Authentication & Storage
- **Google OAuth 2.0** - User authentication
- **AWS S3** - File storage (discontinued due to free tier expiration)

### Deployment
- **Render** - Cloud hosting platform
- **Docker** - Container deployment

## 🚀 Live Demo

🔗 **[Live Application on Render](https://it22d-backend.onrender.com/)**

> ⚠️ **Note**: The application is hosted on Render's free tier. The initial page load may take 30-60 seconds as the server spins up from sleep mode.

## 📌 Project Management

We use **Taiga** for tracking tasks and project progress:  
🔗 [Taiga Board](https://tree.taiga.io/project/victordiez-it22dasw/taskboard/sprint-1-22919)

## 🏗️ Architecture

### API Endpoints
The application provides a comprehensive REST API that can be consumed by any frontend application or external service.

#### 📚 API Documentation
The REST API is fully documented using **Swagger/OpenAPI**, providing:
- Interactive API explorer
- Detailed endpoint descriptions
- Request/response examples
- Authentication requirements

🔗 **[API Documentation (Swagger UI)](https://it22d-backend.onrender.com/swagger/)**

### Web Interface
A traditional Django-rendered web application with server-side rendering, featuring:
- Google OAuth integration
- Session-based authentication
- Responsive Bootstrap-based UI

## ⚠️ Important Notes

- **AWS Integration**: File attachment functionality is currently disabled due to the expiration of our AWS Student account. The feature remains in the codebase for future reactivation.
- **Render Hosting**: Due to free tier limitations, the application may experience cold starts. Please allow extra time for the initial load.

## 🎓 Academic Context

This project was developed as part of the **ASW (Aplicaciones y Servicios Web)** course, demonstrating:
- Full-stack web development
- RESTful API design
- Authentication systems
- Cloud deployment
- Team collaboration
- Agile project management

##🏆 Academic Achievement

Final Grade: 9.5/10 - Excellent project execution and implementation quality.

## 📊 Features Showcase

- ✅ Create and manage issues
- ✅ Filter and sort functionality  
- ✅ User authentication with Google
- ✅ RESTful API with Swagger documentation
- ✅ File attachment system architecture
- ✅ Interactive API explorer
- ✅ Responsive web interface
- ✅ Docker containerization
- ✅ Cloud deployment

## 🔧 Local Development

```bash
# Clone the repository
git clone https://github.com/inkih04/SabanaBack.git

# Navigate to project directory
cd SabanaBack

# Build and run with Docker
docker-compose up --build
```

## 📸 Screenshots

### 🌐 Web Interface
![Main Dashboard](https://github.com/inkih04/SabanaBack/blob/main/images/Issues.png)
![Filters](https://github.com/inkih04/SabanaBack/blob/main/images/filters.png)
![Create Issue](https://github.com/inkih04/SabanaBack/blob/main/images/create.png)
![Issue Details](https://github.com/inkih04/SabanaBack/blob/main/images/issue.png) 



### 📚 API Documentation

 ![Swagger UI Overview](https://github.com/inkih04/SabanaBack/blob/main/images/API.png) 
![API Endpoints](https://github.com/inkih04/SabanaBack/blob/main/images/API2.png) 




## 📝 License

This project was developed for educational purposes as part of university coursework.

---

**Developed with ❤️ by the Sabana Team**
