from setuptools import setup, find_packages

setup(name='orca',
      version='0.1',
      description='Orca SDK',
      author='Orca',
      author_email='info@orcalabs.io',
      url='http://orcalabs.io',
      packages=find_packages(),
      install_requires=[],
      test_suite="tests.orca_test_suite",

      )
