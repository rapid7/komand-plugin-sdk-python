from setuptools import setup, find_packages

setup(name='komand',
      version='0.3.4',
      description='Komand Plugin SDK',
      author='Komand',
      author_email='support@komand.com',
      url='http://komand.com',
      packages=find_packages(),
      install_requires=['requests==2.9','python_jsonschema_objects','jsonschema==2.3.0',],
      test_suite="tests.komand_test_suite",

      )
