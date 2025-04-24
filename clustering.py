import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
import hashlib
import matplotlib.pyplot as plt


def stable_hash(s):
    # Get consistent integer from a hash string
    try:
        return float(int(hashlib.sha256(s.encode()).hexdigest(), 16) % 1e8) /1e8
    except AttributeError:
        # Cases for ints and floats
        return float(s) #int(hashlib.sha256(s).hexdigest(), 16)


# Loading and preprocessing the data
raw_data = pd.read_csv('cftr.csv', dtype = str)
raw_data = raw_data.drop(columns=['gnomAD ID'])
#raw_data = raw_data.dropna()

# Convert all columns to string and hash them
data = raw_data.applymap(stable_hash) #np.empty((len(raw_data), len(raw_data.columns)))
#data = data.dropna()

filter(lambda x: len(x) != 0, data)

data = data.dropna(axis = 1) # Dropping columns with all NaN values

print(data)

# Normalizing data
scaler = StandardScaler()
scaled_data = scaler.fit_transform(data)

# Apply KMeans
kmeans = KMeans(n_clusters=3, random_state=42)
kmeans.fit(scaled_data)

print("Cluster centers:", kmeans.cluster_centers_)
print("Labels:", kmeans.labels_)

#print(data)
