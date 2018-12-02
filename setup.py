#!/usr/bin/env python3

from os import path

from setuptools import setup, find_packages

import deserialize

def run_setup():
    """Run package setup."""
    here = path.abspath(path.dirname(__file__))

    # Get the long description from the README file
    with open(path.join(here, 'README.md')) as f:
        long_description = f.read()

    setup(
        name='deserialize',
        version=deserialize.__version__,
        description='A library to make deserialization easy.',
        long_description=long_description,
        long_description_content_type="text/markdown",
        url='https://github.com/dalemyers/deserialize',
        author='Dale Myers',
        author_email='dale@myers.io',
        license='MIT',
        install_requires=[],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.7',
            'Topic :: Software Development :: Libraries'
        ],

        keywords='deserialization, deserialize, objects, object, json',
        packages=find_packages(exclude=['docs', 'tests'])
    )

if __name__ == "__main__":
    run_setup()
