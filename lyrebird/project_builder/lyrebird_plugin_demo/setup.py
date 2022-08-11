from setuptools import setup, find_packages
import runpy
import os

here = os.path.abspath(os.path.dirname(__file__))

VERSION = runpy.run_path(
    os.path.join(here, '{{project_name}}', 'version.py')
)['VERSION']

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='{{package_name}}',
    version=VERSION,
    packages=find_packages(),
    url='',
    author='',
    author_email='',
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
    ],
    entry_points={
        'lyrebird_plugin': [
            '{{project_name}} = {{project_name}}.manifest'
        ]
    },
    install_requires=[
        'lyrebird'
    ]
)
