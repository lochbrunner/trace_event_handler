import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='trace_event_handler',
    version='0.0.1',
    author='Matthias Lochbrunner',
    author_email='matthias_lochbrunner@web.de',
    description='Python Logging Handler which dumps in the Trace Event Format supported by Chromium based browsers.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/lochbrunner/trace_event_handler',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
