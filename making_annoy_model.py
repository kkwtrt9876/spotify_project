from annoy import AnnoyIndex
from pymongo import MongoClient

f = 20  # Assume query_mfcc is correctly sized
annoy_index = AnnoyIndex(f, 'angular')  # Use angular distance
mongodb_ids = []

client = MongoClient('localhost', 27017)
db = client['music_database']
collection = db['tracks']

for i, doc in enumerate(collection.find()):
    mfccs = doc['mfcc']
    annoy_index.add_item(i, mfccs)
    mongodb_ids.append(doc['_id'])

print(len(mongodb_ids))    

try:
    with open("ids.txt", 'a') as file:
        for id in mongodb_ids:
            file.write(f"{id}\n")
            print(id)
except Exception as e:
    print("An error occurred while writing to ids.txt:", e)


annoy_index.build(50)  # Number of trees, increase for larger datasets
annoy_index.save('mfcc_index.ann')
