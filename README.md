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
    
## Projects on which the current tools are based

The current tools are based on the following projects.

* [Battleships with partial NOT gates](https://medium.com/qiskit/how-to-program-a-quantum-computer-982a9329ed02) inspired `ladder`.
* [Battleships with complementary measurements](https://medium.com/@decodoku/how-to-program-a-quantum-computer-part-2-f0d3eee872fe) inspired `twobit`.
* [Quantum Battleships](https://medium.com/@decodoku/quantum-battleships-the-first-multiplayer-game-for-a-quantum-computer-e4d600ccb3f3) inspired `bell_correlation`.
* [Quantum Emoticons](https://medium.com/qiskit/making-a-quantum-computer-smile-cee86a6fc1de) inspired `emoticon_superposer`.
* [Image Superposer](https://medium.com/qiskit/a-quantum-superposition-of-a-tiger-and-a-bear-b461e3b23908)
 inspired `image_superposer`.
* [Quantum Awesomeness](https://github.com/Qiskit/qiskit-tutorials/blob/master/community/games/quantum_awesomeness.ipynb) inspired `layout`.
* [Audio Superposer](https://github.com/Qiskit/qiskit-tutorials/blob/master/community/hello_world/laurel_or_yanny.ipynb) inspired `audio_superposer`.
* [Hello Qiskit](https://github.com/Qiskit/qiskit-tutorials/blob/master/community/games/Hello_Qiskit.ipynb)
  and [Hello Quantum](http://helloquantum.mybluemix.net/) inspired `pauli_grid`.
* [Quantum Tic-Tac-Toe](https://github.com/Qiskit/qiskit-tutorials/blob/master/community/games/quantum_tic_tac_toe.ipynb)  inspired `random_grid`.
* [Quantum 8-Ball](https://github.com/Qiskit/qiskit-tutorials/blob/master/community/hello_world/quantum_8ball.ipynb)  inspired `qrng`.
* [Quantum Slot Machine](https://github.com/Qiskit/qiskit-tutorials/blob/master/community/games/quantum_slot_machine.ipynb)  inspired `qrng`.

## License Stuff

The qreative package is provided under the [Apache 2.0 license](LICENSE.txt). It uses Qiskit to create quantum programs and run simulations. Qiskit is also provided under the Apache 2.0 license.

Through qreative and Qiskit it is also possible to use real quantum devices and simulators using the IBM Q Experience. This is an optional extra that requires an IBM Q Experience account. Results from this service are provided in accordance with the [IBM Q Experience EULA](https://quantumexperience.ng.bluemix.net/qx/terms).

## Credits

This project was initiated by James Wootton while at the [Condensed Matter and Quantum Computing Theory Group](http://www.quantumtheory.unibas.ch/) of the University of Basel. He continues to develop it while at IBM Research. Contributions are welcome.
