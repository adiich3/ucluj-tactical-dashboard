import pandas as pd
from sklearn.ensemble import RandomForestClassifier

df = pd.read_csv("ucluj_labeled_matches.csv")

X = df.drop(columns=[
    "match",
    "cluster",
    "good_match"
])

y = df["good_match"]

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X, y)

predictions = model.predict(X)

df["predicted_match_quality"] = predictions

df.to_csv(
    "predicted_match_quality.csv",
    index=False
)

print("Fisier creat: predicted_match_quality.csv")