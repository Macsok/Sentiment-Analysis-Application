# Sentiment analysing web application project.
description...

# Download the repository
Clone the repository:
```sh
git clone https://github.com/Macsok/Sentiment-Analysis-Application
cd Sentiment-Analysis-Application
```

# Prerequsites
`Python=>3.10.0`


# Used libraries (details in requirements.txt file)
`googletrans` `google-api-python-client` `playwright` `nltk` `asyncio` `flask` `typing` `simplejson` `pandas`


# Using Virtualenv (on Windows)
Use virtualenv to isolate project dependencies, ensuring no conflicts between different projects.
First, install Virtualenv if you haven't already:
```sh
pip install virtualenv
```
Navigate to main project directory and create a new virtual environment:
```sh
python -m virtualenv myvenv
```
Activate the Virtual Environment:
```sh
python -m source myenv/Scripts/activate
```
When activated, your shell will show the virtual environment’s name in the prompt.

Now that the environment is active, you can install packages:
```sh
pip install -r requirements.txt
```
Once you have finished working on your project, it’s a good habit to deactivate its venv. By deactivating, you leave the virtual environment.
```sh
deactivate
```
Delete the Virtual Environment (if your virtual environment is in a directory called 'venv':):
```sh
rm -r myvenv
```
> [!NOTE]
> You can learn more about virtual environments at: https://python.land/virtual-environments/virtualenv


# Browser installing
```sh
python -m playwright install firefox
```
> [!TIP]
> Alternatively you can try: npx playwright install firefox


# Adding credentials
To use online scrapers you need to provide credentials to your platforms. Create new directory in main project folder (Sentiment-Analysis-Application) called 'credentials'. Then add 3 files to it: AMAZON, X, YT_API_KEY. Each file should consist of:
### AMAZON
- email
- password
### X
- username
- password
- email
### YT_API_KEY
- API key (more at: https://developers.google.com/youtube/v3)


> [!TIP]
> You can still use 'live review' without providing any credentials to your platforms.


# Running
```sh
python run.py
```