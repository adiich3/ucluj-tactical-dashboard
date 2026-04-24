import pandas as pd

df = pd.read_csv("ucluj_clustered_matches.csv")

# luam doar coloanele numerice

numeric_df = df.select_dtypes(include=["number"])

# calcul medii per cluster

cluster_summary = numeric_df.groupby(df["cluster"]).mean()

print("\nMedii pe cluster:\n")
print(cluster_summary)

# numar meciuri per cluster

counts = df["cluster"].value_counts()

print("\nNumar meciuri per cluster:\n")
print(counts)