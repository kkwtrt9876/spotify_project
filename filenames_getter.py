import os
from mutagen.mp3 import MP3

folder_path = '/home/i221944/bigdata_project/flask/static/songs'

files = os.listdir(folder_path)

with open('names.txt', 'a') as file:
    for file_name in files:
        try:
            if file_name.endswith(".mp3"):
                file_path = os.path.join(folder_path, file_name)
                audio = MP3(file_path)
                title = audio.tags.get("TIT2", [file_name])[0]
                title = title.lower()
                file.write(f"{title}\t{file_name}\n")
        except Exception as e:
            print(f"Error processing file '{file_name}': {e}")
