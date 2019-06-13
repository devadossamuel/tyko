from setuptools import setup

setup(
    name='avform',
    version='0.0.1',
    packages=['avforms'],
    url='https://github.com/UIUCLibrary/avdatabase',
    license='University of Illinois/NCSA Open Source License',
    author='University Library at The University of Illinois at Urbana '
           'Champaign: Preservation Services',
    author_email='prescons@library.illinois.edu',
    description='Database for handling entering metadata for AV content',
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "pytest-bdd"],
    install_requires=[
        "sqlalchemy",
        "mysqlclient"
        ],
    entry_points={
        "console_scripts": [
            "avdata=avforms.run:main"
        ]
    }
)
