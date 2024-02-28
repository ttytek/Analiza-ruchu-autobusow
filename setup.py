from setuptools import setup, find_packages

setup(
    name='Analiza ruchu autobusów',
    version='1.0',
    packages=find_packages(),
    install_requires=[
    'geopy',
    'datetime',
    'matplotlib',
    'numpy',
    'pstats'
    ],
)