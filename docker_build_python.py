import subprocess
import os 

def has_dockerfile(directory):
    return os.path.isfile(f"{directory}/Dockerfile")

def create_dockerfile(directory):
    with open(f"{directory}/Dockerfile", 'w') as f:
        f.write("ENV FILE_PATH")
        f.write('FROM PYTHON:3.10\n')
        f.write('COPY . /app\n')
        f.write('WORKDIR /app\n')
        
        # Edit to include different types of configuration files...! 
        f.write('RUN pip3 install --upgrade pip3 && \
                 test -f requirements.txt && pip3 install -r requirements.txt || true && \
                 test -f Pipfile.lock && pipenv install --ignore-pipfile || true && \
                 test -f setup.py && python3 setup.py || true\n')
        f.write(f"CMD python3 $FILE_PATH\n")

def build_docker_image(directory, file_name, image_name):
    subprocess.run(['docker', 'build', "--build-arg", f"FILE_PATH={file_name}", '-t', image_name, directory])

def run_docker_image(image_name, file_name):
    subprocess.run(['docker', 'run', "-e", f"FILE_PATH=${file_name}", image_name])


# Call the function at the top of Core.
def repo_to_container(directory, file_name, image_name):

    if not has_dockerfile(directory):
        create_dockerfile(directory)
    
    build_docker_image(image_name, file_name, image_name)
    run_docker_image(image_name, file_name)
