import subprocess
import os 

def has_dockerfile(directory):
    return os.path.isfile(f"{directory}/Dockerfile")

def create_dockerfile(directory):
    with open(f"{directory}/Dockerfile", 'w') as f:
        f.write('FROM python:3.10\n')
        f.write('ARG FILE_PATH\n')
        f.write("ENV FILE_PATH $FILE_PATH\n")
        f.write('COPY . /app\n')
        f.write('WORKDIR /app\n')
        
        f.write('RUN apt-get update && apt-get install -y python3.10 python3-pip &&\
                 test -f requirements.txt && pip3 install -r requirements.txt || true && \
                 test -f Pipfile.lock && pipenv install --ignore-pipfile || true && \
                 test -f setup.py && pip3 install setup.py || true\n')
        f.write("CMD python3 $FILE_PATH\n")

def build_docker_image(directory, file_path, image_name):
    subprocess.run(['docker', 'build', "--build-arg", f"FILE_PATH={file_path}", '-t', image_name, directory])

def run_docker_image(image_name, file_path):
    subprocess.run(['docker', 'run', "-e", f"FILE_PATH={file_path}", image_name])

def repo_to_container(directory, file_path, image_name):
    if not has_dockerfile(directory):
        create_dockerfile(directory)
    
    build_docker_image(directory, file_path, image_name)
    run_docker_image(image_name, file_path)


repo_to_container("../Desk-Alpha-Fork/Strats/BollingerBands", "BollingerBandsMultiStock.py", "test")
