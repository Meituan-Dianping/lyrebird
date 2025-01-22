import runpy
import os
import sys
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

VERSION = runpy.run_path(
    os.path.join(here, "lyrebird", "version.py")
)["VERSION"]


# Formatting (Spaces, etc.) in requirement must be consistent based on string parsing
def read_requirements(file_path):
    with open(file_path, encoding='utf-8') as f:
        return [
            line.strip().split(';')[0].strip()
            for line in f
            if line.strip() and not line.startswith('#') and (
                '; python_version' not in line or
                check_version_condition(line.split(';')[1].strip())
            )
        ]


def check_version_condition(condition):
    if not condition.startswith('python_version'):
        return True
    op, ver = condition.split(' ', 1)[1].split(' ')
    current_ver = sys.version_info[:2]
    ver = tuple(map(int, ver.strip('"').split('.')))
    return {
        '>': current_ver > ver,
        '>=': current_ver >= ver,
        '<': current_ver < ver,
        '<=': current_ver <= ver,
        '==': current_ver == ver
    }.get(op)


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
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
    ],
    entry_points={
        'console_scripts': [
            'lyrebird = lyrebird.manager:main'
        ]
    },
    setup_requires=['packaging'],
    install_requires=read_requirements('requirements.txt.lock'),
    extras_require={
        'dev': read_requirements('requirements.dev.txt')
    }
)
