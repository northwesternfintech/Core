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
	packages = ['build-essential', 'clang', 'cmake', 'gdb', 'wget']
	for package in packages:
		INSTALLATIONS += f' \\\n{package}'

	COPY = '\n\nCOPY . /usr/src/docker'

	WORKDIR = '\n\nWORKDIR /usr/src/docker'
	
	project_name = path.split('/')[-1]
	file_name = relative_file_path.split('/')[-1].split('.')[0]

	### install dependencies here!
	MAKE = F'\n\nRUN make' if os.path.exists(f"{path}makefile") else ''

	COMPILE = f'\n\nRUN g++ -o {file_name} {relative_file_path}'

	RUN = f'\n\nCMD ["./{file_name}"]'

	DOCKERFILE = ''.join([BASE_IMAGE, UPDATE, INSTALLATIONS, COPY, WORKDIR, MAKE, COMPILE, RUN])

	with open(f'{path}/Dockerfile', 'w+') as Dockerfile:
		Dockerfile.write(DOCKERFILE)

def main():
	# path = "./Strats/Template/stevenewald/"
	# relative_file_path = 'multistrat.cpp'
	# create_Dockerfile(path, relative_file_path)
	# for testing on Desk-Alpha on steve-dev
	pass
