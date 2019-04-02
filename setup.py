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
        "aniso8601==6.0.0",
        "asn1crypto==0.24.0",
        "astroid==2.2.5",
        "atomicwrites==1.3.0",
        "attrs==19.1.0",
        "beautifulsoup4==4.7.1",
        "blinker==1.4",
        "brotlipy==0.7.0",
        "certifi==2019.3.9",
        "cffi==1.12.2",
        "chardet==3.0.4",
        "Click==6.7",
        "colorama==0.4.1",
        "cryptography==2.3.1",
        "Flask==1.0.2",
        "Flask-RESTful==0.3.7",
        "Flask-SocketIO==3.3.2",
        "h11==0.7.0",
        "h2==3.1.0",
        "hpack==3.0.0",
        "hyperframe==5.2.0",
        "idna==2.8",
        "isort==4.3.16",
        "itsdangerous==1.1.0",
        "Jinja2==2.10",
        "kaitaistruct==0.8",
        "lazy-object-proxy==1.3.1",
        "ldap3==2.5.2",
        "MarkupSafe==1.1.1",
        "mccabe==0.6.1",
        "mitmproxy==4.0.4",
        "more-itertools==7.0.0",
        "packaging==19.0",
        "passlib==1.7.1",
        "pluggy==0.9.0",
        "portpicker==1.3.1",
        "py==1.8.0",
        "pyasn1==0.4.5",
        "pycparser==2.19",
        "pylint==2.3.1",
        "pyOpenSSL==18.0.0",
        "pyparsing==2.2.2",
        "pyperclip==1.6.5",
        "pytest==3.9.3",
        "python-engineio==3.5.0",
        "python-socketio==3.1.2",
        "pytz==2018.9",
        "requests==2.21.0",
        "ruamel.yaml==0.15.89",
        "six==1.12.0",
        "sortedcontainers==2.0.5",
        "soupsieve==1.9",
        "SQLAlchemy==1.3.1",
        "tornado==5.1.1",
        "typed-ast==1.3.1",
        "urllib3==1.24.1",
        "urwid==2.0.1",
        "Werkzeug==0.15.1",
        "wrapt==1.11.1",
        "wsproto==0.11.0"
    ]
    )
