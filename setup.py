long_description = """
pyShipping provides connections to interface with shipping companies and to transport shipping related
information.
"""

from setuptools import setup, find_packages


setup(name='pyShipping',
      maintainer='Maximillian Dornseif',
      maintainer_email='md@hudora.de',
      version='1.3p3',
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

