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
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
    ],
    entry_points={
        'console_scripts': [
            'lyrebird = lyrebird.manager:main'
        ]
    },
    install_requires=[
        "beautifulsoup4==4.7.1",
        "colorama==0.4.1",
        "Flask==1.1.1",
        "Flask-RESTful==0.3.7",
        "Flask-SocketIO==4.2.1",
        "mitmproxy==5.3.0",
        "packaging==19.0",
        "portpicker==1.3.1",
        "python-socketio==4.6.1",
        "requests==2.21.0",
        "SQLAlchemy==1.3.22",
        "click==7.1.2",
        "urllib3==1.24.2",
        "qrcode==6.1",
        "Pillow==8.0.1",
        "eventlet==0.30.1"
    ],
    extras_require={
        'dev': [
            "autopep8",
            "pylint",
            "pytest",
            "pytest-cov"
        ]
    }
)
