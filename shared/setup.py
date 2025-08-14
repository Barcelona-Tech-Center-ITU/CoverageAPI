from setuptools import setup, find_packages

setup(
    name="giga-coverage-shared",
    version="1.0.0",
    description="Shared utilities and components for GIGA Coverage microservices",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.0",
        "sqlalchemy>=1.4.0",
        "pydantic>=2.0.0",
        "psycopg2-binary>=2.9.0"
    ],
    python_requires=">=3.8"
)
