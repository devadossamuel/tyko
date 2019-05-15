from setuptools import setup

setup(
    name='avform',
    version='0.0.1',
    packages=['avforms'],
    url='https://library.illinois.edu',
    license='University of Illinois/NCSA Open Source License',
    author=
        'University Library at The University of Illinois at Urbana '
        'Champaign: Preservation Services',
    author_email='prescons@library.illinois.edu',
    description='',
    install_requires=[
        "sqlalchemy",
        "mysqlclient"
        ]
)
