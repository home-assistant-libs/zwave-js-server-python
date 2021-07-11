"""Setup module for zwave-js-server-python."""
from pathlib import Path

from setuptools import find_packages, setup

PROJECT_DIR = Path(__file__).parent.resolve()
README_FILE = PROJECT_DIR / "README.md"
VERSION = "0.27.1"


setup(
    name="zwave-js-server-python",
    version=VERSION,
    url="https://github.com/home-assistant-libs/zwave-js-server-python",
    download_url="https://github.com/home-assistant-libs/zwave-js-server-python",
    author="Home Assistant Team",
    author_email="hello@home-assistant.io",
    description="Python wrapper for zwave-js-server",
    long_description=README_FILE.read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["test.*", "test"]),
    python_requires=">=3.8",
    install_requires=["aiohttp>3"],
    entry_points={
        "console_scripts": ["zwave-js-server-python = zwave_js_server.__main__:main"]
    },
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Home Automation",
    ],
)
