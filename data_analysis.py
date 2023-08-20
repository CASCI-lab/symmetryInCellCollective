import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib import patches as mpatches
from matplotlib import lines as mlines
import pandas as pd
import numpy as np

def loadDataCC():
	new = pd.read_csv("./data/cc-ks-n_0-k_0-PI_0-timeout_10-version_new-trials_5.csv")
	old = pd.read_csv("./data/cc-ks-n_0-k_0-PI_0-timeout_10-version_v0.1.2-trials_5.csv")
	data = pd.concat(
		[new, old],
		ignore_index=True
	)
	return data

def loadDataRng():
	new = pd.read_csv("./data/rng-funcs-rng-n_200-k_5-biasStep_6.txt-PI_0-timeout_10-version_new-trials_5.csv")
	old = pd.read_csv("./data/rng-funcs-rng-n_200-k_5-biasStep_6.txt-PI_0-timeout_10-version_v0.1.2-trials_5.csv")
	data = pd.concat(
		[new, old],
		ignore_index=True
	)
	return data

def analysis(data, source):
	# print(data)

	# count number incorrect

	# remove timeouts
	# data = data[data["timeout"]==False]

	# remove duplicate functions
	dataUniq = data.drop_duplicates(subset=["func", "version"])
	dataUniq = dataUniq.sort_values(by=["version", "func"])
	print(dataUniq)

	numIncorrect = len(dataUniq[ (dataUniq["version"]=="v0.1.2") & (dataUniq["correct"]==False) ])
	# count number of timeouts
	numTimeoutsNew = len(dataUniq[ (dataUniq["version"]=="new") & (dataUniq["timeout"]==True) ])
	numTimeoutsOld = len(dataUniq[ (dataUniq["version"]=="v0.1.2") & (dataUniq["timeout"]==True) ])

	print(numIncorrect)
	print(numTimeoutsNew, numTimeoutsOld)

	# make two column figure
	# fig, axes = plt.subplots(1,2, width_ratios=[0.8, 0.2], figsize=(10,10))
	fig = plt.figure(figsize=(10,10))

	# plot old vs new time and if it was correct or not
	ax1 = plt.subplot2grid((6,7), (1,0), colspan=3, rowspan=5)
	colors = ["blue" if x==True else "red" for x in dataUniq[dataUniq["version"]=="v0.1.2"]["correct"]]
	ax1.scatter(dataUniq[dataUniq["version"]=="new"]["time_sym"], dataUniq[dataUniq["version"]=="v0.1.2"]["time_sym"], alpha=0.15, s=dataUniq[dataUniq["version"]=="new"]["k"]**2*5, c=colors)
	ax1.plot(np.arange(0, 2, 0.1), np.arange(0,2,0.1), linestyle="dashed", color="black")
	# plt.xlim([0, 2]); plt.ylim([0,2])
	ax1.set_xlim([10**-4, 10])
	ax1.set_ylim([10**-4, 10])
	ax1.set_yscale("log"); ax1.set_xscale("log")
	ax1.set_xlabel("TSS time, schematodes (sec)", fontsize=22)
	ax1.set_ylabel("TSS time, v0.1.2 (sec)", fontsize=22)
	ax1.tick_params(axis="both", labelsize=16)
	redCirc = mlines.Line2D([], [], color="red", marker="o", linestyle="None", markersize=10, label="incorrect in v0.1.2")
	blueCirc = mlines.Line2D([], [], color="blue", marker="o", linestyle="None", markersize=10, label="correct in v0.1.2")
	ax1.legend(handles=[redCirc, blueCirc])
	ax1.margins(0)

	# plot boxplot of speedup between old and new, per function
	# compute speedup per function
	ax2 = plt.subplot2grid((6,7), (0,5), rowspan=6, colspan=2)
	speedups = [x/y for x,y in zip(list(dataUniq[dataUniq["version"]=="v0.1.2"]["time_sym"]), list(dataUniq[dataUniq["version"]=="new"]["time_sym"]))]
	print("mean speedup:",np.nanmean(speedups))
	ax2.boxplot([np.log10(x) for x in speedups if not np.isnan(x)])
	# ax2.set_yscale("log")
	ax2.set_ylabel("$\log_{10}($Times Speedup$)$", fontsize=22)
	# ax2.set_xlabel("v0.1.2 / schematodes")
	ax2.set_xticks([])
	ax2.tick_params(axis="both", labelsize=16)
	ax2.axhline(np.log10(np.nanmean(speedups)), linestyle="dashed", c="black", label="mean")
	ax2.set_ylim([-4,4])

	# plot timeouts in separate axes
	dataUniqMerge = dataUniq[dataUniq["version"]=="new"].merge(dataUniq[dataUniq["version"]=="v0.1.2"], on="Unnamed: 0")
	newOnlyTimeout = dataUniqMerge[(dataUniqMerge["timeout_x"]==True)&(dataUniqMerge["timeout_y"]==False)]
	newOnlyTimeout.to_csv(f"newOnlyTimeout-{source}.csv")
	oldOnlyTimeout = dataUniqMerge[(dataUniqMerge["timeout_x"]==False)&(dataUniqMerge["timeout_y"]==True)]
	# how many timeout on both?
	print("both timeout:", len(dataUniqMerge[(dataUniqMerge["timeout_x"]==True)&(dataUniqMerge["timeout_y"]==True)]))

	ax3 = plt.subplot2grid((6,7), (0,0), colspan=3)
	# colors = ["blue" if x==True else "red" for x in oldOnlyTimeout["correct_
	ax3.scatter(oldOnlyTimeout["time_sym_x"], [0]*len(oldOnlyTimeout.index), c="black", alpha=0.2, s=oldOnlyTimeout["k_x"]**2*5)
	ax3.set_yticks([])
	ax3.set_xlim([10**-4, 10])
	ax3.set_xscale("log")
	ax3.set_xticks([], minor=True)
	ax3.set_xticks([], minor=False)
	ax3.set_ylabel("timeout")

	ax4 = plt.subplot2grid((6,7), (1,3), rowspan=5)
	colors = ["blue" if x==True else "red" for x in newOnlyTimeout["correct_y"]]
	ax4.scatter([0]*len(newOnlyTimeout.index), newOnlyTimeout["time_sym_y"], c=colors, alpha=0.2, s=newOnlyTimeout["k_x"]**2*5)
	ax4.set_xticks([])
	ax4.set_ylim([10**-4, 10])
	ax4.set_yscale("log")
	ax4.set_yticks([], minor=True)
	ax4.set_yticks([], minor=False)
	ax4.set_xlabel("timeout")
	ax4.margins(0)

	# plt.legend()
	plt.tight_layout()
	fig.savefig(f"figs/speedup-{source}.pdf")

	
	# plot ks with NON-unique functions
	fig, axes = plt.subplots(2,1, figsize=(5,5))
	sns.set_context("paper")
	sns.histplot(data[data["version"]=="new"], x="ks", bins=15, ax=axes[0])
	axes[0].set_xlabel("$k_s$")
	sns.histplot(data[data["version"]=="new"], x="ks_norm", bins=15, ax=axes[1])
	axes[1].set_xlabel("$k_s / k$")
	plt.tight_layout()
	plt.savefig(f"figs/ks_dist-{source}.pdf")

	axes[0].set_yscale("log")
	axes[0].set_xscale("log")
	axes[1].set_yscale("log")
	axes[1].set_xscale("log")
	plt.savefig(f"figs/ks_dist-{source}-loglog.pdf")

	# plot ks vs ke
	plt.figure(figsize=(10,10))
	sns.displot(dataUniq[dataUniq["version"]=="new"], x="ke_norm", y="ks_norm", cbar=True, binwidth=0.05, binrange=((0,1), (0,1)))
	plt.ylim(0,1)
	# plt.gca().set_ylim([0, 1])
	plt.xlabel("$k_e/k$")
	plt.ylabel("$k_s/k$", rotation="horizontal")
	plt.tight_layout()
	plt.axis("equal")
	plt.savefig(f"figs/ks_v_ke-{source}.pdf")

	# plot time for TSS vs num PI in both versions to see scaling behavior
	plt.figure(figsize=(5,5))
	sns.stripplot(dataUniq, x="numPI", y="time_sym", hue="version", alpha=0.3, jitter=0.25)
	plt.yscale("log")
	plt.xlim([0,13])
	plt.xlabel("Num. Prime Implicants")
	plt.ylabel("TSS time (sec)")
	plt.tight_layout()
	plt.savefig(f"figs/tss_time-vs-PI-by-version-{source}.pdf")

	# plot std
	plt.figure(figsize=(5,5))
	data["time_sym_ratio"] = data["time_sym_std"] / data["time_sym"]
	sns.histplot(data, x="time_sym_ratio", hue="version", element="step", log_scale=(True, False))
	plt.xlabel("TSS time std / TSS time mean")
	plt.savefig(f"figs/tss_time_std-by-version-{source}.pdf")

	# plt.show()

def compare(dataCC, dataRng):
	data = pd.concat( [dataCC, dataRng], ignore_index=True)
	data = data[data["version"]=="new"] # looking at calc from NEW version only, comparing CC and Rng
	# print(data)

	sns.set_context("paper")
	plt.figure(figsize=(5,5))
	sns.histplot(data, x="ks_norm", common_norm=False, hue="source")
	plt.savefig(f"figs/ks-dist-compare.pdf")

if __name__ == "__main__":
	analysis(loadDataCC(), "cc")
	analysis(loadDataRng(), "rng")
	compare(loadDataCC(), loadDataRng())


