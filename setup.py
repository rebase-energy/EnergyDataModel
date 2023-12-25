from setuptools import setup, find_packages

setup(
    name='EnergyDataModel',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        "pandas",
        "shapely",
        "pytz"
    ],
    author='rebase.energy',
    description='Data model for energy modelling.',
)