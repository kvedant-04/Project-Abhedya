"""
Setup configuration for Abhedya Air Defense System.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="abhedya",
    version="1.0.0",
    description="Abhedya Air Defense System - Software-only simulation and decision-intelligence platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Abhedya Development Team",
    url="https://github.com/yourusername/abhedya",
    packages=find_packages(exclude=["tests", "examples"]),
    python_requires=">=3.9",
    install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="defense simulation decision-support advisory ai",
    project_urls={
        "Documentation": "https://github.com/yourusername/abhedya",
        "Source": "https://github.com/yourusername/abhedya",
    },
)

