import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# citire date

df = pd.read_csv("ucluj_labeled_matches.csv")

X = df.drop(columns=[
    "match",
    "cluster",
    "good_match"
])

y = df["good_match"]

# split

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.3,
    random_state=42
)

# model

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# predictie

y_pred = model.predict(X_test)

# salvare classification report

report = classification_report(y_test, y_pred)

with open("model_metrics.txt", "w") as f:
    f.write(report)

# feature importance

importance = model.feature_importances_

features = X.columns

feature_importance_df = pd.DataFrame({
    "feature": features,
    "importance": importance
})

feature_importance_df = feature_importance_df.sort_values(
    by="importance",
    ascending=False
)

# salvare importance

feature_importance_df.to_csv(
    "feature_importance.csv",
    index=False
)

print("Model antrenat.")
print("Fisier creat: model_metrics.txt")
print("Fisier creat: feature_importance.csv")