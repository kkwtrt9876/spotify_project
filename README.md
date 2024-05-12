This project was divided into three steps the first step was etl pipeline, second step was music recommendation model and the third step was deployment.

Etl pipeline:-

The initial part of the ETL process involves extracting audio files from a specified folder. The script uses os.listdir to retrieve all files within the target directory, specifically filtering for MP3 files. For each MP3 file, the script employs the mutagen library to extract the title from the MP3 tags, defaulting to the filename if the title tag isn't available. Additionally, librosa is used to calculate the Mel-frequency cepstral coefficients (MFCCs) for the audio data. It computes the MFCCs for the entire audio file and then calculates the average across all frames to simplify the data and ensure consistency for each file.

After extracting the MFCCs from all audio files, the features are loaded into a NumPy array for batch processing. A StandardScaler from sklearn is utilized to standardize the MFCC data. This scaling adjusts the MFCCs to have a mean of zero and a standard deviation of one, normalizing the data for enhanced performance in future machine learning or data analysis tasks.

In the final phase, each audio file’s metadata and processed MFCCs are stored in a MongoDB collection named tracks within the music_database. The script adds each new entry, which includes the title in lowercase and the list of averaged MFCCs, using insert_one. Once the MFCCs are standardized, the script updates each document in the MongoDB with the new standardized MFCC values using update_one, ensuring the database holds the most relevant and processed data.

Music recommendation model:-

annoy model is being used for this purpose , this finds the approximate near neighbors. The tree size is kept 50 and the processed mfcc are being used in this to make the annoy index. Size by side the id of each mfccs is being tracked inorder to get the results of the model when a query is being made to the model. When the query is being made to the model, it will return the annoy indexes. These annoy indexes will be matched with the ids of the mfccs and from that the title of the recommended songs will be shown to the user. 

Deployment:-

the model made is deployed on the webpage using flask. The flask application manages the ids of different users and keeps track of them. Each user will be shown his own set of recommendations based on his watch history. When ever a new user login into the system he will be randomly shown some songs on the data. When ever a user plays, this is tracked by the kafka producer and send to the consumer. The consumer based on this title get the mfcc of the song and send it to the annoy model to generate the recommendations. These recommendations are then shown to the user when he comes to home page.
