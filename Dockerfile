FROM python:3.9.6

RUN apt-get update && apt-get -y install gcc

COPY . /usr/src/app/
WORKDIR /usr/src/app/
RUN mkdir -p submissions/ && make

ARG USERNAME=userjude
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME
USER $USERNAME

# WORKDIR /usr/src/app/
# https://stackoverflow.com/questions/30323224/deploying-a-minimal-flask-app-in-docker-server-connection-issues
RUN pip3 install --upgrade pip && pip3 install Flask==2.0.3

CMD ["python", "main.py"]
