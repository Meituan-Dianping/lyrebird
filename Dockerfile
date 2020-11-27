# Build FE
FROM node:10.16.3 as nodeos

COPY . /usr/src/app

WORKDIR /usr/src/app/frontend

RUN npm install \
    && npm run build

# Build lyrebird
FROM alpine:3.12.1

ENV LANG=en_US.UTF-8

COPY . /usr/src/app

WORKDIR /usr/src/app

COPY --from=nodeos /usr/src/app/lyrebird/client/ /usr/src/app/lyrebird/client/

# Add our user first to make sure the ID get assigned consistently,
# regardless of whatever dependencies get added.
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories \
    && addgroup -S lyrebird && adduser -S -G lyrebird lyrebird \
    && apk add --no-cache \
    su-exec \
    git \
    g++ \
    libffi \
    libffi-dev \
    libstdc++ \
    openssl \
    openssl-dev \
    python3 \
    python3-dev \
    libxml2-dev libxslt-dev libffi-dev gcc musl-dev libgcc \
    jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
    curl \
    && python3 -m ensurepip --upgrade \
    && pip3 install -U pip \
    && pip3 install wheel \
    && LDFLAGS=-L/lib pip3 install -U . \
    && pip install facebook-wda jsonschema \
    && apk del --purge \
    git \
    g++ \
    libffi-dev \
    openssl-dev \
    python3-dev \
    libxml2-dev libxslt-dev libffi-dev gcc musl-dev libgcc \
    jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
    && rm -rf ~/.cache/pip /usr/src/app


EXPOSE 9090 4272

CMD [ "lyrebird" ]
