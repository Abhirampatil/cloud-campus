# Cloud Campus

Cloud Campus is a cloud-based academic resource sharing platform where students can upload, browse, and download study notes securely.

The application allows verified users to share academic resources while storing files securely in AWS S3.

---

## Features

* User registration and login system
* Secure password hashing
* Upload study notes (PDF, DOC, DOCX, PPT, PPTX)
* Browse notes by subject or search by title
* Download notes using secure AWS S3 links
* Personal dashboard to manage uploaded notes
* Download tracking for uploaded resources
* Cloud storage using AWS S3

---

## Tech Stack

Backend

* Python
* Flask
* SQLAlchemy
* Flask-Login

Frontend

* HTML
* Bootstrap 5
* Bootstrap Icons

Cloud & Storage

* AWS S3

Database

* SQLite (development)

---

## Project Structure

```
cloud-campus/
│
├── Frontend/
│   ├── base.html
│   ├── index.html
│   ├── browse.html
│   ├── dashboard.html
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   └── upload.html
│
├── app.py
├── config.py
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Installation

### 1. Clone the repository

```
git clone https://github.com/Abhirampatil/cloud-campus.git
cd cloud-campus
```

### 2. Create a virtual environment

```
python -m venv .venv
```

Activate it:

Windows

```
.venv\Scripts\activate
```

Mac/Linux

```
source .venv/bin/activate
```

---

### 3. Install dependencies

```
pip install -r requirements.txt
```

---

### 4. Configure environment variables

Create a `.env` file in the project root:

```
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///cloudcampus.db
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_BUCKET_NAME=your-bucket-name
AWS_REGION=us-east-1
```

---

### 5. Run the application

```
python app.py
```

The application will run on:

```
http://127.0.0.1:5000
```

---

## AWS S3 Setup

1. Create an S3 bucket in AWS.
2. Create an IAM user with access to S3.
3. Add the access keys to your `.env` file.
4. Ensure the bucket name matches `AWS_BUCKET_NAME`.

---

## Allowed File Types

The platform allows uploading:

* PDF
* DOC
* DOCX
* PPT
* PPTX

Maximum file size: **16MB**

---

## Security Practices

* Passwords are hashed before storing in the database.
* Secrets are stored in environment variables.
* `.env` files are excluded from version control.
* Files are accessed through **temporary AWS presigned URLs**.

---

## Future Improvements

* Email verification system
* Role-based access (Admin / Student)
* File preview inside the platform
* Rating system for notes
* Better search and filtering

---

## License

This project is intended for educational and learning purposes.
