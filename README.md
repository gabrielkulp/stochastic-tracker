# Stochastic Tracker

General application for stochastic tracking of time usage, mood, location, or anything

## Installation

For the simplest method, just do this:

```bash
pip install flask
flask init-db
```

For an isolated installation, the process is a bit more involved:

```bash
# First install the virtual package environment manager
pip install virtualenv

# Next create a new virtual environment
virtualenv venv

# Activate the virtual environment in bash.
# There are other scripts for other shells, like activate.fish and .ps1
source venv/bin/activate

# Once inside venv, pip will install packages isolated from your system
pip install flask

# Then setup your local state
flask init-db

# When you're done with flask, exit the virtual environment
deactivate
```

### In Docker

Build the image with a command similar to this:

```sh
docker build --tag stochastic-tracker .
```

Run the image with a command similar to this:

```sh
docker run --rm --name tracker -p 80:8080 stochastic-tracker
```

You'll probably want to change at least the run command for production use (for example, to add database persistence). The database is located at `/app/instance/samples.sqlite`. You should probably also set the environment variables `AUTH_USERNAME` and `AUTH_PASSWORD`.

## Usage

If you're using `virtualenv`, then first run `source venv/bin/activate`. Run `deactivate` or exit the shell to leave the virtual environment.

Execute `flask run`, then visit http://127.0.0.1:5000 in your browser.
