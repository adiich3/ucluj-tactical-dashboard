import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# citire date

df = pd.read_csv("ucluj_match_vectors.csv")

# scoatem coloana match (nu e numerica)

features = df.drop(columns=["match"])

# normalizare date

scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

# alegem numar de clusteri

kmeans = KMeans(n_clusters=4, random_state=42)

df["cluster"] = kmeans.fit_predict(scaled_features)

# salvare rezultat

df.to_csv("ucluj_clustered_matches.csv", index=False)

print("Clustering finalizat.")
print(df[["match", "cluster"]])

# vizualizare simpla (2 dimensiuni)

plt.scatter(
    scaled_features[:, 0],
    scaled_features[:, 1],
    c=df["cluster"]
)

plt.title("Match Clusters")
plt.xlabel("Feature 1")
plt.ylabel("Feature 2")

plt.show()