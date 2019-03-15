import runpy
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

VERSION = runpy.run_path(
        os.path.join(here, "lyrebird", "version.py")
    )["VERSION"]

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='lyrebird',
    version=VERSION,
    packages=['lyrebird'],
    url='https://github.com/meituan/lyrebird',
    author='HBQA',
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    zip_safe=False,
    classifiers=(
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
    ),
    entry_points={
        'console_scripts': [
            'lyrebird = lyrebird.manager:main'
        ]
    },
    install_requires=[
        'mitmproxy==4.0.4',
        'flask==1.0.2',
        'requests==2.21.0',
        'colorama==0.4.1',
        'flask-socketio==3.3.1', 
        'flask-restful==0.3.7', 
        'beautifulsoup4==4.7.1',
        'portpicker==1.3.0', 
        'colorama==0.4.1',
        'packaging==19.0',
        'SQLAlchemy==1.2.18'
    ])
