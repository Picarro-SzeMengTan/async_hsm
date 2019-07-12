import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="async_hsm",
    version="0.2.0",
    author="Dean Hall, Sze Tan",
    author_email="dwhall256@gmail.com, stan@picarro.com",
    description="Asyncio based Hierarchical State Machines",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        'Intended Audience :: Developers',

        # Python 3.4 (or later) because asyncio is required
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
