# VxFormsApi
## How to upload
First you need to change the version and create the distributions in the terminal:

```
python .\setup.py sdist
python .\setup.py bdist_wheel --universal
```
### Test PyPI
This process will require the API Token associated with the account.
```
twine upload --repository-url https://test.pypi.org/legacy/ .\dist\*
```

### PyPI
This process will require the API Token associated with the account.
```
twine upload dist/*
```