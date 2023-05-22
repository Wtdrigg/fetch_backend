FROM python:alpine
WORKDIR /app
COPY . /app
RUN pip install flask
EXPOSE 5000
ENV PYTHONUNBUFFERED=1
CMD python backend.py --host=0.0.0.0