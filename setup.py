from setuptools import setup, find_packages

setup(
    name="qcTrader",
    version="0.1.0",
    packages=find_packages(include=['qcTrader', 'qcTrader.*']),
    install_requires=[
    'setuptools>=42',
    'wheel>=0.34.2',
    'pythonnet>=2.5.2',
    'pandas>=1.1.5',
    'numpy>=1.19.5',
    'quantconnect', 
    'requests',
    'tqdm',
    'distro' 
   ],
    entry_points={
        'console_scripts': [
            'uninstall_qcTrader=qcTrader.uninstall:uninstall_lean_runner',
        ],
    },
    author="Pallavi Priyadarshini",
    author_email="pallavidapriya75@gmail.com",
    description="This is a wrapper around quantConnect engine to calculate results based on trading algorithms",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/qctrader/qctrader",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
