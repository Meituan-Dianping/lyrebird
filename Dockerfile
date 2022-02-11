FROM node:14.15-alpine as nodebuilder
ARG USE_MIRROR 
COPY . /usr/src
WORKDIR /usr/src/frontend
RUN if [[ -n "$USE_MIRROR" ]] ; then npm --registry https://registry.npmmirror.com install ; else npm install ; fi \
  && npm run build

FROM python:3.8-alpine as pybuilder
ARG USE_MIRROR 
ENV PYTHONUNBUFFERED 1
COPY . /usr/src
WORKDIR /usr/src
COPY --from=nodebuilder /usr/src/lyrebird/client/ /usr/src/lyrebird/client/
RUN if [[ -n "$USE_MIRROR" ]] ; then sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories ; fi \
  && apk update \
  && apk add --no-cache build-base jpeg-dev zlib-dev libffi-dev openssl-dev \
  && if [[ -n "$USE_MIRROR" ]] ; then pip install --no-cache-dir . facebook-wda==0.8.1 jsonschema -i https://pypi.douban.com/simple ; else pip install --no-cache-dir . facebook-wda==0.8.1 jsonschema ; fi \
  && rm -rf /usr/src \
  && apk del --purge build-base jpeg-dev zlib-dev libffi-dev openssl-dev

FROM python:3.8-alpine
ARG USE_MIRROR 
ENV PYTHONUNBUFFERED 1
RUN if [[ -n "$USE_MIRROR" ]] ; then sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories ; fi \
  && apk update \
  && apk add --no-cache jpeg zlib libffi openssl curl libstdc++ tzdata
COPY --from=pybuilder /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages
COPY --from=pybuilder /usr/local/bin /usr/local/bin

EXPOSE 9090 4272
CMD [ "lyrebird" ]
