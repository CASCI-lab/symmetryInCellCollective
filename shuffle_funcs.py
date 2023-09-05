# type: ignore
import multiprocessing
import random

import numpy as np
from cana.boolean_node import BooleanNode

from data_analysis import loadDataCC

TIMEOUT_SECS = 50
N_TRIALS_PER_FUNC = 12


def sym(bn, ks, index):
    ks[index] = bn.input_symmetry()


if __name__ == "__main__":
    cc = loadDataCC()

    cc = cc[cc["version"] == "new"].merge(
        cc[cc["version"] == "v0.1.2"],
        on="Unnamed: 0",
        suffixes=("_v1.0.0", "_v0.1.2"),
    )

    ks_shuffle_vals = []
    for cc_row, cc_func in enumerate(cc["func_v1.0.0"]):
        f_out = list(cc_func)
        processes = []
        ks = multiprocessing.Array("f", [np.nan] * N_TRIALS_PER_FUNC)
        for trial in range(N_TRIALS_PER_FUNC):
            random.shuffle(f_out)
            bn = BooleanNode(k=int(np.log2(len(f_out))), outputs=f_out)
            p = multiprocessing.Process(target=sym, args=(bn, ks, trial), daemon=True)
            p.start()
            processes.append(p)

        # for p in processes:
        #     p.start()
        for p in processes:
            p.join(TIMEOUT_SECS)
        for p in processes:
            if p.is_alive():
                print("Timeout reached...")
                p.terminate()
                print("Terminated!")

        print(
            f"rule {cc_row}/{len(cc['func_v1.0.0'])}, shuffle {trial+1}/{N_TRIALS_PER_FUNC} : ks = {ks[:]}"
        )
        ks_shuffle_vals += ks[:]
    with open("ks_shuffle_vals.csv", "w") as f:
        f.write(",".join(map(str, ks_shuffle_vals)))
