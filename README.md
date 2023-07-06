# VAKGI

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5750019.svg)](https://doi.org/10.5281/zenodo.5750019)

A sample implementation of VAKG

To run, first create a credentials.py file in the root of this project with three variables:

```python
url = # url to a neo4j instance
login = # login to a neo4j instance
password = # its password
```

Then, run the main.py file and either check the app/graph/test folder for examples or go to http://localhost:8888/docs/api to check for the api usage.

## Install dependencies

```bash
pip install -r requirements.txt
```

## Install spacy model

```bash
python -m spacy download en_core_web_md
```

# CITATION

```bibtex
@software{leonardo_christino_2021_5750019,
  author       = {Leonardo Christino, Fernando Paulovich},
  title        = {vakg},
  month        = dec,
  year         = 2021,
  publisher    = {Zenodo},
  version      = {0.1},
  doi          = {10.5281/zenodo.5750019},
  url          = {https://doi.org/10.5281/zenodo.5750019}
}
```
