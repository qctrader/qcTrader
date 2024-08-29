from setuptools import setup, find_packages
import glob

# # Collect all tar chunk files
# tar_chunks = glob.glob("dist/*.tar.gz.part*")
setup(
    name="qcTrader",
    version="1.1.7",
    packages=find_packages(),
    include_package_data=True,
    # package_data={
    #     '': ['Lean/**/*', 'installers/**/*', 'utils/**/*','*.txt', '*.md', '*.cs', '*.csproj', '*.csproj.*', '*.json', '*.bat', '*.sh',  '*.xml',  '*.pdb', '*.dll',  '*.yaml',  '*.config',  '*.exe'],
    # },
    install_requires=[
        'setuptools>=42',
        'wheel>=0.34.2',
        'pythonnet>=2.5.2',
        'pandas>=1.1.5',
        'numpy>=1.19.5',
        'quantconnect',
        'requests',
        'tqdm',
        'distro',
        'pexpect',
        'python-dotenv',
        'wexpect',
        'yfinance'
  

        
        # 'qcTrader-submodule1 @ https://github.com/qcTraderPackages/packages-bundle/releases/download/testing_001/qctrader_submodule1-1.1.7.tar.gz',
        #                             'qcTrader-submodule2 @ https://github.com/qcTraderPackages/packages-bundle/releases/download/testing_001/qctrader_submodule2-1.1.7.tar.gz',
        #                             'qcTrader-submodule3 @ https://github.com/qcTraderPackages/packages-bundle/releases/download/testing_001/qctrader_submodule3-1.1.7.tar.gz',
        #                             'qcTrader-submodule12 @ https://github.com/qcTraderPackages/packages-bundle/releases/download/testing_001/qctrader_submodule12-1.1.7.tar.gz',
        #                             'qcTrader-submodule13 @ https://github.com/qcTraderPackages/packages-bundle/releases/download/testing_001/qctrader_submodule13-1.1.7.tar.gz',
        #                             'qcTrader-submodule14 @ https://github.com/qcTraderPackages/packages-bundle/releases/download/testing_001/qctrader_submodule14-1.1.7.tar.gz',
        #                             'qcTrader-submodule15 @ https://github.com/qcTraderPackages/packages-bundle/releases/download/testing_001/qctrader_submodule15-1.1.7.tar.gz',
        #                             'qcTrader-submodule16 @ https://github.com/qcTraderPackages/packages-bundle/releases/download/testing_001/qctrader_submodule16-1.1.7.tar.gz',
        #                             'qcTrader-submodule18 @ https://github.com/qcTraderPackages/packages-bundle/releases/download/testing_001/qctrader_submodule18-1.1.7.tar.gz',
        #                             'qcTrader-submodule19 @ https://github.com/qcTraderPackages/packages-bundle/releases/download/testing_001/qctrader_submodule19-1.1.7.tar.gz',
        #                             'qcTrader-submodule20 @ https://github.com/qcTraderPackages/packages-bundle/releases/download/testing_001/qctrader_submodule20-1.1.7.tar.gz',
        #                             'qcTrader-submodule21 @ https://github.com/qcTraderPackages/packages-bundle/releases/download/testing_001/qctrader_submodule21-1.1.7.tar.gz',
        #                             'qcTrader-submodule22 @ https://github.com/qcTraderPackages/packages-bundle/releases/download/testing_001/qctrader_submodule22-1.1.7.tar.gz',
        #                             'qcTrader-submodule23 @ https://github.com/qcTraderPackages/packages-bundle/releases/download/testing_001/qctrader_submodule23-1.1.7.tar.gz',
        #                             'qcTrader-submodule24 @ https://github.com/qcTraderPackages/packages-bundle/releases/download/testing_001/qctrader_submodule24-1.1.7.tar.gz',
        #                             'qcTrader-submodule25 @ https://github.com/qcTraderPackages/packages-bundle/releases/download/testing_001/qctrader_submodule25-1.1.7.tar.gz',
        #                             'qcTrader-submodule26 @ https://github.com/qcTraderPackages/packages-bundle/releases/download/testing_001/qctrader_submodule26-1.1.7.tar.gz',
        #                             'qcTrader-submodule27 @ https://github.com/qcTraderPackages/packages-bundle/releases/download/testing_001/qctrader_submodule27-1.1.7.tar.gz',
        #                             'qcTrader-submodule28 @ https://github.com/qcTraderPackages/packages-bundle/releases/download/testing_001/qctrader_submodule28-1.1.7.tar.gz',
        #                             'qcTrader-submodule222 @ https://github.com/qcTraderPackages/packages-bundle/releases/download/testing_001/qctrader_submodule222-1.1.7.tar.gz'


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
