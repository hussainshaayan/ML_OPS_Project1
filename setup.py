from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="ML_OPS_First_Project",
    version="0.1",
    author="Shaayan",
    packages=find_packages(where="src"),
    package_dir={"": "src"},  # Tells setuptools that packages live in src/
    install_requires=requirements,
)
