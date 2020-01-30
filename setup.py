from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='wireframe2code',
    packages=find_packages(exclude=["*.test", "*.test.*", "test.*", "test"]),
    exclude=[''],
    version='1.0.0-SNAPSHOT',
    description='An experimental wireframe to code tool',
    author='Angela Guardian',
    author_email='jillguardian@gmail.com',
    url='https://docs.google.com/document/d/1M9vRmGvUtWRM-Th1hrMKeBZBLi4AJ7sj2X5cRXpBXrU',
    classifiers='''
    Programming Language :: Python
    Programming Language :: Python :: 3
    Operating System :: OS Independent
    Development Status :: 3 - Alpha
    Environment :: Console
    Intended Audience :: Developers
    Topic :: Scientific/Engineering :: Image Recognition
    ''',
    python_requires='>=3.7',
    install_requires=[
        'numpy',
        'imutils',
        'opencv-contrib-python',
        'pytest',
        'more-itertools'
    ]
)