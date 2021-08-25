# -*- coding: utf-8 -*-

import os
import re

from setuptools import find_packages, setup

version = ""
with open("hcspy/__init__.py", encoding="UTF8") as f:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE
    ).group(1)

path = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")

requirements = []
with open(f"{path}/requirements.txt", encoding="UTF8") as f:
    requirements = f.read().splitlines()

if not version:
    raise RuntimeError("version is not defined")

with open(f"{path}/README.md", encoding="UTF8") as f:
    readme = f.read()

setup(
    name="hcspy",
    author="decave27",
    author_email="decave27@gmail.com",
    url="https://github.com/decave27/hcspy",
    project_urls={
        "Source": "https://github.com/decave27/hcspy",
        "Tracker": "https://github.com/decave27/hcspy/issues",
    },
    version=version,
    packages=find_packages(),
    license="GPL-V3",
    description="코로나 자가진단 파이썬 라이브러리",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=requirements,
    keywords=["korea", "covid", "auto", "hcspy", "corona", "covid19"],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Development Status :: 5 - Production/Stable",
    ],
)
