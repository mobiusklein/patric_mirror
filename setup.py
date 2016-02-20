from setuptools import setup, find_packages


required = []
with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='patric_mirror',
    version='0.0.1',
    packages=find_packages(),
    install_requires=required,
    description=("A library for making a local copy of the Pathosystems "
                 "Resource Integration Center's genome annotations in a relational database.")
    )
