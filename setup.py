"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

import os
import sys

from setuptools import setup, find_packages

# pylint: disable=redefined-builtin

here = os.path.abspath(os.path.dirname(__file__))  # pylint: disable=invalid-name

with open(os.path.join(here, "README.rst"), encoding="utf-8") as fid:
    long_description = fid.read()  # pylint: disable=invalid-name

setup(
    name="extract-flash-cards",
    version="0.0.1",
    description="Extract flash cards from a text using ChatGPT.",
    long_description=long_description,
    url="https://github.com/mristin/extract-flash-cards",
    author="Marko Ristin",
    author_email="marko@ristin.ch",
    classifiers=[
        # yapf: disable
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8'
        # yapf: enable
    ],
    license="License :: OSI Approved :: MIT License",
    keywords="chatgpt extract vocabulary flash cards",
    install_requires=[
        "icontract>=2.6.1",
        "openai==0.27.7",
    ],
    extras_require={
        "dev": [
            "black==24.1.1",
            "mypy==1.8.0",
            "pylint==3.0.3",
        ],
    },
    py_modules=["extractflashcards"],
    packages=find_packages(exclude=["continuous_integration"]),
    data_files=[
        (".", ["LICENSE", "README.rst"]),
    ],
    entry_points={
        "console_scripts": [
            "extract-flash-cards=extractflashcards.main:entry_point",
        ]
    },
)
