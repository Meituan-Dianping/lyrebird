FROM python:3.7.5 as pyos

COPY . /usr/src/app

WORKDIR /usr/src/app

RUN pip install --upgrade pip \
    && pip install . -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && rm -rf /usr/src/app

FROM python:3.7.5

COPY --from=pyos /usr/local/lib/python3.7/site-packages /usr/local/lib/python3.7/site-packages
COPY --from=pyos /usr/local/bin /usr/local/bin

WORKDIR /root

EXPOSE 9090
EXPOSE 4272

ENV LC_ALL=C.UTF-8
ENV LANG C.UTF-8

CMD [ "lyrebird" ]
