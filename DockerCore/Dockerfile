# syntax=docker/dockerfile:1 
FROM ubuntu:22.04 
# insert required credentials if applicable

# install app dependencies 
RUN apt-get update && apt-get install -y python3.10 python3-pip wget && apt-get install unzip 
# install app 
RUN wget https://github.com/northwesternfintech/Core/archive/dev.zip -O Core.zip && unzip -d . Core.zip && rm Core.zip && mv Core-* Core && \ 
mkdir ~/.nuft && cd ~/.nuft && mkdir server && mkdir logs && printf '%s\n' '[server]' 'host = 127.0.0.1' 'port = 54427' > config.ini 
WORKDIR Core 
RUN pip3 install -e . 

WORKDIR Core
CMD ["nuft"]
# CMD ["nuft", "start"]
