long_description = """
pyShipping provides connetions to interface with shipping companier and to transport shipping related
information.
"""

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages


setup(name='pyShipping',
      maintainer='Maximillian Dornseif',
      maintainer_email='md@hudora.de',
      version='1.2p1',
      description='pyShipping - Shipping related Toolkit',
      long_description=long_description,
      classifiers=['License :: OSI Approved :: BSD License',
                   'Intended Audience :: Developers',
                   'Programming Language :: Python'],
      # download_url
      zip_safe=False,
      packages=find_packages(),
      package_data={'pyshipping': ['carriers/dpd/georoutetables/*']},
      include_package_data=True,
)

