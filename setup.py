import subprocess
import sys

from setuptools import find_packages, setup
from setuptools.command.install import install


class PostInstallCommand(install):
    """
    Post-installation for installation mode.

        Extracts .zip files in **/archives** to their designated locations.
    """

    def run(self):
        install.run(self)
        subprocess.check_call([sys.executable, "post_install.py"])


setup(
    name='geojson2mongo', version='0.1.0', packages=find_packages(),
    install_requires=['dill', 'pymongo', 'python-dotenv'], url='https://github.com/crypt0lith/geojson2mongo',
    license='', author='crypt0lith', author_email='',
    description='A tool for loading and mapping GeoJSON data in MongoDB.', cmdclass={
        'install': PostInstallCommand,
    }, entry_points={
        'console_scripts': ['geojson2mongo=geojson2mongo.loader:main', ],
    }, include_package_data=True,)
