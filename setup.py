"""
Self_Optimizing_Holo_Half - AI Agent Self-Evolution Platform

A self-evolving platform that integrates OpenHands and OpenSpace
with scientific A/B testing and automated decision making.
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取 README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# 读取 requirements
requirements = []
req_file = this_directory / "requirements.txt"
if req_file.exists():
    with open(req_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('-'):
                # 跳过注释行和可选依赖
                if 'openhands' not in line.lower() and 'openspace' not in line.lower():
                    requirements.append(line)

setup(
    name="self-optimizing-holo-half",
    version="0.1.0",
    author="firefox-669",
    author_email="your-email@example.com",
    description="A self-evolving platform for OpenHands & OpenSpace with A/B testing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/firefox-669/Self_Optimizing_Holo_Half",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "openhands": ["openhands>=0.1.0"],
        "openspace": ["openspace @ git+https://github.com/HKUDS/OpenSpace.git"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sohh=main:main",
            "self-optimizing-holo-half=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.yaml", "*.yml", ".env.example"],
    },
    keywords="ai-agent self-evolution openhands openspace ab-testing",
    project_urls={
        "Bug Reports": "https://github.com/firefox-669/Self_Optimizing_Holo_Half/issues",
        "Source": "https://github.com/firefox-669/Self_Optimizing_Holo_Half",
        "Documentation": "https://github.com/firefox-669/Self_Optimizing_Holo_Half#readme",
    },
)
