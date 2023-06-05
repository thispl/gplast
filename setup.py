from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in gplast/__init__.py
from gplast import __version__ as version

setup(
	name="gplast",
	version=version,
	description="development",
	author="Teampro",
	author_email="erp.teamproit.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
