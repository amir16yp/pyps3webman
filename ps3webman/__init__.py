import requests
from bs4 import BeautifulSoup as bs
from enum import Enum
from os.path import basename
from os.path import join as _joinpath
from urllib.parse import urljoin
import re


def joinpath(path1, path2):
    return _joinpath(path1, path2).replace('\\', '/')

class LedColor(Enum):
    RED = 0
    GREEN = 1
    YELLOW = 2


class BuzzType(Enum):
    NO_SOUND = None
    SIMPLE = 1
    DOUBLE = 2
    TRIPLE = 3
    SND_CANCEL = 0
    SND_TROPHY = 5
    SND_DECIDE = 6
    SND_OPTION = 7
    SND_SYSTEM_OK = 8
    SND_SYSTEM_NG = 9


class NotificationIconType(Enum):
    INFO = 0
    WARN = 3
    BLOCKED = 7
    SECURITY = 34
    SETTINGS = 8
    FILES = 27
    PROFILE_ROBOT = 28
    PROFILE = 40
    GAME_DISC = 41
    DISC = 42
    DVD_DISC = 46
    BLURAY_DISC = 43
    CD_DISC = 44
    MEDIA = 45
    MUSIC = 30
    PHOTOS = 31
    VIDEOS = 32
    GAMES = 33
    MESSAGE_BOX = 36
    NEW_MESSAGE = 38
    REFRESH = 39
    REMOTE_PLAY = 48
    CLOCK = 49
    GAME_INSTALL = 50
    TROPHY_1 = 9
    TROPHY_2 = 10
    TROPHY_3 = 11
    TROPHY_4 = 12
    TROPHY_PLATINUM = 12
    PSN_FRIEND = 1
    PSN_YELLOW = 19
    PSN_BLUE = 20
    SIGN_QUESTION_MARK = 47
    SIGN_X = 35
    SIGN_BLOCKED = 35
    SIGN_NEW = 21
    SIGN_CHECKMARK = 22
    SIGN_WARNING = 23
    SIGN_SETTINGS = 24
    SIGN_TROPHY = 25
    SIGN_STORE = 26
    SIGN_LOADING = 29
    CURSOR_PALM = 13
    CURSOR_DRAG = 16
    CURSOR = 15
    CURSOR_PEN = 14
    PLAY = 17
    PAUSE = 18
    HEADPHONES = 2
    KEYBOARD = 4


class PS3Directory:
    def __init__(self, webman, name, path, space, date, html=None):
        self.webman = webman
        self.name = name
        self.path = path
        self.space = space
        self.date = date
        self.html = html

    def __repr__(self):
        return f"PS3Directory(name={self.name}, path={self.path}, space={self.space}, date={self.date})"

    def _get_html(self):
        r = self.webman.SESSION.get(f'{self.webman.url}{self.path}')
        return r.content.decode()

    def _fetch_and_parse_html(self):
        if not self.html:
            self.html = self._get_html()
        return PS3Directory._parse_directory_html(self.webman, self.html, self.path)

    def get_listing(self):
        directories, files = self._fetch_and_parse_html()
        return directories + files

    def get_files(self):
        _, files = self._fetch_and_parse_html()
        return files

    def get_file(self, filename):
        for file in self.get_files():
            if file.name == filename:
                return file
        return None

    def get_directory(self, dirname):
        for directory in self.get_directories():
            if directory.name == dirname:
                return directory
        return None

    def get_directories(self):
        directories, _ = self._fetch_and_parse_html()
        return directories

    @staticmethod
    def _parse_directory_html(webman, html_content, _dir_path):
        soup = bs(html_content, 'html.parser')

        # Try to extract free space information from outside the table, if available
        external_space_info = {}
        for tag in soup.find_all('b'):
            link = tag.find('a')
            if link:
                directory_path = link.get('href')
                space_parts = tag.text.split(': ')
                if len(space_parts) > 1:
                    space_text = space_parts[1].split(' free')[0]
                    external_space_info[directory_path] = space_text

        # Find the directory table in the HTML content
        directory_table = soup.find("table", {"id": "files"})
        rows = directory_table.find_all("tr")[1:]

        directories = []
        files = []

        for row in rows:
            columns = row.find_all("td")

            # Extract name, path, and date
            item_name = columns[0].a.text if columns[0].a else None
            item_path = columns[0].a['href'] if columns[0].a else None
            item_date = columns[2].text.strip()

            # Distinguish between directories and files
            if "<dir>" in columns[1].text or columns[1].find('div'):
                item_space = None
                div_element = columns[1].find('div')
                if div_element and div_element.a:
                    title_info = div_element.a.get('title')
                    if title_info:
                        # Extract free space and total space from the title
                        free_space, total_space = title_info.split(' / ')
                        free_space = free_space.split(' ')[0].strip()
                        total_space = total_space.split(' ')[0].strip()
                        item_space = f"Free: {free_space} / Total: {total_space}"
                elif item_path in external_space_info:
                    # Extract space from the external tags if not found in the table
                    item_space = f"Free: {external_space_info[item_path]}"
                directories.append(PS3Directory(webman, item_name, joinpath(
                    _dir_path, item_path), item_space, item_date))
            else:
                # It's a file
                item_size = columns[1].text.strip().split(
                    ' ')[0]  # Extract the size of the file
                files.append(PS3File(webman, item_name, joinpath(
                    _dir_path, item_path), item_date))

        return directories, files


class PS3File:
    def __init__(self, webman, name, path, date):
        self.webman = webman
        self.name = name
        self.path = path
        self.date = date
        self.html = None

    def get_url(self):
        return urljoin(self.webman.url, self.path)

    def fetch_html(self):
        # Fetch and store HTML content
        md5info_url = self.webman.url + '/md5.ps3' + self.path
        r = self.webman.SESSION.get(md5info_url)
        self.html = r.content.decode()

    def get_md5(self):
        if self.html is None:
            self.fetch_html()

        # Parse the HTML using BeautifulSoup
        soup = bs(self.html, 'html.parser')

        # Initialize variable for MD5 value
        md5_value = None

        # Iterate over every <p> tag and check for the MD5 value
        for p_tag in soup.find_all('p'):
            text = p_tag.text.strip()
            if text.startswith('MD5:'):
                md5_value = text[len('MD5:'):].strip()

        return md5_value


    def get_size(self):
        if self.html is None:
            self.fetch_html()

        # Parse the HTML using BeautifulSoup
        soup = bs(self.html, 'html.parser')

        # Initialize variable for size
        file_size = None

        # Iterate over every <p> tag and check for the size
        for p_tag in soup.find_all('p'):
            text = p_tag.text.strip()
            if text.startswith('Size:'):
                file_size = text[len('Size:'):].strip()

        return file_size

    def __repr__(self):
        return f"PS3File(name={self.name}, path={self.path}, size={self.get_size()}, date={self.date})"


class PS3Game:
    def __init__(self, webman, title, directory_path, icon):
        self.webman = webman
        self.title = title
        self.directory_path = directory_path
        self.icon = icon

    def get_directory(self):
        return self.webman.get_directory(self.directory_path)

    def mount(self):
        mount_path = self.webman.url + '/mount.ps3/' + self.directory_path
        self.webman.SESSION.get(mount_path)
        
class WebMan:
    def __init__(self, ip, port=80):
        self.SESSION = requests.Session()
        self.ip = ip
        self.port = port
        self.url = f'http://{ip}:{port}'
        self.dhtml = None  # Initialize dhtml as None


    def refresh_data(self, path='/cpursx.ps3?/sman.ps3'):
        r = self.SESSION.get(f'{self.url}{path}')
        self.dhtml = r.content.decode()  # Save the HTML response in dhtml



    def get_temps(self  ):
        r = self.SESSION.get(f'{self.url}/cpursx_ps3')

        if r.status_code != 200:
            print(f"Failed to retrieve data. Status code: {r.status_code}")
            return None, None

        soup = bs(r.content, 'html.parser')
        temp_info = soup.find('a', href='/cpursx.ps3')

        if not temp_info:
            print("Failed to find temperature information in the HTML.")
            return None, None

        temp_text = temp_info.text
        temp_values = [int(val) for val in re.findall(r'\d+', temp_text)]

        if len(temp_values) != 2:
            print("Failed to parse temperatures.")
            return None, None

        cpu_temp, rsx_temp = temp_values
        return cpu_temp, rsx_temp


    def get_fan_speed(self, refresh=True):
        if refresh:
            self.refresh_data('/cpursx.ps3?/sman.ps3')  # Call refresh_data to update the HTML
        soup = bs(self.dhtml, 'html.parser')
        
        # Find the fan speed information within the anchor tag
        fan_speed_info = soup.find('a', href='/cpursx.ps3?mode').text
        
        # Extract the fan speed value
        fan_speed = int(fan_speed_info.split(':')[1].strip().split('%')[0])
        
        return fan_speed

    def get_hdd_space(self, refresh=True):
        if refresh:
            self.refresh_data('/cpursx.ps3?/sman.ps3')  # Call refresh_data to update the HTML
        soup = bs(self.dhtml, 'html.parser')
        
        # Find the hard disk space information within the anchor tag
        hdd_info = soup.find('a', href='/dev_hdd0').text
        
        # Extract the free hard disk space value
        hdd_space_str = hdd_info.split('HDD:')[1].strip()
        hdd_space = float(hdd_space_str.split('GB')[0].strip())
        
        return hdd_space

    def buzz(self, buzzType: BuzzType):
        if buzzType.value is not None:
            r = self.SESSION.get(
                self.url + f'/buzzer.ps3mapi?snd={buzzType.value}')

    def notify(self, msg: str, iconType=NotificationIconType.INFO, buzzType=None):
        params = {'msg': msg, 'icon': iconType.value}
        if buzzType is not None:
            params['snd'] = buzzType.value
        self.SESSION.get(self.url + '/notify.ps3mapi', params=params)

    def get_directory(self, path='/'):
        if not path.startswith('/'):
            path = '/' + path
        r = self.SESSION.get(f'{self.url}{path}')
        html = r.content.decode()
        return PS3Directory(webman=self, name=basename(path), path=path, space=None, date=None, html=html)

    def get_games_list(self):
        r = self.SESSION.get(f'{self.url}/sman.ps3?')
        html = r.content.decode()
        
        soup = bs(html, 'html.parser')
        games = []

        # Find game entries within the HTML
        game_entries = soup.find_all('div', class_='gn')
        
        for entry in game_entries:
            # Extract game title and link
            game_link = entry.find('a', href=True)
            game_title = game_link.get_text(strip=True)
            game_directory = game_link['href']

            # Check if the game URL links to a directory (excluding /mount)
            if game_directory.startswith('/') and not game_directory.startswith('/mount'):
                # Extract game icon image URL
                game_icon_img = entry.find_previous('div', class_='ic').find('img', class_='gi')
                game_icon_url = game_icon_img['src'] if game_icon_img else None
                
                # Create a PS3Game object and append it to the list
                game = PS3Game(webman=self, title=game_title, directory_path=game_directory, icon=PS3File(self, name=basename(game_icon_url), path=game_icon_url, date=None))
                games.append(game)
        
        return games
