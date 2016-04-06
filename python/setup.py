from setuptools import setup, find_packages

setup(name='komand',
      version='0.1',
      description='Komand Plugin SDK',
      author='Komand',
      author_email='support@komand.com',
      url='http://komand.com',
      packages=find_packages(),
      install_requires=['requests==2.9','jsonschema==2.5'],
      test_suite="tests.komand_test_suite",

      )
