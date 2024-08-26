from setuptools import setup, find_packages

setup(
    name='qcTrader-submodule16',
    version='1.1.7',
    packages=find_packages(),
    install_requires=[
        'clr_loader==0.2.6',
        'matplotlib==3.9.2',
        'numpy==2.1.0',
        'pandas==2.2.2',
        'QuantConnect==0.1.0',
        'scipy==1.14.1',
        'setuptools==73.0.1'
    ],
    description='Submodule 16 for qcTrader',

    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/qctrader/qctrader',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
