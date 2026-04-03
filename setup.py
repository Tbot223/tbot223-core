from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='tbot223-core',
    version='4.0.0',
    description='Python utility library with Result pattern for consistent error handling, file operations, parallel execution, and logging.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='tbot223',
    author_email='tbotxyz@gmail.com',
    url='https://github.com/Tbot223/tbot223-core',
    install_requires=[],
    packages=find_packages(include=['tbot223_core', 'tbot223_core.*']),
    package_data={"tbot223_core": ["py.typed"]},
    keywords=[
        'result-pattern', 'error-handling', 'result',
        'file-operations', 'atomic-write', 
        'parallel-execution', 'thread-pool', 'process-pool',
        'logging', 'exception-tracking',
        'shared-memory', 'thread-safe',
        'utilities', 'debugging'
    ],
    python_requires='>=3.10',
    classifiers=[
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'License :: OSI Approved :: Apache Software License',
    ],
)
