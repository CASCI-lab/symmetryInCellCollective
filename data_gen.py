from cana.datasets.bio import load_all_cell_collective_models
from cana.boolean_node import BooleanNode
import pandas as pd
from tqdm import tqdm
import time
import numpy as np
import argparse
import math
from multiprocessing import Process, Queue
import queue
from helper import compare
import os

def runSym(node: BooleanNode, q: Queue):
    """compute two-symbol schemata of node. Return result and time taken through q. This should be used to start a forked process from main.
    Note: this does NOT check that node has already computed everything necessary for two-symbol calculation.
    """
    t0 = time.time()
    node._check_compute_canalization_variables(two_symbols=True)
    q.put(time.time() - t0)
    q.put(node._two_symbols)

# collect all CC functions
def getCCNodes(n, k):
    """return BooleanNode objects from the Cell collective.

    Params:
        n: the number to return
        k: the maximum k of the function to return
    Returns:
        (list of BooleanNode)
    """
    nodes = [node for network in load_all_cell_collective_models() for node in network.nodes if node.k <= k or k==0]
    if n <= 0:
        return nodes
    else:
        return nodes[:n]

def getRandomNodes(n, ks, biass):
    rng = np.random.default_rng()
    nodes = []
    hist = set()
    for k in ks:
        numLUT = 2**k
        for p in biass:
            numOnes = math.floor(p*numLUT)
            f = "1"*numOnes + "0"*(numLUT-numOnes)
            for i in range(n):
                tmp = list(f)
                rng.shuffle(tmp)
                tmp2 = "".join(tmp)
                if tmp2 not in hist:
                    nodes.append(BooleanNode(k=k, outputs=tmp))
                    hist.add(tmp2)
    return nodes

# get their ks and other variables
# prime implicants, time taken on each, k, bias
# only attempt symmetry if PI < some value
def computeOnNodes(nodes, maxPI, timeoutSecs, ntrials):
    """compute symmetry and other properties of BooleanNodes in nodes.

    Params:
        maxPI: the threshold for not computing symmetry on the function.
        timeoutSecs: the seconds before timeout during the symmetry calculation.
        ntrials: the number of times to compute the symmetry on the same function
    """
    # initialize data frame
    data = pd.DataFrame(columns=["network", "name", "func", "k", "bias", "numPI", "time_PI", "ks", "time_sym", "time_ks", "time_cov", "ke", "tss", "correct", "timeout", "time_sym_std"])
    # for each BooleanNode
    for n in (pbar := tqdm(nodes)):
        info = f"{n.name:>10}, k: {n.k:>3}, {''.join(n.outputs)[:32]:>32}"
        pbar.set_description(info + " PI")

        # default values for row
        func = "".join(map(str, n.outputs))
        k = n.k
        bias = n.bias()
        time_sym = np.nan
        time_sym_std = np.nan
        time_ks = np.nan
        time_cov = np.nan
        ks = np.nan
        time_PI = np.nan
        numPI = np.nan
        ke = np.nan
        tss = np.nan
        correct = np.nan
        timeout = False

        # wrap in try for timeout
        try:
        
            # compute prime implicants
            t0 = time.time()
            n._check_compute_canalization_variables(prime_implicants=True)
            time_PI = time.time() - t0
            numPI = max([len(i[1]) for i in n._prime_implicants.items()])

            ke = n.effective_connectivity(norm=False)

            if maxPI == 0 or numPI <= maxPI: # only continue if not too many PI
                # setup process call for implementing a timeout
                symTimes = []
                for trial in range(ntrials):
                    n._two_symbols = None # reset two symbol result so calculation is recomputed for each trial
                    q = Queue()
                    p = Process(target=runSym, args=(n, q)) # will compute two-symbol symmetry in spawned process
                    pbar.set_description(info + " SY")
                    p.start()
                    time_sym_tmp = q.get(timeout=timeoutSecs) # raises queue.Empty on timeout
                    n._two_symbols = q.get() # data not shared between processes, so Node object passed is not the same one in this scope
                    p.join()
                    symTimes.append(time_sym_tmp)
                time_sym = np.mean(symTimes)
                time_sym_std = np.std(symTimes)

                # check if F'' is same function as was given (i.e., if it got it right)
                tss = [n._two_symbols[0],  n._two_symbols[1]]
                correct0 = compare(n._prime_implicants["0"], n._two_symbols[0])[0] if "0" in n._prime_implicants else True
                correct1 = compare(n._prime_implicants["1"], n._two_symbols[1])[0] if "1" in n._prime_implicants else True
                correct =  correct0 and correct1

                # NOTE: comment out CO and KS steps for cana==0.1.2, as ks is broken and implemented differently
                pbar.set_description(info + " CO")
                t0 = time.time()
                n._check_compute_canalization_variables(ts_coverage="whatever bro") # this step is necessary for ks
                time_cov = time.time() - t0

                pbar.set_description(info + " KS")
                t0 = time.time()
                # ks = n.input_symmetry(aggOp="mean", kernel="numDots", sameSymbol=False)
                ks = n.input_symmetry_mean() # this version is faster
                time_ks = time.time() - t0

        except queue.Empty: # handles the timeout
            print("timeout on SY")
            timeout = True
            os.kill(p.pid, 9) # need os level call because stuck in Rust call
            print("process killed")
            p.join()
            p.close()

            # handle case where timeout occurred but function TSS completed on previous trial
            if len(symTimes) > 0:
                print(f"WARNING: {n.network.name}, {n.name}, {func} timed out but previously completed")

        # put row in frame with whatever was able to be computed
        data.loc[len(data.index)] = [n.network.name, n.name, func, k, bias, numPI, time_PI, ks, time_sym, time_ks, time_cov, ke, tss, correct, timeout, time_sym_std]
    return data


def runCC(args):
    data = computeOnNodes(getCCNodes(args.n, args.k), args.maxPI, args.timeoutSecs, args.ntrials)
    # compute normalized variants
    data["ks_norm"] = data["ks"] / data["k"]
    data["ke_norm"] = data["ke"] / data["k"]
    # annotate data
    data["source"] = ["cc"]*len(data.index) 
    data["version"] = [args.CANAversion]*len(data.index)
    data.to_csv(f"data/cc-ks-n_{args.n}-k_{args.k}-PI_{args.maxPI}-timeout_{args.timeoutSecs}-version_{args.CANAversion}-trials_{args.ntrials}.csv")
    return data

# TODO: add timestamp to csv
def runRng(args):
    data = computeOnNodes(getRandomNodes(args.n, range(1, args.k+1), np.linspace(0, 0.5, num=args.biasStep)), args.maxPI)
    data["ks_norm"] = data["ks"] / data["k"]
    data["ke_norm"] = data["ke"] / data["k"]
    data["source"] = ["rng"]*len(data.index)
    data.to_csv(f"data/rng-ks-n_{args.n}-k_{args.k}-PI_{args.maxPI}-biasStep_{args.biasStep}.csv")
    return data

# output csv
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_cc = subparsers.add_parser("cc")
    parser_cc.add_argument("n", type=int, help="number of nodes to examine. 0 for all")
    parser_cc.add_argument("k", type=int, help="maxmimum k to examine. 0 for all")
    parser_cc.add_argument("maxPI", type=int, help="maximum number of PI a function can have to be examined. 0 for no max")
    parser_cc.add_argument("timeoutSecs", type=int, help="number of seconds to wait for TSS to complete. 0 for no timeout")
    parser_cc.add_argument("--CANAversion", type=str, help="the CANA version to use to compute. NOTE: does NOT change the version, just annotates the data.", default=None)
    parser_cc.add_argument("--ntrials", type=int, help="the number of times to compute the two-symbol symmetry for each function, for benchmarking purposes", default=1)
    parser_cc.set_defaults(func=runCC)

    parser_rng = subparsers.add_parser("random")
    parser_rng.add_argument("n", type=int, help="number of unique functions to generate at each parameterization")
    parser_rng.add_argument("k", type=int, help="max k of functions to generate")
    parser_rng.add_argument("maxPI", type=int, help="maximum number of PI a function can have to be examined")
    parser_rng.add_argument("biasStep", type=int, help="step size on bias")
    parser_rng.set_defaults(func=runRng)

    args = parser.parse_args()

    args.func(args)