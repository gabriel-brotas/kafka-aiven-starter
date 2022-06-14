FROM python:3.10.2-slim

RUN apt update && apt install -y --no-install-recommends \
    default-jre \
    git \
    libsnappy-dev \
    curl

RUN apt-get install build-essential librdkafka-dev -y

RUN useradd -ms /bin/bash python

RUN pip install pdm pdm-venv

USER python

WORKDIR /home/python/app

# specify the python version we want to work with
ENV MY_PYTHON_PACKAGES=/home/python/app/__pypackages__/3.10
ENV PYTHONPATH=${PYTHONPATH}/home/python/app/src
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH $PATH:${MY_PYTHON_PACKAGES}/bin

RUN echo 'eval "$(pdm --pep582)"' >> ~/.bashrc

EXPOSE 3000

CMD [ "tail", "-f", "/dev/null"]