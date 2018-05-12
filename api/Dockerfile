FROM python:3.6.5

WORKDIR /srv/src

# Do this first to cache requirements
ADD requirements.txt /srv/src
RUN pip install -r requirements.txt

ADD . /srv/src

ENV PYTHONPATH=/srv/src

EXPOSE 8000
