from flask import Flask, render_template, request, redirect, url_for,jsonify,flash
import os
from mutagen.mp3 import MP3
import json
from threading import Thread
from kafka import KafkaConsumer
import json
from kafka import KafkaProducer
from annoy import AnnoyIndex
from pymongo import MongoClient
import numpy as np
from bson.objectid import ObjectId
import random 



client = MongoClient('localhost', 27017)
db = client['music_database']
collection = db['tracks']
collection1 = db['users']

mfcc_list = []

username = ' '
password = ' '

def start_consumer():
    global songs
    
    consumer = KafkaConsumer(
        'user-activity',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='latest',
        group_id='data', 
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    for message in consumer:
        data = message.value
        
        if data:
            filter = {'username': username}
            
            songs = []
            print(f"recieved data in consumer {data}")
            
            to_Check = data['track_name']
            
            single_mfcc = []
            for data in to_Check:
                value = data.lower()
                single_mfcc.append(collection.find_one({'title': value})['mfcc'])
                
            
            
            mfccs_np = np.array(single_mfcc)
            avg_mfcc = np.mean(mfccs_np, axis=0)
            f = 20
            annoy_index = AnnoyIndex(f, 'angular')
            annoy_index.load('/home/i221944/bigdata_project/flask/mfcc_index.ann')
            num_neighbors = 10  # Number of nearest neighbors to retrieve
            nearest_ids = annoy_index.get_nns_by_vector(avg_mfcc, num_neighbors)
            list_ids = []
            with open("/home/i221944/bigdata_project/flask/ids.txt",'r') as file:
                for line in file:
                    data = line.strip()
                    list_ids.append(data)
        
            new_ids = []

            for id in nearest_ids:
                id = int(id)
                new_ids.append(list_ids[id])

            for id in new_ids:
                object_id = ObjectId(id)
                result = collection.find_one({'_id':object_id})
                print(result['title'])
                songs.append(result['title'])
                
            updated_songs = []
            
            
            for key in songs_name:
                for name in songs:
                    if key['song'] == name:
                        updated_songs.append(key)
                        break
                    
            print(f"print updated songs in the consumer {updated_songs}")
            collection1.update_one(filter, {'$set': {'history': updated_songs}})
            
                    

            
            
            
       

# Run the consumer in a background thread
consumer_thread = Thread(target=start_consumer)
consumer_thread.start()
producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

app = Flask(__name__)
app.secret_key = 'project' 

songs_name = []
folder_path = '/home/i221944/bigdata_project/flask/names.txt'

@app.route('/')
def home(): #in this block the names of all the song along with the url to get the songs in bein stored
    global condition
    condition = False
    global songs_name  
    songs_name = [] 
    with open(folder_path, 'r') as file:
        for line in file:
            song = {}
            line = line.strip().split('\t')
            song['song'] = line[0]
            song['source'] = url_for('static', filename='songs/' + line[1])
            songs_name.append(song)
            print(song)

    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    global username
    global password
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        data_validate = collection1.find_one({'username':username,'password':password})
        
        if data_validate:
            return redirect(url_for('welcome'))
        else:
            flash('wrong credentials', 'error')
            return render_template('login.html')
            
    return render_template('login.html')        
    

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    global username
    global password
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Safely attempt to retrieve the username
        user_document = collection1.find_one({'username': username})
        
        if user_document:
            # Username exists, flash error and stay on signup page
            flash('Username already exists', 'error')
            return render_template('signup.html')
        else:
            random_num1 = random.randint(1,100000)
            random_num2 = random_num1 + 20
            watched = []
            data_insert = {
                'username':username,
                'password':password,
                'history':songs_name[random_num1:random_num2],
                'watched': watched
            }
            
            collection1.insert_one(data_insert)
            
            return redirect(url_for('welcome'))  # Redirect to the welcome page for now
            
    # GET request or not redirected, show the signup form
    return render_template('signup.html')

@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    # global condition
    # global songs 
    # global username
    # global password
    
    updated_songs = []
    data = collection1.find_one({'username':username,'password':password})
    if data:
        updated_songs = data['history']
        # print(updated_songs)
        return render_template('welcome.html',songs = updated_songs)
    else:
        print("not present")

    

@app.route('/search',methods = ['GET',"POST"])
def search():
    songs = []
    if request.method == 'POST':
        query = request.form['query'].lower()
        for data in songs_name:
            if data['song'] == query:
                songs.append(data)
                break
            
            
    return render_template('welcome.html', songs=songs)
    
    
@app.route('/track-play', methods=['POST'])
def track_play():
    
    
    data = request.get_json()
    track_name = data['trackName']
    print(track_name)
    
    data_history = list(collection1.find_one({'username':username})['watched'])
    data_history.append(track_name)
    
    collection1.update_one({'username':username}, {'$set': {'watched': data_history}})
    
    # print(f"data history :- {data_history}")
    
    producer.send('user-activity', {'track_name': data_history})
    
    return jsonify({'status': 'success'}), 200


@app.route('/play/<song_name>')
def play_song(song_name):
    # Find the song by name
    song = next((item for item in songs_name if item['song'] == song_name), None)
    if song:
        return render_template('play_song.html', song=song)
    else:
        return 'Song not found', 404



@app.route('/logout')
def logout():
    # Add your logout handling logic here, perhaps clearing session data
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
