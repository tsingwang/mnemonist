from pathlib import Path
from setuptools import setup, find_packages


def get_version():
    with open(Path(__file__).parent / 'mnemonist/VERSION') as version_file:
        return version_file.read().strip()

setup(
    name="mnemonist",
    version=get_version(),
    author="Tsing Wang",
    author_email="tsing.nix@qq.com",
    description="Memory assistant tool for command line",
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/tsingwang/mnemonist",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "mnemonist = mnemonist.main:main",
        ],
    },
    install_requires=[
        "click",
        "SQLAlchemy",
        "rich",
        "textual",
        "textual-image",
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
