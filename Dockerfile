FROM pytorch/pytorch:1.13.1-cuda11.6-cudnn8-runtime
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /

ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY

ENV AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
ENV AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}

RUN apt-get update && apt-get install -y git
RUN git clone https://github.com/kohya-ss/sd-scripts.git
RUN mv sd-scripts/ sdscripts/

RUN pip3 install --upgrade pip

RUN apt-get install python3-opencv -y

ADD requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ADD server.py .
EXPOSE 8000

ADD download.py .
RUN python3 download.py

ADD app.py .
CMD python3 -u server.py
