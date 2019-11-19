# Build FE
FROM node:10.16.3 as nodeos

COPY . /usr/src/app

WORKDIR /usr/src/app/frontend

RUN npm install \
    && npm run build

# Build lyrebird
FROM python:3.7.5 as pyos

COPY . /usr/src/app

WORKDIR /usr/src/app

COPY --from=nodeos /usr/src/app/lyrebird/client/ /usr/src/app/lyrebird/client/

RUN pip install --upgrade pip==19.3.1 \
    && pip install . -i https://pypi.douban.com/simple \
    && rm -rf /usr/src/app

# Make lyrebird image
FROM python:3.7.5-slim

COPY --from=pyos /usr/local/lib/python3.7/site-packages /usr/local/lib/python3.7/site-packages
COPY --from=pyos /usr/local/bin /usr/local/bin

RUN apt-get update && apt-get install -y --no-install-recommends git=1:2.20.1-2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 9090
EXPOSE 4272

ENV LC_ALL=C.UTF-8
ENV LANG C.UTF-8

CMD [ "lyrebird" ]
