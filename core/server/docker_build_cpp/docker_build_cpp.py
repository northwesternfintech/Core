import os
'''
1. Take C++ directory path as input
2. Copy directory into container
3. Install dependencies by looking at
	CMakeLists.txt, vcpkg, .pro file from qtcreator
4. Handle C++ versions (take as parameter, set default), compilers, package installs, make files
5. Run C++ file
'''


def dependency_type(path):
	'''
	return how dependencies are managed
	done manually for now for makefile only
	'''
	pass


def create_Dockerfile(path, relative_file_path):
	'''
	Takes in C++ project directory path and writes a Dockerfile for it
	'''
	base_image = 'gcc'
	BASE_IMAGE = f'FROM {base_image}'
	
	UPDATE = '\n\nRUN apt-get -y install'

	INSTALLATIONS = f'\n\nRUN apt-get -y update && apt-get install -y'
	packages = ['build-essential', 'clang', 'cmake', 'gdb', 'wget', 'python3-pip',]
	for package in packages:
		INSTALLATIONS += f' \\\n{package}'
	
	PYBIND = '\n\nRUN pip install pybind11'

	COPY = '\n\nCOPY . /usr/src/docker'

	WORKDIR = '\n\nWORKDIR /usr/src/docker'
	
	project_name = path.split('/')[-1]
	file_name = relative_file_path.split('/')[-1].split('.')[0]

	### install dependencies here!
	# MAKE = f'\n\nRUN make' if os.path.exists(f"{path}makefile") else '' # change to Cmake

	CMAKE = f'\n\nRUN mkdir build\nRUN cmake -S . -B build && cmake --build build' # if os.path.exists("CMakeLists.txt") else ''

	# COMPILE = f'\n\nRUN g++ -o {file_name} {relative_file_path}'

	RUN = f'\n\nCMD ["./build/{file_name}"]'

	DOCKERFILE = ''.join([BASE_IMAGE, UPDATE, INSTALLATIONS, PYBIND, COPY, WORKDIR, CMAKE, RUN])

	with open(f'{path}/Dockerfile', 'w+') as Dockerfile:
		Dockerfile.write(DOCKERFILE)

def main():
	# demo
	path = "./core/server/docker_build_cpp"
	relative_file_path = 'helloworld.cpp'
	create_Dockerfile(path, relative_file_path)

if __name__ == "__main__":
	main()