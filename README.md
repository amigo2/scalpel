# Scalpel Backend FastAPI & Async SQLAlchemy + AWS Terraform micorservices.

This project is a backend and a frontend service for a Data Capture Application, designed to handle image processing and annotation management. It is built using FastAPI, async SQLAlchemy, and PostgreSQL, with full Docker support for both the backend and frontend.

## Features

- 🚀 **Asynchronous API Endpoints:** Built with FastAPI and async SQLAlchemy for high performance.
- 🐳 **Fully Containerized with Docker:** Both the backend (FastAPI) and frontend (React TypeScript) run in Docker containers for easy deployment.
- ⚛️ **React TypeScript Frontend:** The frontend is built using React with TypeScript for a scalable and maintainable UI.
- 🗂️ **ORM Models:** Defines Images, Annotations, Users, and Locations as database models.
- 🔄 **Full CRUD Support:**  
  - Create images and annotations.  
  - Update annotations.  
  - List images with filters.  
  - Retrieve images and annotations.  
  - Process images with optional scaling and quality adjustments (JPEG only).  

- 🔧 **Dependency Management:** Uses Docker for environment consistency and easy setup.

## Project Structure
```
project-root/
|--
├── Dockerfile
├── README.md
├── docker-compose.yml
├── frontend
│   ├── README.md
│   ├── src
│   │   ├── App.tsx
│   │   ├── Appnew.tsx
│   │   ├── components
│   │   ├── index.css
│   │   ├── main.tsx
│   │   ├── types.ts
├── src
│   ├── app
│   │   ├── database.py
│   │   ├── images
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   ├── requirements.txt
├── tests
│   ├── conftest.py
│   └── test_endpoints.py
└── wait-for-it.sh
             # Project documentation (this file)
```

## Prerequisites

- **Python 3.9+**
- **PostgreSQL**
- **Docker**
- **Node**

## Setup

**Clone the Repository**

   ```bash
   git clone https://github.com/amigo2/scalpel
   cd scalpel
   ```
## Build and run Docker
  Install Docker.  
  For local development I've created a --reload Fastapi app so you can tweak the code and see the changes inmediatly.  

  Build docker app and database, and will run the tests
  ```bash
  docker-compose up --build
  docker-compose down -v

  docker-compose up -d
  docker-compose restart web



  ```
  After building, you can run tests separately.  
  Test backend endpoints async to db
  ```bash
  docker-compose run test  
  ```

The server will start at http://127.0.0.1:8000. You can access the interactive API docs at:

Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc
On startup, the application will automatically create (or update) the necessary database tables.

## Frontend
To build frontend
```bash
  cd frontend
  npm install
  npm run dev
  
  ```
Server will start at http://localhost:5173/

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

- **List Image Annotations (Not implemented)** 
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

## Frontend ##

**Some screen shots**  

<img src="img/ss1.png" alt="Project Preview" width="600"/>  

**New Image**  
<img src="img/ss2.png" alt="New Image" width="300"/>  

**Update size**  
<img src="img/ss3.png" alt="Update size" width="300"/>  

**New annotation**  
<img src="img/ss4.png" alt="New annotation" width="200"/>

**Update annotation**  
<img src="img/ss5.png" alt="New annotation" width="200"/>

## Features ## 
- Users can filter images by annotation, user, client, or location.
- Users can upload and create images with metadata.
- Users can edit image size and quality (JPEG format only).
- Users can add new annotations to images.
- Users can modify existing annotations.
- Users can delete an image by its key.
- Hovering over the image key name displays the full path.  

Note:
Images are stored following a structure similar to Amazon S3, where the file path and file key (filename) are stored separately.





 export AWS_PROFILE=bistro_agent                                                      
export AWS_REGION=eu-west-2         

aws ecr get-login-password \                                                         
  | docker login --username AWS --password-stdin 929423420164.dkr.ecr.eu-west-2.amazonaws.com


export DOCKER_BUILDKIT=0  

docker build --platform linux/amd64 -t scalpel:latest .           



fernandocabello@Fernandos-MacBook-Pro scalpel % docker tag scalpel:latest \                              
  929423420164.dkr.ecr.eu-west-2.amazonaws.com/scalpel:latest

docker push 929423420164.dkr.ecr.eu-west-2.amazonaws.com/scalpel:latest

docker manifest inspect 929423420164.dkr.ecr.eu-west-2.amazonaws.com/scalpel:latest \
  | grep mediaType                                           




# ensure we’re using your bistro_agent profile
export AWS_PROFILE=bistro_agent AWS_REGION=eu-west-2

# disable BuildKit so we get a classic Docker manifest
export DOCKER_BUILDKIT=0

# build and tag
docker build --platform linux/amd64 -t scalpel:latest .

# login + push
aws ecr get-login-password \
  | docker login --username AWS --password-stdin 929423420164.dkr.ecr.eu-west-2.amazonaws.com

docker tag scalpel:latest 929423420164.dkr.ecr.eu-west-2.amazonaws.com/scalpel:latest
docker push 929423420164.dkr.ecr.eu-west-2.amazonaws.com/scalpel:latest


## run local
docker run --platform linux/amd64 -it --rm \
  -p 8000:8000 \
  -v "$(pwd)/src/app":/var/task/app \
  --entrypoint uvicorn \
  scalpel:latest \
  app.main:app \
  --reload



## test local lambda
 docker run --platform linux/amd64 -p 9000:8080 --rm scalpel:latest
 
 curl -v -XPOST http://localhost:9000/2015-03-31/functions/function/invocations \
     -H "Content-Type: application/json" \
     -d @event.json

* checkout new fuile event.json, can be done with SAM



### Build or rebuild your SPA on the host:

bash
Copy
Edit
cd frontend
npm run build
cd ..
Restart your compose stack, removing any orphans:

bash
Copy
Edit
docker-compose down
docker-compose up -d --build --remove-orphans
Verify inside the running container that the files are present:

bash
Copy
Edit
docker-compose exec web ls /app/frontend/dist
# you should see index.html, assets/, etc.
Browse to http://localhost:8000/ — your SPA’s index.html should now load.



## deploy front end
aws s3 sync frontend/dist s3://scalpel-frontend-bucket/ \
  --profile bistro_agent \
  --region eu-west-2
