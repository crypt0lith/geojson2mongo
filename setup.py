import subprocess

from setuptools import find_packages, setup
from setuptools.command.install import install


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        install.run(self)
        subprocess.call(['python', 'post_install.py'])


setup(
    name='geojson2mongo', version='0.1.0', packages=find_packages(),
    install_requires=['dill', 'pymongo', 'python-dotenv', 'setuptools', 'rarfile'],
    url='https://github.com/crypt0lith/geojson2mongo', license='', author='crypt0lith', author_email='',
    description='A tool for loading and mapping GeoJSON data in MongoDB.', cmdclass={
        'install': PostInstallCommand,
    })
