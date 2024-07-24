from setuptools import setup, find_packages

setup(
    name='prover_cli',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'argparse',
    ],
    entry_points={
        'console_scripts': [
            'prover-cli=prover_cli.cli:main',
        ],
    },
    description='CLI tool for running block proving tasks and collecting performance metrics.',
    author='Daniel Paul Moore',
    author_email='dmoore@polygon.technology',
    url='https://github.com/0xPolygon/prover-cli',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

