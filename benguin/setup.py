from setuptools import setup

setup(
    name='benguin',
    version='4.2.0',
    py_modules=['benguin'],
    entry_points={
        'console_scripts': [
            'benguin = benguin:benguin'
        ]
    }
)