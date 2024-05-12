from pymongo import MongoClient
from pprint import pprint
import numpy as np
from sklearn.preprocessing import StandardScaler

client = MongoClient('localhost', 27017)
db = client['music_database']
collection = db['tracks']


mfccs_documents = []

def retrieve_all_documents():
    documents = collection.find()
    for document in documents:
        mfccs_documents.append(document['mfcc'])
        
retrieve_all_documents()



np_array = np.array(mfccs_documents)


scaler = StandardScaler()
standardized_mfccs = scaler.fit_transform(np_array)

for i, document in enumerate(collection.find()):
    print(i)
    collection.update_one(
        {'_id': document['_id']},
        {'$set': {'mfcc': standardized_mfccs[i].tolist()}}
    )
    

