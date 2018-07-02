## Reddit Wallpaper

### A tool to download and set wallpapers from different Subreddits of Reddit

![GIF demo](https://raw.githubusercontent.com/prmsrswt/reddit-wallpaper/master/outa.gif)
[**Youtube mirror of demo**](https://youtu.be/XNjiX8mj3uo) 

## Requirements
- python
- pip
- a reddit developer app. Go to https://www.reddit.com/pref/apps and create a new app.

## Installation
- clone this repo `git clone https://github.com/prmsrswt/reddit-wallpaper.git && cd reddit-wallpaper`
- Install the requirements `pip install -r requirements.txt`
- Create a praw.ini file in `~/.config/praw.ini`
- put your client id and client secret in it
    - The syntax would be
    ```ini
    [DEFAULT]
    client_id=<your-client-id>
    client_secret=<your-cliet-secret>
    ```
    

## Usage

Run the app using python `python reddit-wallpaper.py`
