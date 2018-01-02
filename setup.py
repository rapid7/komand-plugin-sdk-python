from setuptools import setup, find_packages

setup(name='komand',
      version='0.3.13',
      description='Komand Plugin SDK',
      author='Komand',
      author_email='support@komand.com',
      url='http://komand.com',
      packages=find_packages(),
      install_requires=[
          'requests>=2.9.1',
          'python_jsonschema_objects==0.3.1',
          'jsonschema==2.3.0',
          'certifi==2017.11.5'
      ],
      test_suite="tests.komand_test_suite",

      )
