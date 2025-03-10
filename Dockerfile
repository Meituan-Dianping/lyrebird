FROM node:16-slim as nodebuilder
ARG USE_MIRROR 
COPY . /usr/src
WORKDIR /usr/src/frontend
RUN if [[ -n "$USE_MIRROR" ]] ; then npm --registry https://registry.npmmirror.com install ; else npm install ; fi \
  && npm run build

FROM python:3.9-slim
ARG USE_MIRROR 
ENV PYTHONUNBUFFERED 1

COPY . /usr/src
WORKDIR /usr/src
COPY --from=nodebuilder /usr/src/lyrebird/client/ /usr/src/lyrebird/client/

RUN if [[ -n "$USE_MIRROR" ]] ; then sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list ; fi \
  && apt-get update \
  && apt-get install -y build-essential libjpeg-dev zlib1g-dev libffi-dev libssl-dev curl libstdc++6 tzdata redis-server \
  && if [[ -n "$USE_MIRROR" ]] ; then pip install --upgrade pip  -i https://pypi.tuna.tsinghua.edu.cn/simple && pip install --no-cache-dir . facebook-wda==0.8.1 jsonschema redis -i https://pypi.tuna.tsinghua.edu.cn/simple ; else pip install --upgrade pip && pip install --no-cache-dir . facebook-wda==0.8.1 jsonschema redis ; fi \
  && if [[ -n "$USE_MIRROR" ]] ; then pip install werkzeug==2.2.2 mitmproxy -t /usr/local/mitmenv -i https://pypi.tuna.tsinghua.edu.cn/simple ; else pip install werkzeug==2.2.2 mitmproxy -t /usr/local/mitmenv ; fi \
  && echo -e "#!/bin/sh\nexport PYTHONPATH=/usr/local/mitmenv\npython -c 'from mitmproxy.tools.main import mitmdump;mitmdump()' \$@" > /usr/local/bin/mitmdump \
  && chmod a+x /usr/local/bin/mitmdump \
  && rm -rf /usr/src \
  && apt-get purge -y build-essential \
  && apt-get autoremove -y \
  && apt-get clean

EXPOSE 9090 4272
CMD [ "lyrebird" ]
