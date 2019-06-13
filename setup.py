#!/usr/bin/env python
# encoding: utf-8

from setuptools import (setup, find_packages)

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name="sms-store",
    version="1.1.0",
    packages=find_packages(),

    # metadata for upload to PyPI
    author="Vision Network",
    author_email="michael@vision.network",
    description="SMS Store.",
    keywords='SMS Store, SMS, Store',

    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VisionNetworkProject/python-sms-store",

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    install_requires=[
        'requests',
        'profig',
        'cli-print',
    ],
)
