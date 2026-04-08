# AI Background Removal Backend

A scalable **Django + Celery based backend** for removing image backgrounds asynchronously using AI.
Built with production-ready architecture including task queues, cloud storage, and CI/CD.

---

## 🧠 Features

*  Upload images via REST API
*  Asynchronous background removal using Celery
*  AI-powered image processing
*  Cloud storage using AWS S3
*  Status polling for long-running tasks
*  API documentation with Swagger
*  CI/CD with GitHub Actions
*  Secure and scalable backend architecture

---

## 🏗️ Tech Stack

* **Backend:** Python, Django, Django REST Framework
* **Async Tasks:** Celery
* **Message Broker:** Redis
* **Storage:** AWS S3
* **Server:** Gunicorn + Nginx
* **Deployment:** AWS EC2
* **CI/CD:** GitHub Actions

---

## 📂 Project Structure

```
image_bg_removal_backend/
│── bg_removal/        # Main app (models, views, tasks)
│── project/           # Django settings & config
│── manage.py
│── requirements.txt
│── .env
```

---

## ⚙️ Setup Instructions

### 1. Clone Repository

```bash
git clone https://github.com/your-username/image_bg_removal_backend.git
cd image_bg_removal_backend
```

---

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your_secret_key
DEBUG=True

DB_NAME=your_db
DB_USER=your_user
DB_PASSWORD=your_password

AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_STORAGE_BUCKET_NAME=your_bucket
AWS_S3_REGION_NAME=your_region

CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/1
```

---

### 5. Run Migrations

```bash
python manage.py migrate
```

---

### 6. Start Services

#### Start Django

```bash
python manage.py runserver
```

#### Start Redis

```bash
redis-server
```

#### Start Celery Worker

```bash
celery -A project worker --loglevel=info
```

---

## 📡 API Endpoints

### Upload Image

```http
POST /api/remove-bg/
```

**Response:**

```json
{
  "id": 1,
  "status": "pending"
}
```

---

### Check Status

```http
GET /api/status/{id}/
```

**Response:**

```json
{
  "id": 1,
  "status": "completed",
  "output_image": "https://s3-url/output.png"
}
```

---

## 🔄 Workflow

```
Client → Django API → Celery Queue → AI Processing → S3 Storage → Response
```

---

## 🚀 Deployment

* Hosted on AWS EC2
* Reverse proxy using Nginx
* Gunicorn as WSGI server
* Static/media handled via S3

---

## 🔁 CI/CD

GitHub Actions automates:

* Pull latest code
* Install dependencies
* Run migrations
* Restart services

---

## 🧠 Key Learnings

* Handling async processing with Celery
* Optimizing ML workloads for low-resource servers
* Reverse proxy setup with Nginx
* Production deployment on AWS
* CI/CD automation

---

## 📌 Future Improvements

* Add GPU-based processing
* Improve model accuracy
* Add authentication system
* Rate limiting & API security

---

## 👨‍💻 Author

**Anuraag K S**

---

## ⭐ If you like this project

Give it a ⭐ on GitHub!
