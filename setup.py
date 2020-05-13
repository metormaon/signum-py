import os
from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


extra_files = package_files('catcha-images')

setup(
    name="signum-py", # Replace with your own username
    version="0.0.1",
    author="Moran Mahabi, Noam Rotem",
    author_email="moran.mahabi@gmail.com, metormaon@gmail.com",
    description="Sign-in tools for Python servers",
    url="https://github.com/metormaon/signum-py",
    package_dir={'signum': 'src'},
    packages=['signum'],
    package_data={'signum': extra_files},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=required
)
