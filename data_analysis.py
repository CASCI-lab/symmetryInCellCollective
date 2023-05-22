import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib import patches as mpatches
from matplotlib import lines as mlines
import pandas as pd
import numpy as np

def loadData():
	new = pd.read_csv("./data/cc-ks-n_0-k_0-PI_0-timeout_10-version_new-trials_5.csv")
	old = pd.read_csv("./data/cc-ks-n_0-k_0-PI_0-timeout_10-version_v0.1.2-trials_5.csv")
	data = pd.concat(
		[new, old],
		ignore_index=True
	)
	return data

if __name__ == "__main__":
	data = loadData()
	# print(data)

	# count number incorrect

	# remove timeouts
	# data = data[data["timeout"]==False]

	# remove duplicate functions
	dataUniq = data.drop_duplicates(subset=["func", "version"])
	dataUniq = dataUniq.sort_values(by=["version", "func"])

	numIncorrect = len(dataUniq[ (dataUniq["version"]=="v0.1.2") & (dataUniq["correct"]==False) ])
	# count number of timeouts
	numTimeoutsNew = len(dataUniq[ (dataUniq["version"]=="new") & (dataUniq["timeout"]==True) ])
	numTimeoutsOld = len(dataUniq[ (dataUniq["version"]=="v0.1.2") & (dataUniq["timeout"]==True) ])

	print(numIncorrect)
	print(numTimeoutsNew, numTimeoutsOld)

	# make two column figure
	fig, axes = plt.subplots(1,2, width_ratios=[0.8, 0.2], figsize=(10,10))

	# plot old vs new time and if it was correct or not
	colors = ["blue" if x==True else "red" for x in dataUniq[dataUniq["version"]=="v0.1.2"]["correct"]]
	axes[0].scatter(dataUniq[dataUniq["version"]=="new"]["time_sym"], dataUniq[dataUniq["version"]=="v0.1.2"]["time_sym"], alpha=0.15, s=dataUniq[dataUniq["version"]=="new"]["k"]**2*5, c=colors)
	axes[0].plot(np.arange(0, 2, 0.1), np.arange(0,2,0.1), linestyle="dashed", color="black")
	# plt.xlim([0, 2]); plt.ylim([0,2])
	axes[0].set_xlim([10**-4, 10])
	axes[0].set_ylim([10**-4, 10])
	axes[0].set_yscale("log"); axes[0].set_xscale("log")
	axes[0].set_xlabel("TSS time, schematodes (sec)", fontsize=22)
	axes[0].set_ylabel("TSS time, v0.1.2 (sec)", fontsize=22)
	axes[0].tick_params(axis="both", labelsize=16)
	redCirc = mlines.Line2D([], [], color="red", marker="o", linestyle="None", markersize=10, label="incorrect in v0.1.2")
	blueCirc = mlines.Line2D([], [], color="blue", marker="o", linestyle="None", markersize=10, label="correct in v0.1.2")
	axes[0].legend(handles=[redCirc, blueCirc])

	# plot boxplot of speedup between old and new, per function
	# compute speedup per function
	speedups = [x/y for x,y in zip(list(dataUniq[dataUniq["version"]=="v0.1.2"]["time_sym"]), list(dataUniq[dataUniq["version"]=="new"]["time_sym"]))]
	print("mean speedup:",np.nanmean(speedups))
	axes[1].boxplot([np.log10(x) for x in speedups if not np.isnan(x)])
	# axes[1].set_yscale("log")
	axes[1].set_ylabel("$\log_{10}($Times Speedup$)$", fontsize=22)
	# axes[1].set_xlabel("v0.1.2 / schematodes")
	axes[1].set_xticks([])
	axes[1].tick_params(axis="both", labelsize=16)
	axes[1].axhline(np.log10(50), linestyle="dashed", c="black", label="mean")
	axes[1].set_ylim([-4,4])
	plt.legend()
	plt.tight_layout()
	fig.savefig("speedup.pdf")

	# plot ks with NON-unique functions
	fig, axes = plt.subplots(2,1, figsize=(5,5))
	sns.set_context("paper")
	sns.histplot(data[data["version"]=="new"], x="ks", bins=15, ax=axes[0])
	axes[0].set_xlabel("$k_s$")
	sns.histplot(data[data["version"]=="new"], x="ks_norm", bins=15, ax=axes[1])
	axes[1].set_xlabel("$k_s / 2^k$")
	plt.tight_layout()
	plt.savefig("ks_dist.pdf")

	# plot ks vs ke
	plt.figure(figsize=(10,10))
	sns.displot(dataUniq[dataUniq["version"]=="new"], x="ke_norm", y="ks_norm", cbar=True)
	plt.xlabel("$k_e/2^k$")
	plt.ylabel("$k_s/2^k$", rotation="horizontal")
	plt.tight_layout()
	plt.savefig("ks_v_ke.pdf")

	# plot time for TSS vs num PI in both versions to see scaling behavior
	plt.figure(figsize=(5,5))
	sns.stripplot(dataUniq, x="numPI", y="time_sym", hue="version", alpha=0.3, jitter=0.25)
	plt.yscale("log")
	plt.xlim([0,13])
	plt.xlabel("Num. Prime Implicants")
	plt.ylabel("TSS time (sec)")
	plt.tight_layout()
	plt.savefig("tss_time-vs-PI-by-version.pdf")

	# plot std
	plt.figure(figsize=(5,5))
	data["time_sym_ratio"] = data["time_sym_std"] / data["time_sym"]
	sns.histplot(data, x="time_sym_ratio", hue="version", element="step", log_scale=(True, False))
	plt.xlabel("TSS time std / TSS time mean")
	plt.savefig("tss_time_std-by-version.pdf")

	# plt.show()
