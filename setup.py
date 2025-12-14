"""
Setup script for OBS Plugin Manager
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="obs-plugin-manager",
    version="1.0.0",
    author="OBS Plugin Manager Team",
    description="A Windows-based OBS Studio Plugin Management Solution",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/obs-plugin-manager",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.8",
    install_requires=[
        "psutil>=5.9.0",
        "requests>=2.31.0",
        "pywin32>=305; platform_system=='Windows'",
    ],
    entry_points={
        "console_scripts": [
            "obs-plugin-manager=obs_plugin_manager.gui:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
