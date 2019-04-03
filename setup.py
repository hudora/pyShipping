long_description = """
pyShipping provides connections to interface with shipping companies and to transport shipping related
information.
"""

from setuptools import setup, find_packages
from distutils.extension import Extension
import codecs

setup(name='pyShipping-python3',
      maintainer='Jon Combe via Maximillian Dornseif',
      maintainer_email='jon@naremit.com',
      url="https://github.com/joncombe/pyShipping-python3",
      version='0.0.1',
      description='pyShipping - Shipping related Toolkit',
      long_description=codecs.open('README.rst', "r", "utf-8").read(),
      classifiers=['License :: OSI Approved :: BSD License',
                   'Intended Audience :: Developers',
                   'Programming Language :: Python'],
      # download_url
      zip_safe=False,
      packages=find_packages(),
      package_data={'': ['README.rst'], 'pyshipping': ['carriers/dpd/georoutetables/*']},
      include_package_data=True,
      # cmdclass = {'build_ext': build_ext}
)

