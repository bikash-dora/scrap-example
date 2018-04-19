# sets up the environment for testing
import sys, os
from setuptools import setup

sys.path.append('../utils')
sys.path.append('../aggregator')
sys.path.append('../scraper')
sys.path.append('../adverts_controller')
sys.path.append('../db_cleaner')

setup(
    name='sls-basics-tests',
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'boto3', 'moto', 'simplejson', 'requests-mock', 'mechanicalsoup']
)