# Scalpel Backend Challenge with FastAPI & Async SQLAlchemy

This project is a backend service for a Data Capture Application. It provides asynchronous API endpoints for managing images and their annotations using FastAPI, SQLAlchemy (with async support), and PostgreSQL.

## Features

- **Asynchronous API Endpoints**: Built with FastAPI and async SQLAlchemy.
- **ORM Models**: Defines models for Images, Annotations, Users, and Locations.
- **CRUD Operations**: Create images and annotations, update annotations, list images with filters, retrieve images/annotations and return an image (with optional scale and quality adjustments).
- **Dependency Management**: Uses virtual environments.

## Project Structure
```
project-root/
├── src/
│   └── app/
│       ├── main.py         # FastAPI application and endpoints
│       ├── models.py       # SQLAlchemy ORM models
│       ├── schemas.py      # Pydantic models for request/response validation
│       └── database.py     # Async database connection and session dependency
├── .gitignore              # Git ignore file
└── README.md               # Project documentation (this file)
```

## Prerequisites

- **Python 3.9+**
- **PostgreSQL**: Ensure PostgreSQL is installed and running.

## Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/amigo2/scalpel
   cd scalpel
   ```
2. **Run Docker**
  Install docker.
  For local dvelopment i created a --reload fastapi app so you can tweak the code and see the changes inmediatly.
  
  ```bash
  docker-compose up --build
  ```

<!-- 2. ## Create and Activate a Virtual Environment
Using Python’s built-in venv:

```bash
python -m venv venv
```
On Linux/macOS:

```bash
source venv/bin/activate
```
On Windows:

```bash
venv\Scripts\activate
```
## Install Dependencies with pip
Install the dependencies by running:

```bash
cd src
pip install -r requirements.txt
```
This command will install all required packages for the project.
## Create the PostgreSQL Database
Create a new database called scalpel_db by running:

Using psql:

```bash
psql -U postgres
postgres=# CREATE DATABASE scalpel_db;
postgres=# \q
```

Update the database connection string in src/app/database.py (or use a .env file with environment variables):
```bash
DATABASE_URL = "postgresql+asyncpg://postgres:your_password@localhost:5432/scalpel_db"
```

Running the Application
```bash
cd src
uvicorn app.main:app --reload
``` -->

The server will start at http://127.0.0.1:8000. You can access the interactive API docs at:

Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc
On startup, the application will automatically create (or update) the necessary database tables.

## API Endpoints Overview

- **Create an Image**
  - **Method:** `POST`
  - **Endpoint:** `/images`
  - **Description:** Create an image record with optional annotations.

- **List Images**
  - **Method:** `GET`
  - **Endpoint:** `/images`
  - **Description:** Retrieve a list of images, with optional filtering by user, location, or instrument.

- **Add an Annotation**
  - **Method:** `POST`
  - **Endpoint:** `/images/{image_key}/annotations`
  - **Description:** Add a new annotation for an existing image.

- **List Image Annotations**
  - **Method:** `GET`
  - **Endpoint:** `/images/{image_key}/annotations`
  - **Description:** Retrieve all annotations associated with an image.

- **Update an Annotation**
  - **Method:** `PUT`
  - **Endpoint:** `/images/{image_key}/annotations/{annotation_index}`
  - **Description:** Update an existing annotation for an image.
  
- **Retrieve an Image File**
  - **Method:** `GET`
  - **Endpoint:** `/images/{image_key}/file`
  - **Description:** Return an image file (with optional scale and quality adjustments).

## Testing
Use Pytest from root.
```bash
pytest tests/test_endpoints.py --disable-warnings -s
```
or 
```bash
pytest tests/test_endpoints.py
```
Only create Image test developed I'm afraid.  

## Interview Review Note

This project is submitted as part of a technical test and is intended for review in the next interview. It is provided "as is" and demonstrates my approach to solving the challenge. I welcome any feedback or discussion during the interview.


