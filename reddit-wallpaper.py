from __future__ import unicode_literals
import ctypes
import os
import praw
import platform
import re
import requests
import sys
import random
import time
import wx
from io import StringIO
from collections import defaultdict

if sys.version_info <= (2, 6):
    import commands as subprocess
else:
    import subprocess

default_settings = dict(
	#interval = 24,
	minVote = 0,
	subreddit = 'wallpapers',
	search = '',
	past = 'day',
	allowNSFW = False,
	select = 'top'
)

settings = default_settings


class MyFrame(wx.Frame):

    def __init__(self, parent):

        select = ['random', 'top']
        pasts = ['hour', 'day', 'week', 'month', 'year', 'all']
        suggested_subreddits = ['wallpapers', 'wallpaper', 'EarthPorn', 'BackgroundArt', 'TripleScreenPlus', 'quotepaper', 'BigWallpapers', 'MultiWall', 'DesktopLego', 'VideoGameWallpapers']


        wx.Frame.__init__(self, parent, -1, "ThumbnailCtrl Demo")

        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        vbox.Add(((-1, 10)))

        selectBox = wx.BoxSizer(wx.HORIZONTAL)
        selectBox.Add((10, -1))
        selectBox.Add(wx.StaticText(self, label='Select '))
        self.selectCombo = wx.ComboBox(self, value=settings['select'], choices=select, style=wx.CB_READONLY)
        self.selectCombo.Bind(wx.EVT_TEXT, self.SetSelectCombo)
        self.selectCombo.Bind(wx.EVT_COMBOBOX, self.SetSelectCombo)
        selectBox.Add(self.selectCombo)
        selectBox.Add(wx.StaticText(self, label=' wallpapers...'))
        vbox.Add(selectBox)

        vbox.Add((-1, 15))

        subredditBox = wx.BoxSizer(wx.HORIZONTAL)
        subredditBox.Add((25, -1))
        subredditBox.Add(wx.StaticText(self, label='from the '))
        self.subredditCombo = wx.ComboBox(self, value=settings['subreddit'], choices=suggested_subreddits)
        self.subredditCombo.Bind(wx.EVT_TEXT, self.SetSubredditCombo)
        self.subredditCombo.Bind(wx.EVT_COMBOBOX, self.SetSubredditCombo)
        subredditBox.Add(self.subredditCombo)
        subredditBox.Add(wx.StaticText(self, label=' subreddit'))
        vbox.Add(subredditBox)
        vbox.Add((-1, 15))

        #searchBox = wx.BoxSizer(wx.HORIZONTAL)
        #searchBox.Add((25, -1))
        #searchBox.Add(wx.StaticText(self, label='containing search terms '))
        #self.searchText = wx.TextCtrl(self, value=settings['search'])
        #self.searchText.Bind(wx.EVT_TEXT, self.SetSearchText)
        #searchBox.Add(self.searchText)
        #vbox.Add(searchBox)
        #vbox.Add((-1, 15))

        #minVoteBox = wx.BoxSizer(wx.HORIZONTAL)
        #minVoteBox.Add((25, -1))
        #minVoteBox.Add(wx.StaticText(self, label='with at least '))
        #self.minVoteSpin = wx.SpinCtrl(self, value=str(settings['minVote']), min=0, max=10000)
        #self.minVoteSpin.Bind(wx.EVT_SPINCTRL, self.SetMinVoteSpin)
        #minVoteBox.Add(self.minVoteSpin)
        #minVoteBox.Add(wx.StaticText(self, label=' upvotes'))
        #vbox.Add(minVoteBox)
        #vbox.Add((-1, 15))

        fromBox = wx.BoxSizer(wx.HORIZONTAL)
        fromBox.Add((25, -1))
        fromBox.Add(wx.StaticText(self, label='from the past '))
        self.pastCombo = wx.ComboBox(self, choices=pasts, value=settings['past'], style=wx.CB_READONLY)
        self.pastCombo.Bind(wx.EVT_TEXT, self.SetPastCombo)
        self.pastCombo.Bind(wx.EVT_COMBOBOX, self.SetPastCombo)
        fromBox.Add(self.pastCombo)
        vbox.Add(fromBox)
        vbox.Add((-1, 15))

        #intervalBox = wx.BoxSizer(wx.HORIZONTAL)
        #intervalBox.Add(wx.StaticText(self, label='and update the wallpaper every '))
        #self.intervalSpin = wx.SpinCtrl(self, value=str(settings['interval']), min=1)
        #self.intervalSpin.Bind(wx.EVT_SPINCTRL, self.SetIntervalSpin)
        #intervalBox.Add(self.intervalSpin)
        #intervalBox.Add(wx.StaticText(self, label=' hours.'))
        #vbox.Add(intervalBox)
        #vbox.Add((-1, 15))

        nsfwBox = wx.BoxSizer(wx.HORIZONTAL)
        nsfwBox.Add((25, -1))
        self.nsfwCheck = wx.CheckBox(self, label='Allowing NSFW wallpapers?')
        self.nsfwCheck.SetValue(settings['allowNSFW'])
        self.nsfwCheck.Bind(wx.EVT_CHECKBOX, self.SetNSFWCheck)
        nsfwBox.Add(self.nsfwCheck)
        vbox.Add(nsfwBox)
        vbox.Add((-1, 15))

        vbox.Add((-1, 10))
        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND)
        vbox.Add((-1, 10))

        setw = wx.Button(self, 0, "Go!")
        setw.Bind(wx.EVT_BUTTON, self.OnGet)


        aboutBox = wx.BoxSizer(wx.HORIZONTAL)
        aboutBox.Add((150, -1))
        aboutBox.Add(setw, 0, wx.CENTER | wx.ALL,10)
        vbox.Add(aboutBox)

        self.SetSizer(vbox)


    def SetIntervalSpin(self, evt):
        settings['interval'] = self.intervalSpin.GetValue()
        self.OnUpdateInterval()

    def SetNSFWCheck(self, evt):
        settings['allowNSFW'] = self.nsfwCheck.IsChecked()
        self.OnFilterUpdate()

    def SetPastCombo(self, evt):
        settings['past'] = self.pastCombo.GetValue()
        self.OnFilterUpdate()

    def SetMinVoteSpin(self, evt):
        settings['minVote'] = self.minVoteSpin.GetValue()
        self.OnFilterUpdate()

    def SetSearchText(self, evt):
        settings['search'] = self.searchText.GetValue()
        self.OnFilterUpdate()

    def SetSubredditCombo(self, evt):
        settings['subreddit'] = self.subredditCombo.GetValue()
        self.OnFilterUpdate()

    def SetSelectCombo(self, evt):
        settings['select'] = self.selectCombo.GetValue()
        self.OnFilterUpdate()

    def OnClose(self, evt):
        self.SaveSettings()
        self.Destroy()

    def OnGet(self, evt):
        GetWal()

def get_top_image(sub_reddit):
    """Get image link of most upvoted wallpaper of the day
    :sub_reddit: name of the sub reddit
    :return: the image link
    """
    nsfw = settings['allowNSFW']
    submissions = sub_reddit.top(settings['past'], limit=10,)
    for submission in submissions:
        ret = {"id": submission.id}
        if not nsfw and submission.over_18:
            continue
        url = submission.url
        # Strip trailing arguments (after a '?')
        url = re.sub(R"\?.*", "", url)
        ret['type'] = url.split(".")[-1]
        if url.endswith(".jpg") or url.endswith(".png"):
            ret["url"] = url
        # Imgur support
        if ("imgur.com" in url) and ("/a/" not in url) and ("/gallery/" not in url):
            if url.endswith("/new"):
                url = url.rsplit("/", 1)[0]
            id = url.rsplit("/", 1)[1].rsplit(".", 1)[0]
            ret["url"] = "http://i.imgur.com/{id}.jpg".format(id=id)
        print("id : "),
        print(ret['id'])
        return ret

def get_random_image(sub):
    nsfw = settings['allowNSFW']
    random_post_number = random.randint(0,19)

    posts = [post for post in sub.hot(limit=20)]
    submission = posts[random_post_number]

    #if not args.nsfw and submission.over_18:
       # continue
    
    ret = {"id": submission.id}
        
    url = submission.url
    # Strip trailing arguments (after a '?')
    url = re.sub(R"\?.*", "", url)
    ret['type'] = url.split(".")[-1]
    if url.endswith(".jpg") or url.endswith(".png"):
        ret["url"] = url
    # Imgur support
    if ("imgur.com" in url) and ("/a/" not in url) and ("/gallery/" not in url):
        if url.endswith("/new"):
            url = url.rsplit("/", 1)[0]
        id = url.rsplit("/", 1)[1].rsplit(".", 1)[0]
        ret["url"] = "http://i.imgur.com/{id}.jpg".format(id=id)
    return ret

def detect_desktop_environment():
    """Get current Desktop Environment
       http://stackoverflow.com
       /questions/2035657/what-is-my-current-desktop-environment
    :return: environment
    """
    environment = {}
    if os.environ.get("KDE_FULL_SESSION") == "true":
        environment["name"] = "kde"
        environment["command"] = """
                    qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript '
                        var allDesktops = desktops();
                        print (allDesktops);
                        for (i=0;i<allDesktops.length;i++) {{
                            d = allDesktops[i];
                            d.wallpaperPlugin = "org.kde.image";
                            d.currentConfigGroup = Array("Wallpaper",
                                                   "org.kde.image",
                                                   "General");
                            d.writeConfig("Image", "file:///{save_location}")
                        }}
                    '
                """
    elif os.environ.get("GNOME_DESKTOP_SESSION_ID"):
        environment["name"] = "gnome"
        environment["command"] = "gsettings set org.gnome.desktop.background picture-uri file://{save_location}"
    elif os.environ.get("DESKTOP_SESSION") == "Lubuntu":
        environment["name"] = "lubuntu"
        environment["command"] = "pcmanfm -w {save_location} --wallpaper-mode=fit"
    elif os.environ.get("DESKTOP_SESSION") == "mate":
        environment["name"] = "mate"
        environment["command"] = "gsettings set org.mate.background picture-filename {save_location}"
    else:
        try:
            info = subprocess.getoutput("xprop -root _DT_SAVE_MODE")
            if ' = "xfce4"' in info:
                environment["name"] = "xfce"
        except (OSError, RuntimeError):
            environment = None
            pass
    return environment

def set_wallpaper(save_location):
    supported_linux_desktop_envs = ["gnome", "mate", "kde", "lubuntu"]

    # Check OS and environments
    platform_name = platform.system()
    if platform_name.startswith("Lin"):

        # Check desktop environments for linux
        desktop_environment = detect_desktop_environment()
        if desktop_environment and desktop_environment["name"] in supported_linux_desktop_envs:
            os.system(desktop_environment["command"].format(save_location=save_location))
        else:
            print("Unsupported desktop environment")
            print("Trying feh")
            os.system("feh --bg-fill {save_location}".format(save_location=save_location))
            print("[SUCCESS] done!!")

    # Windows
    if platform_name.startswith("Win"):
        # Python 3.x
        if sys.version_info >= (3, 0):
            ctypes.windll.user32.SystemParametersInfoW(20, 0, save_location, 3)
        # Python 2.x
        else:
            ctypes.windll.user32.SystemParametersInfoA(20, 0, save_location, 3)

    # OS X/macOS
    if platform_name.startswith("Darwin"):
        if args.display == 0:
            command = """
                    osascript -e 'tell application "System Events"
                        set desktopCount to count of desktops
                        repeat with desktopNumber from 1 to desktopCount
                            tell desktop desktopNumber
                                set picture to "{save_location}"
                            end tell
                        end repeat
                    end tell'
                    """.format(save_location=save_location)
        else:
            command = """osascript -e 'tell application "System Events"
                            set desktopCount to count of desktops
                            tell desktop {display}
                                set picture to "{save_location}"
                            end tell
                        end tell'""".format(display=args.display,
                                            save_location=save_location)
        os.system(command)

def GetWal():
    subreddit = settings['subreddit']
    if settings['select'] == 'top':
        random = False
    else:
        random = True

    save_dir = "Pictures/reddit"

    r = praw.Reddit(user_agent='linux:wallies-from-reddit:v0.1 by u/prmsrswt')
    print('[I] Connected to Reddit')
    print('[I] fetching submissions')
    if random:
        print("[I] Aquiring random image.")
        image = get_random_image(r.subreddit(subreddit))
    else:
        # Get top image link
        print("[I] Aquiring top image.")
        image = get_top_image(r.subreddit(subreddit))
    if "url" not in image:
        print("Error: No suitable images were found, please retry")


    # Get home directory and location where image will be saved
    # (default location for Ubuntu is used)
    home_dir = os.path.expanduser("~")
    save_location = "{home_dir}/{save_dir}/{subreddit}-{id}.{image_type}".format(home_dir=home_dir, save_dir=save_dir,
                                                                        subreddit=subreddit,
                                                                        id=image["id"],
                                                                        image_type=image['type'])
    if not os.path.isfile(save_location):
        print('[I] Downloading Image....')
        # Request image
        response = requests.get(image['url'], allow_redirects=False)


        # If image is available, proceed to save
        if response.status_code == requests.codes.ok:
        
        
            # Create folders if they don't exist
            dir = os.path.dirname(save_location)
            if not os.path.exists(dir):
                os.makedirs(dir)

            # Write to disk
            with open(save_location, "wb") as fo:
                for chunk in response.iter_content(4096):
                    fo.write(chunk)
            
            # Setting the wallpaper
            set_wallpaper(save_location)

        else:
            sys.exit("Error: Image url is not available, the program is now exiting.")
    else:
        print('[I] Image Found on disk. Skipping Downloading.')
        set_wallpaper(save_location)


# our normal wxApp-derived class, as usual

app = wx.App(0)

frame = MyFrame(None)
app.SetTopWindow(frame)
frame.Show()

app.MainLoop()