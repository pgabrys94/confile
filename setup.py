from setuptools import setup


setup(
    name='conson',
    version='1.9',
    description='A simple json configuration file manager',
    author='Paweł Gabryś',
    author_email='p.gabrys@int.pl',
    packages=['conson'],
    install_requires=['cryptography>=41.0.3'],
)
