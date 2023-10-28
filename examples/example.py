from ps3webman import *

import time

webman_ip = '10.100.102.12'
webman_port = 80

# Initialize the WebMan class
webman = WebMan(ip=webman_ip, port=webman_port)

# 1. Display CPU and RSX temperatures
cpu_temp, rsx_temp = webman.get_temps()
print(f"CPU Temperature: {cpu_temp}°C, RSX Temperature: {rsx_temp}°C")

# 2. Get and display fan speed
fan_speed = webman.get_fan_speed()
print(f"Fan Speed: {fan_speed}%")

# 3. Get and display HDD space
hdd_space = webman.get_hdd_space()
print(f"Free HDD Space: {hdd_space}GB")

# 4. Display a notification on the PS3
webman.notify("Hello from WebMan!", NotificationIconType.INFO, BuzzType.SND_TROPHY)

# 5. Make the PS3 beep
webman.buzz(BuzzType.TRIPLE)

# 6. List all games and mount the first one
games = webman.get_games_list()
if games:
    print("Games List:")
    for i, game in enumerate(games, start=1):
        print(f"{i}. {game.title}")
    print("\nMounting the first game...")
    first_game = games[0]
    first_game.mount()
    print(f"{first_game.title} mounted successfully!")
else:
    print("No games found.")

# 7. Navigate to a directory and list all files and directories
directory = webman.get_directory('/dev_hdd0')
print("\nListing contents of /dev_hdd0:")
for item in directory.get_listing():
    print(item)

# 8. Fetch and display information about a specific file
example_file = directory.get_file('HENplugin.sprx')
if example_file:
    md5 = example_file.get_md5()
    size = example_file.get_size()
    print(f"\nInformation about HENPlugin.sprx (HEN-related file):")
    print(f"MD5: {md5}")
    print(f"Size: {size}")
else:
    print("\nHENPlugin is not found. HEN is probably not installed.")

# 9. Additional delays to observe notifications and beeps on the PS3
time.sleep(5)
print("Script execution finished.")
