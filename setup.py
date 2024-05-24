from setuptools import setup
from pathlib import Path


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='conson',
    version='3.2.1',
    description='A simple json configuration file manager',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Paweł Gabryś',
    author_email='p.gabrys@int.pl',
    packages=['conson'],
    install_requires=['cryptography>=41.0.3'],
)
