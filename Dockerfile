FROM python:3.10
WORKDIR /google-play-uploader
COPY requirements.txt .
RUN pip install -r requirements.txt && rm requirements.txt
COPY upload.py .
ENTRYPOINT [ "python", "./upload.py" ]
CMD [ "--help" ]
