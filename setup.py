from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='komand',
      version='3.4.0',
      description='Komand Plugin SDK',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Rapid7 Integrations Alliance',
      author_email='integrationalliance@rapid7.com',
      url='https://github.com/rapid7/komand-plugin-sdk-python',
      packages=find_packages(),
      install_requires=[
          'requests>=2.20.0',
          'python_jsonschema_objects==0.3.2',
          'jsonschema==2.3.0',
          'certifi==2017.11.5',
          'six==1.11.0',
          'Flask==0.12.3',
          'gunicorn==19.7.1',
          'marshmallow==3.4.0',
          'apispec==3.2.0',
          'apispec-webframeworks==0.5.2'
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
      include_package_data=True,
      classifiers=[
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 2",
          "Operating System :: OS Independent",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Natural Language :: English",
          "Topic :: Software Development :: Build Tools"
      ]
      )
