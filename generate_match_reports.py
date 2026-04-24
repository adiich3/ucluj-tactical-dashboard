import pandas as pd

df = pd.read_csv("predicted_match_quality.csv")

reports = []

for _, row in df.iterrows():

    reasons = []

    if row["risk_index"] > df["risk_index"].median():
        reasons.append("High ball loss risk")

    if row["attacking_threat_index"] < df["attacking_threat_index"].median():
        reasons.append("Low attacking threat")

    if row["progression_index"] < df["progression_index"].median():
        reasons.append("Poor progression")

    if row["defensive_stability_index"] < df["defensive_stability_index"].median():
        reasons.append("Weak defensive stability")

    if len(reasons) == 0:
        reasons.append("Balanced performance")

    reports.append({
        "match": row["match"],
        "cluster": row["cluster"],
        "predicted_quality": row["predicted_match_quality"],
        "main_issues": "; ".join(reasons)
    })

report_df = pd.DataFrame(reports)

report_df.to_csv(
    "match_tactical_reports.csv",
    index=False
)

print("Fisier creat: match_tactical_reports.csv")