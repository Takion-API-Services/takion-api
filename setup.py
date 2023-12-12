from setuptools import setup, find_packages

setup(
    name='takion_api',
    version='0.1.23',
    packages=find_packages(),
    install_requires=[
        line.strip() for line in open("requirements.txt", "r").readlines()
    ],
    author='glizzykingdreko',
    author_email='glizzykingdreko@protonmail.com',
    description='Official Python wrapper for TakionAPI services, designed for efficient automation and bypass of advanced antibot systems.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Takion-API-Services/takion-api',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    keywords=[
        "takion-api",
        "takion",
        "datadome",
        "antibot",
        "bypass",
    ],
    python_requires='>=3.6',
)