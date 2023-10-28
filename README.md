# pyps3webman - PS3 WebMan MOD API Wrapper and scraper
Allows for one to control a PS3 remotely: Send notification, browse directories, mount games and more.
## Examples

### Initialize WebMan Connection

```python
from ps3webman import *
webman = WebMan(ip='192.168.1.100', port=80)
```

### Get CPU and RSX Temperatures

```python
cpu_temp, rsx_temp = webman.get_temps()
print(f"CPU Temperature: {cpu_temp}°C, RSX Temperature: {rsx_temp}°C")
```

### Get Fan Speed

```python
fan_speed = webman.get_fan_speed()
print(f"Current Fan Speed: {fan_speed}%")
```

### Get HDD Space

```python
hdd_space = webman.get_hdd_space()
print(f"Free HDD Space: {hdd_space} GB")
```

### Send Notification

```python
webman.notify(msg="Hello from Python!", iconType=NotificationIconType.INFO, buzzType=BuzzType.SIMPLE) # buzzType is optional
```

### Make the Console Beep

```python
webman.buzz(BuzzType.SIMPLE)
```

### Get Directory Listing

```python
directory = webman.get_directory(path='/dev_hdd0/')
print("Directory Listing for /dev_hdd0/:")
# files = directory.get_files()
# directories = directory.get_directories()
# both files and directories = directory.get_listing()
for file_or_directory in directory.get_listing():
  print((file_or_directory.name, file_or_directory.path))
```

### Find a specific file

```python3
directory = webman.get_directory(path='/dev_hdd0')
file = directory.get_file('HENplugin.sprx') # returns None if it doesnt exist
if file:
  print('HENplugin.sprx exists, HEN probably installed')
  print(f'File path: {file.path}, size in bytes {file.get_size()}, MD5 {file.get_md5()}, download URL {file.get_url}')
```
### Get List of Games

```python
games = webman.get_games_list()
print("List of Games:")
for game in games:
    print(game.title, game.directory_path)
```

### Get a Game Cover
```python
games = webman.get_games_list()
for game in games:
  print(f"downloading cover for {game.title}")
  # game.icon is a PS3File object, the same you would get from a directory listing
  url = game.icon.get_url()
  md5 = game.icon.get_md5()
  # logic to download and verify the icon would go in here
```

### Mount a Game

```python
games = webman.get_games_list()
if games:
    games[0].mount()
    print(f"{games[0].title} is now mounted!")
else:
    print("No games found.")
```
