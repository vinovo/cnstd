#!/usr/bin/env python3
import os
from setuptools import find_packages, setup
from pathlib import Path

PACKAGE_NAME = "memegle-cnstd"

here = Path(__file__).parent

long_description = (here / "README.md").read_text(encoding="utf-8")

about = {}
exec(
    (here / PACKAGE_NAME.replace('.', os.path.sep) / "__version__.py").read_text(
        encoding="utf-8"
    ),
    about,
)

required = [
    'click',
    'shapely',
    'Polygon3',
    'pyclipper',
    'TensorboardX',
    'opencv-python',
    'numpy>=1.14.0,<1.20.0',
    'pillow>=5.3.0',
    'mxnet>=1.5.0,<1.8.0',
    'gluoncv>=0.3.0,<0.7.0',
]

extras_require = {
    "dev": ["pip-tools", "pytest"],
}

entry_points = """
[console_scripts]
cnstd = cnstd.cli:cli
"""

setup(
    name=PACKAGE_NAME,
    version=about['__version__'],
    description="Chinese STR adapted for use by Memegle",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Paul Zhu',
    author_email='zhz433@ucsd.edu',
    license='Apache 2.0',
    url='https://github.com/vinovo/cnstd',
    platforms=["Mac", "Linux", "Windows"],
    packages=find_packages(),
    entry_points=entry_points,
    include_package_data=True,
    install_requires=required,
    extras_require=extras_require,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
)
