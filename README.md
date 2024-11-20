# SentimentProject
Sentiment analysing web application project.

# Download the repository
Clone the repository:
```sh
git clone https://github.com/Macsok/Sentiment-Analysis-Application
cd Exploratory-Data-Analysis
```

# Prerequsites
`Flask`
`...`

# Running
```sh
python web/main.py
```

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
pip install -r dependencies/requirements.txt
```
Once you have finished working on your project, it’s a good habit to deactivate its venv. By deactivating, you leave the virtual environment.
```sh
deactivate
```
Delete the Virtual Environment (if your virtual environment is in a directory called 'venv':):
```sh
rm -r myvenv
```

You can learn more about virtual environments at: https://python.land/virtual-environments/virtualenv

to be completed...
