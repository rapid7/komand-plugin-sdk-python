from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="insightconnect-plugin-runtime",
    version="4.0.1",
    description="InsightConnect Plugin Runtime",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rapid7 Integrations Alliance",
    author_email="integrationalliance@rapid7.com",
    url="https://github.com/rapid7/komand-plugin-sdk-python",
    packages=find_packages(),
    install_requires=[
        "requests>=2.23.0",
        "python_jsonschema_objects==0.3.12",
        "jsonschema==3.2.0",
        "certifi==2019.11.28",
        "Flask==1.1.1",
        "gunicorn==20.0.4",
        "marshmallow==3.4.0",
        "apispec==3.2.0",
        "apispec-webframeworks==0.5.2",
    ],
    tests_require=[
        "pytest",
        "docker",
        "dockerpty",
        "swagger-spec-validator",
        "pre-commit",
    ],
    test_suite="tests",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Topic :: Software Development :: Build Tools",
    ],
)
