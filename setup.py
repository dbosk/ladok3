from setuptools import setup, find_packages

setup(
    name = "ladok3",
    version = "1.7",
    author = "Daniel Bosk, Alexander Baltatzis, Gerald Q. Maguire Jr",
    author_email = "dbosk@kth.se",
    description = "Python wrapper for the LADOK3 REST API",
    long_description = open("README.md").read(),
    long_description_content_type = "text/markdown",
    url = "https://github.com/dbosk/ladok3",
    project_urls = {
        "Bug Tracker": "https://github.com/dbosk/ladok3/issues",
        "Releases": "https://github.com/dbosk/ladok3/releases"
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Utilities"
    ],
    package_dir = {"": "src"},
    packages = ["ladok3"],
    entry_points = {
        "console_scripts": [
            "ladok = ladok3.cli:main"
        ]
    },
    data_files = [
        ("/etc/bash_completion.d", ["src/ladok3/ladok.bash"])
    ],
    python_requires = ">=3.8",
    install_requires = [
        "appdirs>=1.4.4",
        "argcomplete>=1.12.0",
        "cachetools>=4.0.0",
        "requests>=2.24.0",
        "urllib3>=1.25.8"
    ]
)

