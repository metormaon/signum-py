from distutils.core import setup

setup(
    name="signum-py", # Replace with your own username
    version="0.0.1",
    author="Moran Mahabi, Noam Rotem",
    author_email="moran.mahabi@gmail.com, metormaon@gmail.com",
    description="Sign-in tools for Python servers",
    url="https://github.com/metormaon/signum-py",
    package_dir={'signum': 'src'},
    packages=['signum'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
