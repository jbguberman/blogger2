# blogger_scraper

## What it does

This scraper was constructed to enable researchers to collect Blogger and Blogspot content for the purpose of analysis. In its current incarnation, this scraper is capable of collecting 500 most recent posts from a blog and up to 500 of the most recent comments from each of these posts. Please note that this code is written in Python 3.5 and has only been tested in OS X version 10.11.5 (El Capitan).

## What you'll need

You're going to need a few tools if in order to use this scraper.

### Python

First and foremost, you'll need [Python](https://www.python.org/). If you're on a Mac, you already have Python, but you'll need to get and install version 3.5. If you don't already have this version of Python, I recommend that you install it using [Anaconda](https://www.continuum.io/downloads). Installing Anaconda will install the most recent version of Python and will allow you to, using the included `environment.yml`, recreate the virtual environment in which this code was developed and tested. [Here's a helpful blogpost that will teach you a bit about using Anaconda](http://www.casmlab.org/code/package-management/).

### API Key

In addition to Python, you'll need an [API key](https://en.wikipedia.org/wiki/Application_programming_interface_key) from Google. You can get your key by following these steps:

1. Sign in to the  [Google developer console](https://console.developers.google.com/) using a google account (if you have gmail, that username/password will work).

2. Find and click "credentials" in the left sidebar, and then click "create project."

3. Give your project a name (it can be anything), decide whether you want to receive emails, agree to the terms of service, and then click "create".

4. Give google a few moments, and then click "create credentials." This will open a dropdown menu. Within this menu, click "API key." This will bring up a new window. Click "Server key."

5. Name your key (anything will work) and enter the IP addresses you expect to be using this scraper from. If you need to get your IP address, [click here](https://www.google.com/#q=my+ip). Then, click "create."

Now you have your API key. Make sure to keep track of this for later.

## How to use the scraper

### Setup

First, open `settings.cfg` in a text editor.  Fill in information for each value.  You'll need to get an API Key from Google (instructions on how to do this will be added here later).  For `max_posts` and `max_comments`, enter an integer no larger than 500.

Use the included `environment.yml` file to create an anaconda environment.

### Collect, parse, and format the data

Run each of the three scripts in the following order:

1. blogger_collect.py (retrieves data based on parameters specified in `settings.cfg`

2. blogger_parse.py (gets the data you probably want out of the raw data dump)

3. blogger_toCSV.py (exports the parsed data to a human-readable spreadsheet)
