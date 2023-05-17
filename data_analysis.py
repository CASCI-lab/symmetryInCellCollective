import seaborn as sns
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

data = pd.concat(
	[
	 pd.read_csv("./data/cc-ks-n_0-k_0-PI_15.csv"),
	 pd.read_csv("./data/rng-ks-n_50-k_5-PI_15-biasStep_6.csv")
	],
	ignore_index=True
)
data = data[data["k"]<=5]
print(data)
missing = data[np.isnan(data["ks"])] 
print(missing)

sns.histplot(data=missing, x="k", hue="source")

sns.displot(data=data, x="numPI", hue="source", col="k", col_wrap=3, common_norm=False, stat="probability")

plt.figure()
sns.stripplot(data=data, x="k", y="ks", hue="source", jitter=0.2)
plt.figure()
sns.stripplot(data=data, x="numPI", y="ks", hue="source", jitter=0.2)
sns.pairplot(data, vars=["ks", "ks_norm", "k", "bias", "ke", "ke_norm", "numPI"], hue="source")

plt.show()
