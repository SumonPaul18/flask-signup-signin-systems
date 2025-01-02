FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 5000
CMD ["sh", "-c", "flask db init && flask db migrate -m 'Initial migration' && flask db upgrade && flask run --host=0.0.0.0"]
