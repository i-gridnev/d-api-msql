FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN mkdir /app
WORKDIR /app
COPY ../backend/requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt
ADD ../backend/ /app/
RUN python3 manage.py collectstatic --no-input -v 2