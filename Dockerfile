FROM python:3.9.2
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /app
WORKDIR /app
ADD . /app/

RUN pip install -U pip
RUN make install_requirements

RUN pip3 --no-cache-dir install --upgrade awscli
EXPOSE 8020
CMD ["sh bash"]
