FROM node:14.15-alpine as nodebuilder

COPY . /usr/src

WORKDIR /usr/src/frontend

RUN npm --registry https://registry.npm.taobao.org install \
  && npm run build

FROM python:3.8-alpine as pybuilder

ENV PYTHONUNBUFFERED 1

COPY . /usr/src

WORKDIR /usr/src

COPY --from=nodebuilder /usr/src/lyrebird/client/ /usr/src/lyrebird/client/

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories \
  && apk update \
  && apk add --no-cache build-base jpeg-dev zlib-dev libffi-dev openssl-dev \
  && pip install --no-cache-dir . -i https://pypi.douban.com/simple \
  && rm -rf /usr/src \
  && apk del --purge build-base jpeg-dev zlib-dev libffi-dev openssl-dev

FROM python:3.8-alpine

ENV PYTHONUNBUFFERED 1

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories \
  && apk update \
  && apk add --no-cache jpeg zlib libffi openssl

COPY --from=pybuilder /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages
COPY --from=pybuilder /usr/local/bin /usr/local/bin

EXPOSE 9090 4272

CMD [ "lyrebird" ]
