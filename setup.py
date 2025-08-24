#!/usr/bin/env python
"""Setup for AI Entity Renamer integration."""
from setuptools import find_packages, setup

setup(
    name="ai_entity_renamer",
    version="1.0.0",
    description="AI Entity Renamer integration for Home Assistant",
    author="gatesry",
    author_email="example@example.com",
    url="https://github.com/gatesry/AI-entity-renamer",
    packages=find_packages(),
    install_requires=["openai>=1.0.0"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Home Assistant",
    ],
    keywords=["home assistant", "homeassistant", "hass", "automation", "ai", "entity", "rename"],
    license="MIT",
    include_package_data=True,
    zip_safe=False,
)
