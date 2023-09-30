FROM image: python:3.11-alpine
WORKDIR src/app
COPY . /src/app
RUN python install -r requirements.txt
CMD ["flask","--app","Login","run","--host=0.0.0.0"]