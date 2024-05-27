FROM python:3.12

WORKDIR /usr/src/app/
RUN apt-get update && apt-get -y install gcc

COPY . /usr/src/app/
RUN mkdir -p submissions/ && make

ARG USERNAME=userjude
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

ENV APP_HOME=/usr/src/app/

RUN chown -R $USERNAME:$USERNAME $APP_HOME && \
    chmod -R u+rwX $APP_HOME

RUN pip install --upgrade pip && pip install flask==3.0.2 gunicorn==22.0.0
USER $USERNAME
EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]