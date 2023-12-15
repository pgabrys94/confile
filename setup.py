from setuptools import setup


setup(
    name='confile',
    version='1.8',
    description='A simple configuration file manager',
    author='Paweł Gabryś',
    author_email='p.gabrys@int.pl',
    packages=['confile'],
    install_requires=['cryptography>=41.0.3'],
)
