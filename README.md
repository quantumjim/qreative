# Creative Quantumness [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/quantumjim/qreative/master?filepath=README.ipynb)

The `qreative` package is a set of tools to use quantum computers for creative projects. It is built on the [Qiskit](https://qiskit.org) framework for quantum programming. The jobs created using `qreative` can be run on simulators, or on IBM's prototype quantum processors.

For how to use, see the [tutorials](tutorials/README.md). Here there are guides on all the tools included in the package.

* [`bell_correlation` to explore quantum correlations](tutorials/bell_correlation.ipynb)
* [`ladder` to implement game mechanics based on partial NOT gates](tutorials/ladder.ipynb)
* [`layout` to visualize a quantum processor](tutorials/layout.ipynb)
* [`pauli_grid` to visualize what goes on in a pair of qubits](tutorials/pauli_grid.ipynb)
* [`qrng` for quantum random numbers](tutorials/qrng.ipynb)
* [`random_grid` for procedurally generated grids](tutorials/random_grid.ipynb)
* [An application of `randomn_grid` to make random maps](tutorials/random-maps-with-random_grid.ipynb)
* [`random_mountain` for procedurally generated mountains](tutorials/random_mountain.ipynb)
* [Methods to turn superposition states into images and audio](tutorials/superposers.ipynb)
* [`two_bit` to implement game mechanics based on quantum measurement](tutorials/twobit.ipynb)

In addition to telling you how to use the tools in this package, it also provides guides on the following:

* [How to use real quantum devices with the IBM Q Experience](tutorials/Using-IBM-Q-Experience.ipynb)
* [How to get quantum random numbers from IBM devices via HTTP](tutorials/qrng_with_http.ipynb)

You are encouraged to not just use the qreative tools, but also get inside the code and play around with them. For that reason, our aim is to make the code very well commented to help you understand what it all does. If you have any requests on what to comment better, make a request [here](https://github.com/quantumjim/qreative/issues/new).

If you want to pip install, [download this repository](https://github.com/quantumjim/qreative/archive/master.zip) and unzip to get the 'qreative-master' folder. Then navigate to the folder that contains qreative-master via command line, and run the following

    pip install -e qreative-master
    
    
