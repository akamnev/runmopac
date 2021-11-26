import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='runmopac',
    version='0.0',
    description='',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    install_requires=[
        'numpy',
        'tqdm'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.8',
)
