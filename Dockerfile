#syntax=docker/dockerfile:1 
FROM python:3.10 
# insert required credentials if applicable

# install app dependencies
RUN apt-get update && apt-get install -y python3.10 python3-pip && mkdir Core/
COPY . Core/

RUN cd Core &&  pip3 install -e . 
WORKDIR Core
CMD ["nuft"]
# CMD ["nuft", "start"]
