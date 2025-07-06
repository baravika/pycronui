from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

def get_reqs():
    with open(here / "requirements.txt") as f:
        reqs = f.readlines()
    return reqs

setup(
    name="pycronui",
    version="0.0.1",
    packages=find_packages(include=['pycronui']),
    python_requires=">=3.11",
    install_requires=get_reqs(),
    include_package_data=True
)