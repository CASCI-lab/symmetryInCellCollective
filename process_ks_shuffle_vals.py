# type: ignore

import numpy as np
import pandas as pd

from data_analysis import loadDataCC

N_TRIALS_PER_FUNC = 12

cc = loadDataCC()

cc = cc[cc["version"] == "new"].merge(
    cc[cc["version"] == "v0.1.2"],
    on="Unnamed: 0",
    suffixes=("_v1.0.0", "_v0.1.2"),
)

with open("ks_shuffle_vals.csv", "r") as f:
    line = f.readline()

    vals = np.array(list(map(float, line.split(","))))

nontrivial_rows = [
    row
    for _, row in cc.iterrows()
    if len(list(row["func_v1.0.0"])) != 2 and len(set(list(row["func_v1.0.0"]))) != 1
]

samples = [
    vals[i : i + N_TRIALS_PER_FUNC] for i in range(0, len(vals), N_TRIALS_PER_FUNC)
]

df = pd.DataFrame(nontrivial_rows)
df["ks_shuffle_vals"] = samples
df["ks_shuffle_vals"] = df["ks_shuffle_vals"].map(list).map(repr)
df.to_csv("nontrivial_cc_rules_with_shuffle_vals.csv", index=True)
