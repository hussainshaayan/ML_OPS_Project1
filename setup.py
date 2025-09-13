from setuptools import setup,find_packages

with open("requirements.txt") as f:
    requirements=f.read().splitlines()
    
setup(
    name="ML_OPS_First_Project",
    version="0.1",
    author="Shaayan",
    package=find_packages(),
    install_requires=requirements,
)