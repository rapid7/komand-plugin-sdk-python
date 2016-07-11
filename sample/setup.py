from setuptools import setup, find_packages

setup(name='foobar-komand-plugin',
      version='0.1',
      description='Komand Sample Python Plugin',
      author='Komand',
      author_email='support@komand.com',
      url='http://komand.com',
      packages=find_packages(),
      install_requires=['komand'],
      scripts=['bin/foobar']
      )
