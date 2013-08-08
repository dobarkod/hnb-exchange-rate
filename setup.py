#!/usr/bin/env python

from setuptools import setup, find_packages, Command
import os
import sys


class BaseCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


class TestCommand(BaseCommand):

    description = "run self-tests"

    def run(self):
        ret = os.system('python tests.py')
        if ret != 0:
            sys.exit(-1)


class CoverageCommand(BaseCommand):
    description = "run self-tests and report coverage (requires coverage.py)"

    def run(self):
        r = os.system('coverage run --source=hnbexchange tests.py')
        if r != 0:
            sys.exit(-1)
        os.system('coverage html')

# To install the HNB Exchange library, open a Terminal shell, then run this
# file by typing:
#
# python setup.py install

if sys.version_info.major == 3 and sys.version_info.minor == 3:
    REQUIRES = ["requests>=1.2.3"]
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
    ]
else:
    REQUIRES = ["requests>=1.2.3", "mock>=1.0.1"]
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
    ]

setup(
    name='HNB-Exchange-Rate',
    version='0.0.1',
    author='Neven Mundar',
    author_email='neven.mundar@dobarkod.hr',
    description='HNB Exchange Rate retrieval and parsing',
    license='MIT',
    url='https://github.com/dobarkod/hnb-exchange-rate/',
    classifiers=[
        "Development Status :: 1 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ].extend(classifiers),
    packages=find_packages(),
    install_requires=REQUIRES,
    cmdclass={
        'test': TestCommand,
        'coverage': CoverageCommand
    }
)
