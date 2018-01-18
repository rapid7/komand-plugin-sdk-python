from setuptools import setup, find_packages

setup(name='komand',
<<<<<<< HEAD
      version='0.4.0',
=======
      version='0.3.13',
>>>>>>> origin/master
      description='Komand Plugin SDK',
      author='Komand',
      author_email='support@komand.com',
      url='http://komand.com',
      packages=find_packages(),
<<<<<<< HEAD
      install_requires=['requests==2.9', 'python_jsonschema_objects', 'jsonschema==2.3.0', 'flask'],
=======
      install_requires=[
          'requests>=2.9.1',
          'python_jsonschema_objects==0.3.1',
          'jsonschema==2.3.0',
          'certifi==2017.11.5'
      ],
>>>>>>> origin/master
      test_suite="tests.komand_test_suite",
     )
