# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

setup(
    name='fractalis-thehyve',
    packages=find_packages(),
    author='Sascha Herzinger',
    author_email='sascha.herzinger@uni.lu',
    url='https://github.com/thehyve/Fractalis',
    version='1.3.1.hyve1',
    license='Apache2.0',
    include_package_data=True,
    python_requires='>=3.6.0',
    install_requires=[
        'Flask==1.1.1',
        'flask-cors==3.0.8',
        'Flask-Script==2.0.6',
        'flask-request-id-middleware==1.1',
        'flask-compress==1.4.0',
        'jsonschema==3.2.0',
        'celery[redis]==4.3.0',
        'kombu==4.6.6',
        'redis==3.2.1',
        'numpy>=1.14.3,<1.15.0',
        'scipy==1.3.2',
        'pandas>=0.25.1,<0.26.0',
        'scikit-learn==0.21.3',
        'lifelines==0.23.0',
        'requests==2.22.0',
        'PyYAML>=5.1,<5.2',
        'pycryptodomex==3.9.4',
        'rpy2==2.9.5',  # 3.2.2 requires some changes in array_stats.py
        'tzlocal',
        'cryptography==2.6.1',
        'pyjwt==1.7.1',
        'pydantic==1.2'
    ],
    setup_requires=[
        'pytest-runner',
        'twine',
        # dependency for `python setup.py bdist_wheel`
        'wheel'
    ],
    tests_require=[
        'flake8',
        'pytest',
        'pytest-cov',
        'responses'
    ]
)
