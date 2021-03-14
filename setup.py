import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="AmazonEnviroSensors", # Replace with your own username
    version="0.2.0",
    author="Diarmuid Collins",
    author_email="diarmuid.m.collins+github@gmail.com",
    description="Amazon Environmental sensors",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
          'bluepy',
    ],
    url="https://github.com/diarmuid/AmazonEnviroSensors",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)