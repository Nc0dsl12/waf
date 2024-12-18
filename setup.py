from setuptools import setup, find_packages

setup(
    name="website",
    packages=find_packages(),
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'flask-login',
    ],
)
