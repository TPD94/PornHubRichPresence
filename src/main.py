import yaml
from pypresence import Presence, ActivityType, StatusDisplayType
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests
import os
import sys
import shutil
import subprocess
import time


def find_chrome_path():
    """Return full path to Chrome executable or None if not found."""

    if sys.platform == "win32":
        possible_paths = [
            os.path.join(os.environ.get("PROGRAMFILES", ""), "Google\\Chrome\\Application\\chrome.exe"),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Google\\Chrome\\Application\\chrome.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google\\Chrome\\Application\\chrome.exe"),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path

    elif sys.platform == "darwin":  # macOS
        mac_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(mac_path):
            return mac_path

    else:  # Linux
        for name in ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"]:
            path = shutil.which(name)
            if path:
                return path

    return None

def launch_chrome_debug():
    chrome_path = find_chrome_path()

    if not chrome_path:
        sys.exit("Could not find Chrome")


    if sys.platform == "win32":
        user_data_dir = r"C:\chrome-debug"
    elif sys.platform == "darwin":
        user_data_dir = os.path.expanduser("~/chrome-debug")
    else:
        user_data_dir = os.path.expanduser("~/chrome-debug")

    os.makedirs(user_data_dir, exist_ok=True)

    command = [
        chrome_path,
        "--remote-debugging-port=6000",
        f"--user-data-dir={user_data_dir}",
        "https://pormhub.com/"
    ]

    process = subprocess.Popen(command)
    while process.poll() is None:
        video_info = get_url_and_description()
        if video_info is None:
            RPC.clear()
        else:
            RPC.update(
                state="Gooning",
                details=f"{video_info['title']}",
                large_image="phlogo",
                large_text="PornHub",
                buttons=[
                    {"label": "Watch", "url": f"{video_info['url']}"}
                ],
                activity_type=ActivityType.WATCHING,
                status_display_type=StatusDisplayType.STATE,
                name=f"{video_info['title']}"
            )
            time.sleep(15)
    sys.exit()

def get_tabs():
    tab_response = requests.get(
        url='http://localhost:6000/json/list'
    ).json()
    return tab_response

def find_pornhub_tab():
    tabs = get_tabs()
    for tab in tabs:
        parsed = urlparse(tab['url'])
        if parsed.netloc == "www.pornhub.com" and parsed.path == "/view_video.php":
            return tab['url']
        else:
            continue
    return None

def get_video_info():
    url = find_pornhub_tab()
    if url is None:
        return None
    else:
        pornhub_response = requests.get(
            url=url
        )
        return pornhub_response.text

def parse_video_info():
    video_info = get_video_info()
    if video_info is None:
        return None
    else:
        soup = BeautifulSoup(video_info, "html.parser")
        og_tags = soup.find_all("meta", property=lambda x: x and x.startswith("og:"))
        og_data = {}
        for tag in og_tags:
            property_name = tag.get("property")
            content = tag.get("content")
            if property_name and content:
                og_data[property_name] = content
        return og_data

def get_url_and_description():
    info = parse_video_info()
    if info is None:
        return None
    else:
        return {
            'title': info["og:title"],
            'url': info["og:url"]
        }

RPC = Presence(1478206867451805826)
RPC.connect()
launch_chrome_debug()
