# Publishing Nexus-FastAPI to PyPI

This guide will walk you through the process of publishing the Nexus-FastAPI package to the Python Package Index (PyPI).

## Prerequisites

1. A PyPI account (create one at https://pypi.org/account/register/)
2. Python 3.9 or higher
3. pip, setuptools, and wheel installed
4. A clean virtual environment

## Project Structure

```
nexus-fastapi/
├── src/
│   └── nexus_fastapi/
│       ├── __init__.py
│       ├── cli.py
│       ├── scaffolds.py
│       └── hooks.py
├── tests/
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

## Publishing Steps

1. **Prepare Your Environment**

   ```bash
   # Create and activate a virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install build dependencies
   pip install --upgrade pip setuptools wheel
   pip install build twine
   ```

2. **Update Version**

   - Update the version number in `pyproject.toml`
   - Follow semantic versioning (MAJOR.MINOR.PATCH)

3. **Build Distribution**

   ```bash
   # Clean any existing builds
   rm -rf dist/ build/ *.egg-info/

   # Build the package
   python -m build
   ```

4. **Test Your Distribution**

   ```bash
   # Install the package locally
   pip install dist/nexus_fastapi-*.whl

   # Test the installation
   nexus-fastapi --help
   ```

5. **Upload to TestPyPI (Optional but Recommended)**

   ```bash
   # Upload to TestPyPI first
   python -m twine upload --repository testpypi dist/*
   ```

6. **Upload to PyPI**
   ```bash
   # Upload to PyPI
   python -m twine upload dist/*
   ```

## Package Usage

After publishing, users can install your package using:

```bash
pip install nexus-fastapi
```

## Maintaining Your Package

1. **Version Updates**

   - Update version in `pyproject.toml`
   - Create a new release on GitHub
   - Follow the publishing steps above

2. **Documentation**

   - Keep README.md up to date
   - Document all new features and changes
   - Update docstrings in your code

3. **Testing**
   - Run tests before each release
   - Ensure all features work as expected
   - Test installation in a clean environment

## Troubleshooting

1. **Upload Errors**

   - Ensure you're logged in to PyPI
   - Check your credentials
   - Verify package name isn't taken

2. **Installation Issues**
   - Check Python version compatibility
   - Verify all dependencies are listed
   - Test in a clean virtual environment

## Security Notes

1. Never commit sensitive information
2. Use environment variables for credentials
3. Keep dependencies updated
4. Follow security best practices

## Support

For issues and support:

1. Create an issue on GitHub
2. Check existing issues for solutions
3. Contact maintainers if needed

## License

This project is licensed under the MIT License - see the LICENSE file for details.
