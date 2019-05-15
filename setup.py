from setuptools import setup

with open('HISTORY.rst') as history_file:
    history = history_file.read()

exec(open('microanalyser/__init__.py').read())

def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='microanalyser',
      version=__version__,
      description='Read a MicroTOSCA model of a microservice-based architecture and discover architectural smells',
      long_description=readme() + '\n\n' + history,
      url='',
      include_package_data=True,
      author=__author__,
      author_email=__email__,
      license='MIT',
      keywords='microservice TOSCA smells refactorings',
      packages=['microanalyser'],
      install_requires=[
          'ruamel.yaml','tosca-parser'
      ],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose'],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'microanalyserm=microanalyser.command_line:main',
        ],
    },
)
