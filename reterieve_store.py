import os
from mutagen.mp3 import MP3
import librosa
import numpy as np
from pymongo import MongoClient

#over 

client = MongoClient('localhost', 27017)
db = client['music_database']
collection = db['tracks']


def calculate_mfcc(file_path):
    # Load the audio file
    y, sr = librosa.load(file_path)
    
    # Compute MFCCs
    mfccs = librosa.feature.mfcc(y=y, sr=sr)
    avg_mfccs = np.mean(mfccs, axis=1).tolist()
    
    
    return avg_mfccs


def list_files_in_folder_with_metadata(folder_path):
    # Check if the folder path exists
    if not os.path.exists(folder_path):
        print(f"The folder '{folder_path}' does not exist.")
        return
    
    # Get a list of all files in the folder
    files = os.listdir(folder_path)
    
    # Print the list of file names and their titles
    print("Files in the folder:")
    for i , file_name in enumerate(files):
        
        if file_name.endswith(".mp3"):
            try:
                file_path = os.path.join(folder_path, file_name)
                audio = MP3(file_path)
                title = audio.tags.get("TIT2", [file_name])[0]
                print(f"{file_name}: {title}")
                data = calculate_mfcc(folder_path+"/"+file_name)
                append_data = {
                    "title" : title.lower(),
                    "mfcc" : data
                }
            
                collection.insert_one(append_data)
                print(f"data inserted {i}")
            except Exception as e:
                pass
        else:
            print(file_name)

# Example usage
folder_path = "/home/i221944/bigdata_project/flask/static/songs"
# folder_path = "/home/i221944/bigdata_project/000"
list_files_in_folder_with_metadata(folder_path)


