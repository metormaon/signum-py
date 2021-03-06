
from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(
    name="signum-py",
    version="0.0.1",
    author="Moran Mahabi, Noam Rotem",
    author_email="moran.mahabi@gmail.com, metormaon@gmail.com",
    description="Sign-in tools for Python servers",
    url="https://github.com/metormaon/signum-py",
    package_dir={'signum': 'src', 'captcha-images': 'captcha-images'},
    packages=['signum', 'captcha-images'],
    package_data={'captcha-images': ['*'], '': ['LICENSE']},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=required
)
