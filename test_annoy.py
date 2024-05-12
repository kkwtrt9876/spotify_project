from annoy import AnnoyIndex
from pymongo import MongoClient
import numpy as np
from bson.objectid import ObjectId




client = MongoClient('localhost', 27017)
db = client['music_database']
collection = db['tracks']

def average_mfccs(mfccs):
    # Assuming mfccs is a list of MFCC arrays
    mfccs_np = np.array(mfccs)
    avg_mfcc = np.mean(mfccs_np, axis=0)
    return avg_mfcc

# Example MFCCs from the last 5 songs listened to by a user
last_five_mfccs = [
    collection.find_one({'title': 'where do we go?'})['mfcc'],
    collection.find_one({'title': 'shine'})['mfcc'],
    collection.find_one({'title': 'december song'})['mfcc'],
    collection.find_one({'title': 'butter in my head'})['mfcc'],
    collection.find_one({'title': 'stcfthots'})['mfcc']
]

# Compute the average MFCC
query_mfcc = average_mfccs(last_five_mfccs)


# Load your pre-built Annoy index
f = 20  # Dimension of the MFCC vector
annoy_index = AnnoyIndex(f, 'angular')  # Change 'euclidean' to your preferred distance metric
annoy_index.load('mfcc_index1.ann')  # Path to the saved index file

# Query the index
num_neighbors = 10  # Number of nearest neighbors to retrieve
nearest_ids = annoy_index.get_nns_by_vector(query_mfcc, num_neighbors)

# for id in nearest_ids:
#     print(id)

list_ids = []
with open("ids1.txt",'r') as file:
    for line in file:
        data = line.strip()
        list_ids.append(data)
        
new_ids = []

for id in nearest_ids:
    id = int(id)
    new_ids.append(list_ids[id])
    

document = collection.find()

for id in new_ids:
    object_id = ObjectId(id)
    result = collection.find_one({'_id':object_id})
    print(result['title'])


# for item in document:
#     data = item['_id']
#     print(type(data))
#     break