from python:3.10
WORKDIR /usr/src/app
COPY requirements.txt /usr/src/app
COPY template.docx /usr/src/app
COPY ./src/app.py /usr/src/app
RUN pip3 install --no-cache-dir -U pip && \
    pip3 install --no-cache-dir -r requirements.txt
CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]
