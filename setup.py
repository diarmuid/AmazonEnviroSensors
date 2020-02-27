import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Newkiton", # Replace with your own username
    version="0.0.4",
    author="Diarmuid Collins",
    author_email="diarmuid.m.collins+github@gmail.com",
    description="Newkiton temperature sensor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
          'bluepy',
    ],
    url="https://github.com/diarmuid/Newkiton",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)