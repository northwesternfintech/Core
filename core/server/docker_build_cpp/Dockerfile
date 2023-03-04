FROM gcc

RUN apt-get -y install

RUN apt-get -y update && apt-get install -y \
build-essential \
clang \
cmake \
gdb \
wget \
python3-pip

RUN pip install pybind11

COPY . /usr/src/docker

WORKDIR /usr/src/docker

RUN mkdir build
RUN cmake -S . -B build && cmake --build build

CMD ["./build/helloworld"]