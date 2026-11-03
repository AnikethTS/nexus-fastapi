from setuptools import setup, find_packages

setup(
    name="nexus-fastapi",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "sqlalchemy>=2.0.23",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "python-multipart>=0.0.6",
        "python-dotenv>=1.0.0",
        "email-validator>=2.1.0",
        "passlib>=1.7.4",
        "python-jose[cryptography]>=3.3.0",
        "bcrypt>=4.0.1",
        "alembic>=1.12.1",
        "pytest>=7.4.3",
        "httpx>=0.25.1",
        "black>=23.11.0",
        "isort>=5.12.0",
        "flake8>=6.1.0"
    ],
    entry_points={
        "console_scripts": [
            "nexus-fastapi=nexus_fastapi.cli:main",
        ],
    },
    python_requires=">=3.8",
    author="Meetkumar velani, Axay Patoliya",
    author_email="meetvelani2728@gmail.com, axaypatoliya2222@gmail.com",
    description="A FastAPI project generator and framework",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/meetvelani/nexus-fastapi",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: FastAPI",
        "Development Status :: 3 - Alpha"
    ],
) 