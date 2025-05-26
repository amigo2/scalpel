# Dockerfile
FROM public.ecr.aws/lambda/python:3.9

# 1) Install dependencies + Mangum
COPY src/requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt \
 && pip install mangum

# 2) Copy your app package directly into /var/task/app
#    So /var/task/app/main.py, database.py, models.py, etc.
COPY src/app /var/task/app

# 3) (Optional) Copy static into a place that matches your code
#    If your code does app.mount("/static", StaticFiles(...))
#    then static should live at /var/task/app/static
COPY src/app/static       /var/task/app/static

# 4) Tell Lambda to look for the handler symbol in the module app.main
CMD ["app.main.handler"]
