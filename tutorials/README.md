# Creative Quantumness

The `CreativeQiskit` package is a set of tools to use quantum computers for creative projects. It is built on the [Qiskit](https://qiskit.org) framework for quantum programming. The jobs created using `CreativeQiskit` can be run on simulators, or on IBM's prototype quantum processors.

The tools are based on existing creative projects that have been made so far. They are designed to take the essential quantum part of those projects, and present them it a flexible and reusable way.

## The tools and how to use them

The tools of `CreativeQiskit`, and tutorials for how to use each of them, can be found in the list below.

* [`bell_correlation`](bell_correlation.ipynb)
* [`ladder`](ladder.ipynb)
* [`layout`](layout.ipynb)
* [`pauli_grid`](pauli_grid.ipynb)
* [`qrng`](qrng.ipynb)
* [`random_grid`](random_grid.ipynb)
* The [superposers](superposers.ipynb)
    * `bitstring_superposer`
    * `emoticon_superposer`
    * `image_superposer`
    * `audio_superposer`
* [`twobit`](.ipynb)

Each tool has at least one function that executes a quantum program. These all have the same set of optional arguments, each with a default value.

* `device='qasm_simulator`
* `noisy=False`
* `shots=1024`

The `device` kwarg is a string that specifies the backend on which the program is run. The default value is a local simulator, which can run quantum programs without the need for an IBMQ account. Other possibilities are an HPC simulator (`'ibmq_qasm_simulator'`), a prototype 5 qubit device (`'ibmq_5_tenerife'`) and a prototype 14 qubit device (`'ibmq_16_melbourne'`). All of these are cloud-based resources, and do need an IBMQ account. See [here](https://github.com/Qiskit/qiskit-tutorials/blob/master/INSTALL.md) for how to register, get your API key and save it where Qiskit can find it.

Current prototype devices are imperfect, and any run will encounter errors. The `noisy` kwarg determines whether this noise is also simulated when using the local simulator. The default value `False` means that no noise is simulated. Assigning this a float value, such as `noisy=0.1`, sets up a simple noise model in which the supplied value is used as the probability for certain error events occuring. If a string specifying a prototype device is supplied, such as `noisy='ibmq_16_melbourne'` the noise will mimic that experienced on the prototype device.

Each quantum program can be run multiple times so that the any randomness in the output can be analyzed. The number of repetitions is given by `shots`, which takes the default value 1024 in most cases. The maxmimum value that can be given is 8192.
