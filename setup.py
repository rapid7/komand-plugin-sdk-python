from setuptools import setup, find_packages

setup(name='komand',
      version='1.0.1',
      description='Komand Plugin SDK',
      author='Komand',
      author_email='support@komand.com',
      url='https://komand.com',
      packages=find_packages(),
      install_requires=[
          'requests>=2.20.0',
          'python_jsonschema_objects==0.3.2',
          'jsonschema==2.3.0',
          'certifi==2017.11.5',
          'six==1.11.0',
          'Flask==0.12.2',
          'gunicorn==19.7.1'
      ],
      tests_require=[
          'pytest',
          'docker',
          'dockerpty'
      ],
      extras_require={
          ':python_version == "2.7"': ['futures']
      },
      test_suite="tests",
      include_package_data=True
      )
