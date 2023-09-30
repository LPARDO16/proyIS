FROM python:3.11-alpine
COPY ../../Downloads .
RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps
CMD ["flask","--app","Login","run","--host=0.0.0.0"]