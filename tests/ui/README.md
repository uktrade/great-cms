# Setup
``` bash
# Set these values in your ~/.zprofile (zsh) or ~/.profile (bash)
export BROWSERSTACK_USERNAME="VALUE"
export BROWSERSTACK_ACCESS_KEY="VALUE"

python -m venv .venv
pip-compile --upgrade -r --annotate requirements.in
pip install -q -r requirements.txt
```

# Local
Set different variables in config.json  
Or pass them in on the command line
```
pytest tests --baseurl=URL --browser=BROWSER --headless=BOOLEAN
```

Run tests locally
``` bash
pytest tests  
pytest tests/specific_test.py
pytest tests/specific_test.py::test_name
```
To run in parallel
```
python -m pytest -s -v -n=NUM-OF-PARALLELS
```
Flags for summary report in terminal `https://docs.pytest.org/en/6.2.x/usage.html#detailed-summary-report`

# Browserstack
==NOTE==  
browserstack-sdk requires pytest-selenium which requires pytest <7 and >6, however, version <7 breaks current unit tests  
This is currently tracked https://github.com/pytest-dev/pytest-selenium/issues/305

With browserstack.yml setup with crednetials in it  
Run all tests, a specific class, a specific test  
```
browserstack-sdk pytest
browserstack-sdk pytest tests/specific_test.py
browserstack-sdk pytest tests/specific_test.py::test_name
```
Run from the command line without credentials in the yml  
```
BROWSERSTACK_USERNAME="VALUE" BROWSERSTACK_ACCESS_KEY="VALUE" browserstack-sdk pytest tests/international/international_contact_test.py::test_contact_invest_success
```  
Config is taken from browserstack.yml at the root of the project. This can be manually updated or use browserstack's configurator https://www.browserstack.com/docs/automate/selenium/sdk-config-generator
