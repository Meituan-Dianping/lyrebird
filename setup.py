import runpy
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

VERSION = runpy.run_path(
    os.path.join(here, "lyrebird", "version.py")
)["VERSION"]

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(os.path.join(here, 'install_requires.txt'), encoding='utf-8') as f:
    install_requires_str = f.read()
    install_requires = install_requires_str.split()

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
    install_requires=install_requires,
    extras_require={
        'dev': [
            "autopep8",
            "pylint",
            "pytest",
            "pytest-cov"
        ]
    }
)
