import pandas as pd

reports = pd.read_csv("match_tactical_reports.csv")
vectors = pd.read_csv("ucluj_match_vectors.csv")

print("Total rows reports:", len(reports))
print("Unique matches in reports:", reports["match"].nunique())

print("Total rows vectors:", len(vectors))
print("Unique matches in vectors:", vectors["match"].nunique())