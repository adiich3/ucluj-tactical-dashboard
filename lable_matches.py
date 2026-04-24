import pandas as pd

df = pd.read_csv("ucluj_clustered_matches.csv")

# praguri automate

attack_threshold = df["attacking_threat_index"].median()
risk_threshold = df["risk_index"].median()

def label_match(row):

    if (
        row["attacking_threat_index"] > attack_threshold
        and
        row["risk_index"] < risk_threshold
    ):
        return 1  # good match

    return 0  # bad match

df["good_match"] = df.apply(label_match, axis=1)

df.to_csv("ucluj_labeled_matches.csv", index=False)

print("Labeluri generate.")
print(df["good_match"].value_counts())