FROM python:3.11-slim


# Set the working directory in the container
# RUN mkdir -p /test/backend
WORKDIR /backend

ENV TZ Asia/Tokyo

RUN apt update && \
    apt -y upgrade

COPY requirements.txt ./
# Copy the current directory contents into the container at /app

RUN pip install --upgrade pip && \
    pip install -r requirements.txt \
    pip install requests


COPY . .

EXPOSE 5000

CMD [ "python3", "-m" , "flask", "run", "--host", "0.0.0.0", "--port", "5000"]
