from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dtrade-api-client",  # 修改包名以避免冲突
    version="0.1.0",
    author="DTrader Team",
    author_email="support@dtrade.com",
    description="A Python client for DTrader API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dtrade-python", # 替换为实际仓库地址
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
)
