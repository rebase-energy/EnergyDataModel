from setuptools import setup, find_packages

with open("energydatamodel/requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name='energydatamodel',
    version='0.0.2',
    packages=find_packages(),
    install_requires=requirements,
    author='rebase.energy',
    description='Data model for energy modelling.',
)
