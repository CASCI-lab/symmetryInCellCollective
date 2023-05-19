The repository contains code to run CANA functions on the functions in the Cell Collective, or random functions. It also contains some code to produce plots from the generated data.

To run the data generation code use
```
python data_gen.py
```

This code uses the `argparse` module, so you can use `--help` to see the subcommands and options and what they do. Be sure to install the version of CANA you want to run them on first, as this code does not manage the version.

The code will loop through the list of functions specified, computing prime implicants, then two-symbol symmetry, then two-symbol coverage, and lastly $k_s$. It also computes $k_e$, bias, and checks to see if the function was changed by the TSS.
A timeout can be specified, which will only apply to the portion computing the two-symbol symmetry. If a timeout occurs, the function will still be recorded in the output, but with NaNs for everything not yet computed.
It will export the data as a csv, naming it according to the parameters.

All functions are evaluated, whether they are unique or not. Duplicated functions can be removed in analysis from the csv.

Note that, to implement the timeout, since the newest version of CANA calls a Rust module for two-symbol symmetry calculation, a non-straightforward method had to be used. Since interrupts in external language modules in Python are only handled by Python after return, the external code must either handle the interrupt, or it should be spawned as a process and killed by the OS.
