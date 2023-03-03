import subprocess
import os 



def has_dockerfile(directory):
    '''Given a directory path, check if a Dockerfile exists at the top level of that folder. '''
    return os.path.isfile(f"{directory}/Dockerfile")

def create_dockerfile(directory):
    '''Given a directory path, create a dockerfile at the top level of that folder that install dependencies based on the directory contents. '''
    with open(f"{directory}/Dockerfile", 'w') as f:
        f.write('FROM python:3.10\n')
        f.write('ARG FILE_PATH\n')
        f.write("ENV FILE_PATH $FILE_PATH\n")
        f.write('COPY . /app\n')
        f.write('WORKDIR /app\n')
        

        # Check for whether or not a certain type of dependencies file exists (e.g. requirements.txt) and if so, install related dependencies
        f.write('RUN apt-get update && apt-get install -y python3.10 python3-pip &&\
                 test -f requirements.txt && pip3 install -r requirements.txt || true && \
                 test -f Pipfile.lock && pipenv install --ignore-pipfile || true && \
                 test -f setup.py && pip3 install setup.py || true\n')
        f.write("CMD python3 $FILE_PATH\n")

def build_docker_image(directory, file_path, image_name):
    '''Given a directory path, a path to a file to be run by a container and the image name, build a docker container using the Dockerfile located in the given directory path. The built container will run the function at file_path, and the container can be run using the image name. '''
    subprocess.run(['docker', 'build', "--build-arg", f"FILE_PATH={file_path}", '-t', image_name, directory])

def repo_to_container(directory, file_path, image_name):
    '''Calls build docker image with file path and image name after checking that the given directory contains a Dockerfile (and creates one before building a container if not).'''
    if not has_dockerfile(directory):
        create_dockerfile(directory)
    
    build_docker_image(directory, file_path, image_name)


