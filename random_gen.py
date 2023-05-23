import numpy as np
from cana.boolean_node import BooleanNode
import math

def getRandomNodes(n, ks, biass):
    rng = np.random.default_rng()
    funcs = []
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
                    funcs.append((tmp2))
                    hist.add(tmp2)
    return funcs

def loadFuncs(file):
	nodes = []
	with open(file, "r") as fd:
		for f in fd.readlines():
			f = f[:-1]
			n = BooleanNode(k=int(np.log2(len(f))), outputs=list(f))
			nodes.append(n)
	return nodes

if __name__ == "__main__":
	n = 5
	k = 4
	biasStep = 6
	funcs = getRandomNodes(n, range(1, k+1), np.linspace(0, 0.5, num=biasStep))
	with open(f"functions/funcs-rng-n_{n}-k_{k}-biasStep_{biasStep}.txt", "w") as fd:
		fd.write("\n".join(funcs))
	# print(list(map(lambda x:x.effective_connectivity(), loadFuncs("test"))))