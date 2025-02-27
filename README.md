# Backend Challenge with FastAPI & Async SQLAlchemy

This project is a backend service for a Data Capture Application. It provides asynchronous API endpoints for managing images and their annotations using FastAPI, SQLAlchemy (with async support), and PostgreSQL.

## Features

- **Asynchronous API Endpoints**: Built with FastAPI and async SQLAlchemy.
- **ORM Models**: Defines models for Images, Annotations, Users, and Locations.
- **CRUD Operations**: Create images and annotations, update annotations, list images with filters, and retrieve images/annotations.
- **Dependency Management**: Uses Poetry for managing dependencies and virtual environments.
- **Development Convenience**: Automatically creates database tables at startup (ideal for development).

## Project Structure

project-root/ 
├── challenge/ # Challenge instructions (ignored by Git) 
├── src/ 
│ └── app/ 
│ ├── main.py # FastAPI application and endpoints 
│ ├── models.py # SQLAlchemy ORM models 
│ ├── schemas.py # Pydantic models for request/response validation 
│ └── database.py # Async database connection and session dependency 
├── .gitignore # Git ignore file 
├── pyproject.toml # Poetry configuration file 
└── README.md # Project documentation (this file)


## Prerequisites

- **Python 3.9+**
- **PostgreSQL**: Ensure PostgreSQL is installed and running.
- **Poetry**: For dependency management.

## Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/yourrepository.git
   cd yourrepository


## Install Dependencies

With Poetry installed, run:

bash
Copy
poetry install
Configure the Database

Create a PostgreSQL database (if not already created):

bash
Copy
createdb scalpel_db
Update the database connection string in src/app/database.py (or use a .env file with environment variables):

python
Copy
DATABASE_URL = "postgresql+asyncpg://postgres:your_password@localhost:5432/scalpel_db"
Running the Application
You have two common options:

Option 1: Using Poetry’s Virtual Environment
Poetry automatically creates and manages a virtual environment for your project. You can activate it by running:

bash
Copy
poetry shell
Once activated, start the FastAPI application with:

bash
Copy
uvicorn src.app.main:app --reload
Option 2: Using Poetry Run (Without Activating the Virtual Environment Manually)
Alternatively, you can run the application without entering the virtual environment shell by prefixing your command with poetry run:

bash
Copy
poetry run uvicorn src.app.main:app --reload
In either case, the server will start at http://127.0.0.1:8000. You can access the interactive API docs at:

Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc
On startup, the application will automatically create (or update) the necessary database tables.

API Endpoints Overview
Create an Image

Method: POST
Endpoint: /images
Description: Create an image record with optional annotations.
Add an Annotation

Method: POST
Endpoint: /images/{image_key}/annotations
Description: Add a new annotation for an existing image.
Update an Annotation

Method: PUT
Endpoint: /images/{image_key}/annotations/{annotation_index}
Description: Update an existing annotation for an image.
List Images

Method: GET
Endpoint: /images
Description: Retrieve a list of images, with optional filtering by user, location, or instrument.
Retrieve an Image File

Method: GET
Endpoint: /images/{image_key}/file
Description: Return an image file (with optional scale and quality adjustments). (Image processing logic to be implemented as needed.)
List Image Annotations

Method: GET
Endpoint: /images/{image_key}/annotations
Description: Retrieve all annotations associated with an image.
Contributing
Contributions are welcome! Feel free to open an issue or submit a pull request if you have suggestions or improvements.

License
This project is licensed under the MIT License.