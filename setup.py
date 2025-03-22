from setuptools import setup, find_packages

setup(
    name='energydatamodel',
    version='0.0.2',
    packages=find_packages(),
    install_requires=[
        "pandas",
        "shapely",
        "pytz",
        "ipywidgets",
        "geopandas",
        "anytree",
        "pvlib",
    ],
    author='rebase.energy',
    description='Data model for energy modelling.',
)
