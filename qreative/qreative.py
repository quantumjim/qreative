# coding: utf-8

# Aug 2018 version: Copyright © 2018 James Wootton, University of Basel
# Later versions:   Copyright © 2018 IBM Research

from qiskit import ClassicalRegister, QuantumRegister, QuantumCircuit, execute, Aer, IBMQ
from qiskit.providers.aer.noise import NoiseModel
from qiskit.providers.aer.noise.errors import pauli_error, depolarizing_error

import numpy as np
import random
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
import copy
import networkx as nx
from pydub import AudioSegment

try:
    IBMQ.load_accounts()
except:
    print("You'll need to set up an IBMQ account to access anything but local simulators. See\n    https://github.com/Qiskit/qiskit-tutorials/blob/master/INSTALL.md\nfor details on how to get an account and register the credentials.")

def get_backend(device):
    """Returns backend object for device specified by input string."""
    try:
        backend = Aer.get_backend(device)
    except:
        backend = IBMQ.get_backend(device)
    return backend

def get_noise(noisy):
    """Returns a noise model when input is not False or None.
    A string will be interpreted as the name of a backend, and the noise model of this will be extracted.
    A float will be interpreted as an error probability for a depolarizing+measurement error model.
    Anything else (such as True) will give the depolarizing+measurement error model with default error probabilities."""
    if noisy:
        
        if type(noisy) is str:
            device = get_backend(noisy)
            noise_model = noise.device.basic_device_noise_model( device.properties() )
        else:
            if type(noisy) is float:
                p_meas = noisy
                p_gate1 = noisy
            else:
                p_meas = 0.08
                p_gate1 = 0.04

            error_meas = pauli_error([('X',p_meas), ('I', 1 - p_meas)])
            error_gate1 = depolarizing_error(p_gate1, 1)
            error_gate2 = error_gate1.kron(error_gate1)

            noise_model = NoiseModel()
            noise_model.add_all_qubit_quantum_error(error_meas, "measure")
            noise_model.add_all_qubit_quantum_error(error_gate1, ["u1", "u2", "u3"])
            noise_model.add_all_qubit_quantum_error(error_gate2, ["cx"])
            
    else:
        noise_model = None
    return noise_model
    
class ladder:
    """An integer implemented on a single qubit. Addition and subtraction are implemented via partial NOT gates."""
    
    def __init__(self,d):
        """Create a new ladder object. This has the attribute `value`, which is an int that can be 0 at minimum and the supplied value `d` at maximum. This value is initialized to 0."""
        self.d = d
        self.qr = QuantumRegister(1)
        self.cr = ClassicalRegister(1)
        self.qc = QuantumCircuit(self.qr, self.cr)
        
    def add(self,delta):
        """Changes value of ladder object by the given amount `delta`. This is initially done by addition, but it changes to subtraction once the maximum value of `d` is reached. It will then change back to addition once 0 is reached, and so on.
        
        delta = Amount by which to change the value of the ladder object. Can be int or float."""
        self.qc.rx(np.pi*delta/self.d,self.qr[0])
        
    def value(self,device='qasm_simulator',noisy=False,shots=1024):
        """Returns the current version of the ladder operator as an int. If floats have been added to this value, the sum of all floats added thus far are rounded.
        
        device = A string specifying a backend. The noisy behaviour from a real device will result in some randomness in the value given, and can lead to the reported value being less than the true value on average. These effects will be more evident for high `d`.
        shots = Number of shots used when extracting results from the qubit. A low value will result in randomness in the value given. This should be neglible when the value is a few orders of magnitude greater than `d`. """  
        temp_qc = copy.deepcopy(self.qc)
        temp_qc.barrier(self.qr)
        temp_qc.measure(self.qr,self.cr)
        try:
            job = execute(temp_qc,backend=get_backend(device),noise_model=get_noise(noisy),shots=shots)
        except:
            job = execute(temp_qc,backend=get_backend(device),shots=shots)
        if '1' in job.result().get_counts():
            p = job.result().get_counts()['1']/shots
        else:
            p = 0
        delta = round(2*np.arcsin(np.sqrt(p))*self.d/np.pi)
        return int(delta)

    
class twobit:
    """An object that can store a single boolean value, but can do so in two incompatible ways. It is implemented on a single qubit using two complementary measurement bases."""
    
    def __init__(self):
        """Create a twobit object, initialized to give a random boolean value for both measurement types."""
        self.qr = QuantumRegister(1)
        self.cr = ClassicalRegister(1)
        self.qc = QuantumCircuit(self.qr, self.cr)
        self.prepare({'Y':None})
        
    def prepare(self,state):
        """Supplying `state={basis,b}` prepares a twobit with the boolean `b` stored using the measurement type specified by `basis` (which can be 'X', 'Y' or 'Z').
        
        Note that `basis='Y'` (and arbitrary `b`) will result in the twobit giving a random result for both 'X' and 'Z' (and similarly for any one versus the remaining two). """
        self.qc = QuantumCircuit(self.qr, self.cr)
        if 'Y' in state:
            self.qc.h(self.qr[0])
            if state['Y']:
                self.qc.sdg(self.qr[0])
            else:
                self.qc.s(self.qr[0])
        elif 'X' in state:
            if state['X']:
                self.qc.x(self.qr[0])
            self.qc.h(self.qr[0])
        elif 'Z' in state:
            if state['Z']:
                self.qc.x(self.qr[0])
                
    def value (self,basis,device='qasm_simulator',noisy=False,shots=1024,mitigate=True):
        """Extracts the boolean value for the given measurement type. The twobit is also reinitialized to ensure that the same value would if the same call to `measure()` was repeated.
        
        basis = 'X' or 'Z', specifying the desired measurement type.
        device = A string specifying a backend. The noisy behaviour from a real device will result in some randomness in the value given, even if it has been set to a definite value for a given measurement type. This effect can be reduced using `mitigate=True`.
        shots = Number of shots used when extracting results from the qubit. A value of greater than 1 only has any effect for `mitigate=True`, in which case larger values of `shots` allow for better mitigation.
        mitigate = Boolean specifying whether mitigation should be applied. If so the values obtained over `shots` samples are considered, and the fraction which output `True` is calculated. If this is more than 90%, measure will return `True`. If less than 10%, it will return `False`, otherwise it returns a random value using the fraction as the probability."""
        if basis=='X':
            self.qc.h(self.qr[0])
        elif basis=='Y':
            self.qc.sdg(self.qr[0])
            self.qc.h(self.qr[0])
        self.qc.barrier(self.qr)
        self.qc.measure(self.qr,self.cr)
        try:
            job = execute(self.qc, backend=get_backend(device), noise_model=get_noise(noisy), shots=shots)
        except:
            job = execute(self.qc, backend=get_backend(device), shots=shots)
        stats = job.result().get_counts()
        if '1' in stats:
            p = stats['1']/shots
        else:
            p = 0
        if mitigate:
            if p<0.1:
                p = 0
            elif p>0.9:
                p = 1
        measured_value = ( p>random.random() )
        self.prepare({basis:measured_value})
        
        return measured_value

    def X_value (self,device='qasm_simulator',noisy=False,shots=1024,mitigate=True):
        """Extracts the boolean value via the X basis. For details of kwargs, see `value()`."""
        return self.value('X',device=device,noisy=noisy,shots=shots,mitigate=mitigate)

    def Y_value (self,device='qasm_simulator',noisy=False,shots=1024,mitigate=True):
        """Extracts the boolean value via the X basis. For details of kwargs, see `value()`."""
        return self.value('Y',device=device,noisy=noisy,shots=shots,mitigate=mitigate)
        
    def Z_value (self,device='qasm_simulator',noisy=False,shots=1024,mitigate=True):
        """Extracts the boolean value via the X basis. For details of kwargs, see `value()`."""
        return self.value('Z',device=device,noisy=noisy,shots=shots,mitigate=mitigate)
    
        
def bell_correlation (basis,device='qasm_simulator',noisy=False,shots=1024):
    """Prepares a rotated Bell state of two qubits. Measurement is done in the specified basis for each qubit. The fraction of results for which the two qubits agree is returned.
    
    basis = String specifying measurement bases. 'XX' denotes X measurement on each qubit, 'XZ' denotes X measurement on qubit 0 and Z on qubit 1, vice-versa for 'ZX', and 'ZZ' denotes 'Z' measurement on both.
    device = A string specifying a backend. The noisy behaviour from a real device will result in the correlations being less strong than in the ideal case.
    shots = Number of shots used when extracting results from the qubit. For shots=1, the returned value will randomly be 0 (if the results for the two qubits disagree) or 1 (if they agree). For large shots, the returned value will be probability for this random process.
    """
    qr = QuantumRegister(2)
    cr = ClassicalRegister(2)
    qc = QuantumCircuit(qr,cr)

    qc.h( qr[0] )
    qc.cx( qr[0], qr[1] )
    qc.ry( np.pi/4, qr[1])
    qc.h( qr[1] )
    #qc.x( qr[0] )
    #qc.z( qr[0] )
    
    for j in range(2):
        if basis[j]=='X':
            qc.h(qr[j])

    qc.barrier(qr)
    qc.measure(qr,cr)
    
    try:
        job = execute(qc, backend=get_backend(device), noise_model=get_noise(noisy), shots=shots, memory=True)
    except:
        job = execute(qc, backend=get_backend(device), shots=shots, memory=True)
    stats = job.result().get_counts()
    
    P = 0
    for string in stats:
        p = stats[string]/shots
        if string in ['00','11']:
            P += p
            
    return {'P':P, 'samples':job.result().get_memory() }

def bitstring_superposer (strings,bias=0.5,device='qasm_simulator',noisy=False,shots=1024):
    """Prepares the superposition of the two given n bit strings. The number of qubits used is equal to the length of the string. The superposition is measured, and the process repeated many times. A dictionary with the fraction of shots for which each string occurred is returned.
    
    string = List of two binary strings. If the list has more than two elements, all but the first two are ignored.
    device = A string specifying a backend. The noisy behaviour from a real device will result in strings other than the two supplied occuring with non-zero fraction.
    shots = Number of times the process is repeated to calculate the fractions. For shots=1, only a single randomnly generated bit string is return (as the key of a dict)."""
    
    # make it so that the input is a list of list of strings, even if it was just a list of strings
    strings_list = []
    if type(strings[0])==str:
        strings_list = [strings]
    else:
        strings_list = strings
    
    batch = []
    for strings in strings_list:
        
        # find the length of the longest string, and pad any that are shorter
        num = 0
        for string in strings:
            num = max(len(string),num)
        for string in strings:
            string = '0'*(num-len(string)) + string
        
        qr = QuantumRegister(num)
        cr = ClassicalRegister(num)
        qc = QuantumCircuit(qr,cr)

        if len(strings)==2**num: # create equal superposition of all if all are asked for
            for n in range(num):
                qc.h(qr[n])
        else: # create superposition of just two
            diff = []
            for bit in range(num):
                if strings[0][bit]==strings[1][bit]:
                    if strings[0][bit]=='1':
                        qc.x(qr[bit])
                if strings[0][bit]!=strings[1][bit]:
                    diff.append(bit)
            if diff:
                frac = np.arccos(np.sqrt(bias))/(np.pi/2)
                qc.rx(np.pi*frac,qr[diff[0]])
                for bit in diff[1:]:
                    qc.cx(qr[diff[0]],qr[bit])
                for bit in diff:
                    if strings[0][bit]=='1':
                        qc.x(qr[bit])

        qc.barrier(qr)
        qc.measure(qr,cr)
        
        batch.append(qc)

    try:
        job = execute(batch, backend=get_backend(device), noise_model=get_noise(noisy), shots=shots)
    except:
        job = execute(batch, backend=get_backend(device), shots=shots)
    stats_raw_list = []
    for j in range(len(strings_list)):
        stats_raw_list.append( job.result().get_counts(batch[j]) )

    stats_list = []
    for stats_raw in stats_raw_list:
        stats = {}
        for string in stats_raw:
            stats[string[::-1]] = stats_raw[string]/shots
        stats_list.append(stats)
    
    # if only one instance was given, output dict rather than list with a single dict
    if len(stats_list)==1:
        stats_list = stats_list[0]

    return stats_list
    
def emoticon_superposer (emoticons,bias=0.5,device='qasm_simulator',noisy=False,shots=1024,figsize=(20,20),encoding=7):
    """Creates superposition of two emoticons.
    
    A dictionary is returned, which supplies the relative strength of each pair of ascii characters in the superposition. An image representing the superposition, with each pair of ascii characters appearing with an weight that represents their strength in the superposition, is also created.
    
    emoticons = A list of two strings, each of which is composed of two ascii characters, such as [ ";)" , "8)" ].
    device = A string specifying a backend. The noisy behaviour from a real device will result in emoticons other than the two supplied occuring with non-zero strength.
    shots = Number of times the process is repeated to calculate the fractions used as strengths. For shots=1, only a single randomnly generated emoticon is return (as the key of the dict).
    emcoding = Number of bits used to encode ascii characters."""
    
    # make it so that the input is a list of list of strings, even if it was just a list of strings
    if type(emoticons[0])==str:
        emoticons_list = [emoticons]
    else:
        emoticons_list = emoticons
        
    strings = []
    for emoticons in emoticons_list:
        string = []
        for emoticon in emoticons:
            bin4emoticon = ""
            for character in emoticon:
                bin4char = bin(ord(character))[2:]
                bin4char = (encoding-len(bin4char))*'0'+bin4char
                bin4emoticon += bin4char
            string.append(bin4emoticon)
        strings.append(string)
        
    stats = bitstring_superposer(strings,bias=bias,device=device,noisy=noisy,shots=shots)
    
    # make a list of dicts from stats
    if type(stats) is dict:
        stats_list = [stats]
    else:
        stats_list = stats
        
    ascii_stats_list = []
    for stats in stats_list:
        fig = plt.figure()
        ax=fig.add_subplot(111)
        plt.rc('font', family='monospace')
        ascii_stats = {}
        for string in stats:
            char = chr(int( string[0:encoding] ,2)) # get string of the leftmost bits and convert to an ASCII character
            char += chr(int( string[encoding:2*encoding] ,2)) # do the same for string of rightmost bits, and add it to the previous character
            prob = stats[string] # fraction of shots for which this result occurred
            ascii_stats[char] = prob
            # create plot with all characters on top of each other with alpha given by how often it turned up in the output
            try:
                plt.annotate( char, (0.5,0.5), va="center", ha="center", color = (0,0,0, prob ), size = 300)
            except:
                pass
        ascii_stats_list.append(ascii_stats)

        plt.axis('off')
        plt.show()
    
    # if only one instance was given, output dict rather than list with a single dict
    if len(ascii_stats_list)==1:
        ascii_stats_list = ascii_stats_list[0]
    
    return ascii_stats_list


def _filename_superposer (all_files,files,bias,device,noisy,shots):
    """Takes a list of all possible filenames (all_files) as well as a pair to be superposed or list of such pairs (files) and superposes them for a given bias and number of shots on a given device. Output is a dictionary will filenames as keys and the corresponding fractions of shots as target.""" 

    file_num = len(all_files)
    bit_num = int(np.ceil( np.log2(file_num) ))
    all_files += [None]*(2**bit_num-file_num)
    
    # make it so that the input is a list of list of strings, even if it was just a list of strings
    if type(files[0])==str:
        files_list = [files]
    else:
        files_list = files
    
    strings = []
    for files in files_list:
        string = []
        for file in files:
            bin4pic = "{0:b}".format(all_files.index(file))
            bin4pic = '0'*(bit_num-len(bin4pic)) + bin4pic
            string.append( bin4pic )
        strings.append(string)
    
    full_stats = bitstring_superposer(strings,bias=bias,device=device,noisy=noisy,shots=shots)
        
    # make a list of dicts from stats
    if type(full_stats) is dict:
        full_stats_list = [full_stats]
    else:
        full_stats_list = full_stats
        
    stats_list = []
    for full_stats in full_stats_list:
        Z = 0
        for j in range(file_num):
            string = "{0:b}".format(j)
            string = '0'*(bit_num-len(string)) + string
            if string in full_stats:
                Z += full_stats[string]    
        stats = {}
        for j in range(file_num):
            string = "{0:b}".format(j)
            string = '0'*(bit_num-len(string)) + string
            if string in full_stats:
                stats[string] = full_stats[string]/Z
        stats_list.append(stats)
        
    file_stats_list = []
    for stats in stats_list:
        file_stats = {}
        for string in stats:
            file_stats[ all_files[int(string,2)] ] = stats[string]
        file_stats_list.append(file_stats)
    
    return  file_stats_list


def image_superposer (all_images,images,bias=0.5,device='qasm_simulator',noisy=False,shots=1024,figsize=(20,20)):
    """Creates superposition of two images from a set of images.
    
    A dictionary is returned, which supplies the relative strength of each pair of ascii characters in the superposition. An image representing the superposition, with each of the original images appearing with an weight that represents their strength in the superposition, is also created.
    
    all_images = List of strings that are filenames for a set of images.  The files should be located in 'images/<filename>.png relative to where the code is executed.
    images = List of strings for image files to be superposed. This can either contain the strings for two files, or for all in all_images. Other options are not currently supported.
    device = A string specifying a backend. The noisy behaviour from a real device will result in images other than those intended appearing with non-zero strength.
    shots = Number of times the process is repeated to calculate the fractions used as strengths."""

    image_stats_list = _filename_superposer (all_images,images,bias,device,noise,shots)
    print(image_stats_list)
    
    for image_stats in image_stats_list:  
        # sort from least to most likely and create corresponding lists of the strings and fractions
        sorted_strings = sorted(image_stats,key=image_stats.get)
        sorted_fracs = sorted(image_stats.values())
        n = len(image_stats)
        # construct alpha values such that the final image is a weighted average of the images specified by the keys of `image_stats`
        alpha = [ sorted_fracs[0] ]
        for j in range(0,n-1):
            alpha.append( ( alpha[j]/(1-alpha[j]) ) * ( sorted_fracs[j+1] / sorted_fracs[j] ) )

        fig, ax = plt.subplots(figsize=figsize)
        for j in reversed(range(n)):
            filename = sorted_strings[j]
            if filename:
                image = plt.imread( "images/"+filename+".png" )
                plt.imshow(image,alpha=alpha[j])
        plt.axis('off')
        plt.show()
    
    # if only one instance was given, output dict rather than list with a single dict
    if len(image_stats_list)==1:
        image_stats_list = image_stats_list[0]
    
    return image_stats_list

def audio_superposer (all_audio,audio,bias=0.5,device='qasm_simulator',noisy=False,shots=1024,format='wav'):
    
    audio_stats_list = _filename_superposer (all_audio,audio,bias,device,noisy,shots)
    
    for audio_stats in audio_stats_list:
        loudest = max(audio_stats, key=audio_stats.get)
        mixed = AudioSegment.from_wav('audio/'+loudest+'.'+format)
        for filename in audio_stats:
            if filename != loudest:
                dBFS = np.log10( audio_stats[filename]/audio_stats[loudest] )
                file = AudioSegment.from_wav('audio/'+filename+'.'+format) - dBFS
                mixed = mixed.overlay(file)
        mixed.export('outputs/audio_'+'_'.join(audio)+'.'+format, format=format) 
    
    return audio_stats_list


class layout:
    """Processing and display of data in ways that depend on the layout of a quantum device."""
    
    def __init__(self,device):
        """Given a device, specified by
        
        device = A string specifying a device, or a list of two integers to define a grid.
        
        the following attributes are determined.
        
        num = Number of qubits on the device.
        pairs = Dictionary detailing the pairs of qubits for which cnot gates can be directly implemented. Each value is a list of two qubits for which this is possible. The corresponding key is a string that is used as the name of the pair.
        pos = A dictionary of positions for qubits, to be used in plots.
        """
        if device in ['ibmq_5_tenerife', 'ibmq_16_melbourne']:
                        
            backend = get_backend(device)
            self.num = backend.configuration().n_qubits
            coupling = backend.configuration().coupling_map
            self.pairs = {}
            char = 65
            for pair in coupling:
                self.pairs[chr(char)] = pair
                char += 1
            if device in ['ibmq_5_tenerife']:
                self.pos = { 0: [1,1], 1: [1,0], 2: [0.5,0.5], 3: [0,0], 4: [0,1] }        
            elif device=='ibmq_16_rueschlikon':
                self.pos = { 0: [0,0], 1: [0,1],  2: [1,1],  3: [2,1],  4: [3,1],  5: [4,1],  6: [5,1],  7: [6,1],
8: [7,1], 9: [7,0], 10: [6,0], 11: [5,0], 12: [4,0], 13: [3,0], 14: [2,0], 15: [1,0] }
            elif device=='ibmq_16_melbourne':
                self.pos = { 0: (0,1), 1: (1,1),  2: (2,1),  3: (3,1),  4: (4,1),  5: (5,1),  6: (6,1),
                7: (7,0), 8: (6,0), 9: (5,0), 10: (4,0), 11: (3,0), 12: (2,0), 13: (1,0) }
            
        elif type(device) is list:
            
            Lx = device[0]
            Ly = device[1]
            self.num = Lx*Ly
            self.pairs = {}
            char = 65
            for x in range(Lx-1):
                for y in range(Ly):
                    n = x + y*Ly
                    m = n+1
                    self.pairs[chr(char)] = [n,m]
                    char += 1
            for x in range(Lx):
                for y in range(Ly-1):
                    n = x + y*Ly
                    m = n+Ly
                    self.pairs[chr(char)] = [n,m]
                    char += 1
            self.pos = {}
            for x in range(Lx):
                for y in range(Ly):
                    n = x + y*Ly
                    self.pos[n] = [x,y]
        else:
                
            print("Error: Device not recognized.\nMake sure it is a list of two integers (to specify a grid) or one of the supported IBM devices ('ibmqx2', 'ibmqx4' and 'ibmqx5').")
        
        for pair in self.pairs:
            self.pos[pair] = [(self.pos[self.pairs[pair][0]][j] + self.pos[self.pairs[pair][1]][j])/2 for j in range(2)]
  
    def calculate_probs(self,raw_stats):
        """Given a counts dictionary as the input `raw_stats`, a dictionary of probabilities is returned. The keys for these are either integers (referring to qubits) or strings (referring to pairs of neighbouring qubits). For the qubit entries, the corresponding value is the probability that the qubit is in state `1`. For the pair entries, the values are the probabilities that the two qubits disagree (so either the outcome `01` or `10`."""
        Z = 0
        for string in raw_stats:
            Z += raw_stats[string]
        stats = {}
        for string in raw_stats:
            stats[string] = raw_stats[string]/Z
        
        probs = {}
        for n in self.pos:
            probs[n] = 0
        
        for string in stats:
            for n in range(self.num):
                if string[-n-1]=='1':
                    probs[n] += stats[string]
            for pair in self.pairs: 
                if string[-self.pairs[pair][0]-1]!=string[-self.pairs[pair][1]-1]:
                    probs[pair] += stats[string]
            
        return probs
                    
    def plot(self,probs={},labels={},colors={},sizes={}):
        """An image representing the device is created and displayed.
        
        When no kwargs are supplied, qubits are labelled according to their numbers. The pairs of qubits for which a cnot is possible are shown by lines connecting the qubitsm, and are labelled with letters.
        
        The kwargs should all be supplied in the form of dictionaries for which qubit numbers and pair labels are the keys (i.e., the same keys as for the `pos` attribute).
        
        If `probs` is supplied (such as from the output of the `calculate_probs()` method, the labels, colors and sizes of qubits and pairs will be determined by these probabilities. Otherwise, the other kwargs set these properties directly."""                
        G=nx.Graph()
        
        for pair in self.pairs:
            G.add_edge(self.pairs[pair][0],self.pairs[pair][1])
            G.add_edge(self.pairs[pair][0],pair)
            G.add_edge(self.pairs[pair][1],pair)
        
        if probs:
            
            label_changes = copy.deepcopy(labels)
            color_changes = copy.deepcopy(colors)
            size_changes = copy.deepcopy(sizes)
            
            labels = {}
            colors = {}
            sizes = {}
            for node in G:
                if probs[node]>1:
                    labels[node] = ""
                    colors[node] = 'grey'
                    sizes[node] = 3000
                else:
                    labels[node] = "%.0f" % ( 100 * ( probs[node] ) )
                    colors[node] =( 1-probs[node],0,probs[node] )
                    if type(node)!=str:
                        if labels[node]=='0':
                            sizes[node] = 3000
                        else:
                            sizes[node] = 4000 
                    else:
                        if labels[node]=='0':
                            sizes[node] = 800
                        else:
                            sizes[node] = 1150
                                         
            for node in label_changes:
                labels[node] = label_changes[node]
            for node in color_changes:
                colors[node] = color_changes[node]      
            for node in size_changes:
                sizes[node] = size_changes[node]                   
                                        
        else:
            if not labels:
                labels = {}
                for node in G:
                    labels[node] = node
            if not colors:
                colors = {}
                for node in G:
                    if type(node) is int:
                        colors[node] = (node/self.num,0,1-node/self.num)
                    else:
                        colors[node] = (0,0,0)
            if not sizes:
                sizes = {}
                for node in G:
                    if type(node)!=str:
                        sizes[node] = 3000
                    else:
                        sizes[node] = 750

        # convert to lists, which is required by nx
        color_list = []
        size_list = []
        for node in G:
            color_list.append(colors[node])
            size_list.append(sizes[node])
        
        area = [0,0]
        for coord in self.pos.values():
            for j in range(2):
                area[j] = max(area[j],coord[j])
        for j in range(2):
            area[j] = (area[j] + 1 )*1.1
            
        if area[0]>2*area[1]:
            ratio = 0.65
        else:
            ratio = 1

        plt.figure(2,figsize=(2*area[0],2*ratio*area[1])) 
        nx.draw(G, self.pos, node_color = color_list, node_size = size_list, labels = labels, with_labels = True,
                font_color ='w', font_size = 18)
        plt.show() 
        
class pauli_grid():
    # Allows a quantum circuit to be created, modified and implemented, and visualizes the output in the style of 'Hello Quantum'.

    def __init__(self,device='qasm_simulator',noisy=False,shots=1024,mode='circle',y_boxes=False):
        """
        device='qasm_simulator'
            Backend to be used by Qiskit to calculate expectation values (defaults to local simulator).
        shots=1024
            Number of shots used to to calculate expectation values.
        mode='circle'
            Either the standard 'Hello Quantum' visualization can be used (with mode='circle') or the alternative line based one (mode='line').
        y_boxes=True
            Whether to display full grid that includes Y expectation values.
        """
        
        self.backend = get_backend(device)
        self.noise_model = get_noise(noisy)
        self.shots = shots
        
        self.y_boxes = y_boxes
        if self.y_boxes:
            self.box = {'ZI':(-1, 2),'XI':(-3, 4),'IZ':( 1, 2),'IX':( 3, 4),'ZZ':( 0, 3),'ZX':( 2, 5),'XZ':(-2, 5),'XX':( 0, 7),
                        'YY':(0,5), 'YI':(-2,3), 'IY':(2,3), 'YZ':(-1,4), 'ZY':(1,4), 'YX':(1,6), 'XY':(-1,6) }
        else:
            self.box = {'ZI':(-1, 2),'XI':(-2, 3),'IZ':( 1, 2),'IX':( 2, 3),'ZZ':( 0, 3),'ZX':( 1, 4),'XZ':(-1, 4),'XX':( 0, 5)}
        
        self.rho = {}
        for pauli in self.box:
            self.rho[pauli] = 0.0
        for pauli in ['ZI','IZ','ZZ']:
            self.rho[pauli] = 1.0
            
        self.qr = QuantumRegister(2)
        self.cr = ClassicalRegister(2)
        self.qc = QuantumCircuit(self.qr, self.cr)
        
        self.mode = mode
        # colors are background, qubit circles and correlation circles, respectively
        if self.mode=='line':
            self.colors = [(1.6/255,72/255,138/255),(132/255,177/255,236/255),(33/255,114/255,216/255)]
        else:
            self.colors = [(1.6/255,72/255,138/255),(132/255,177/255,236/255),(33/255,114/255,216/255)]
        
        self.fig = plt.figure(figsize=(5,5),facecolor=self.colors[0])
        self.ax = self.fig.add_subplot(111)
        plt.axis('off')
        
        self.bottom = self.ax.text(-3,1,"",size=9,va='top',color='w')
        
        self.lines = {}
        for pauli in self.box:
            w = plt.plot( [self.box[pauli][0],self.box[pauli][0]], [self.box[pauli][1],self.box[pauli][1]], color=(1.0,1.0,1.0), lw=0 )
            b = plt.plot( [self.box[pauli][0],self.box[pauli][0]], [self.box[pauli][1],self.box[pauli][1]], color=(0.0,0.0,0.0), lw=0 )
            c = {}
            c['w'] = self.ax.add_patch( Circle(self.box[pauli], 0.0, color=(0,0,0), zorder=10) )
            c['b'] = self.ax.add_patch( Circle(self.box[pauli], 0.0, color=(1,1,1), zorder=10) )
            self.lines[pauli] = {'w':w,'b':b,'c':c}
                         
    
    def get_rho(self):
        # Runs the circuit specified by self.qc and determines the expectation values for 'ZI', 'IZ', 'ZZ', 'XI', 'IX', 'XX', 'ZX' and 'XZ' (and the ones with Ys too if needed).
        
        if self.y_boxes:
            corr = ['ZZ','ZX','XZ','XX','YY','YX','YZ','XY','ZY']
            ps = ['X','Y','Z']
        else:
            corr = ['ZZ','ZX','XZ','XX']
            ps = ['X','Z']
        
        results = {}
        for basis in corr:
            temp_qc = copy.deepcopy(self.qc)
            for j in range(2):
                if basis[j]=='X':
                    temp_qc.h(self.qr[j])
                elif basis[j]=='Y':
                    temp_qc.sdg(self.qr[j])
                    temp_qc.h(self.qr[j])
            temp_qc.barrier(self.qr)
            temp_qc.measure(self.qr,self.cr)
            try:
                job = execute(temp_qc, backend=self.backend, noise_model=self.noise_model, shots=self.shots)
            except:
                job = execute(temp_qc, backend=self.backend, shots=self.shots)
            results[basis] = job.result().get_counts()
            for string in results[basis]:
                results[basis][string] = results[basis][string]/self.shots

        prob = {}
        # prob of expectation value -1 for single qubit observables
        for j in range(2):
            
            for p in ps:
                pauli = {}
                for pp in ['I']+ps:
                    pauli[pp] = (j==1)*pp + p + (j==0)*pp
                prob[pauli['I']] = 0
                for ppp in ps:
                    basis = pauli[ppp]
                    for string in results[basis]:
                        if string[(j+1)%2]=='1':
                            prob[pauli['I']] += results[basis][string]/(2+self.y_boxes)
        
        # prob of expectation value -1 for two qubit observables
        for basis in corr:
            prob[basis] = 0
            for string in results[basis]:
                if string[0]!=string[1]:
                    prob[basis] += results[basis][string]

        for pauli in prob:
            self.rho[pauli] = 1-2*prob[pauli]
    
    def update_grid(self,rho=None,labels=False,bloch=None,hidden=[],qubit=True,corr=True,message=""):
        """
        rho = None
            Dictionary of expectation values for 'ZI', 'IZ', 'ZZ', 'XI', 'IX', 'XX', 'ZX' and 'XZ'. If supplied, this will be visualized instead of the results of running self.qc.
        labels = False
            Determines whether basis labels are printed in the corresponding boxes.
        bloch = None
            If a qubit name is supplied, and if mode='line', Bloch circles are displayed for this qubit
        hidden = []
            Which qubits have their circles hidden (empty list if both shown).
        qubit = True
            Whether both circles shown for each qubit (use True for qubit puzzles and False for bit puzzles).
        corr = True
            Whether the correlation circles (the four in the middle) are shown.
        message
            A string of text that is displayed below the grid.
        """

        def see_if_unhidden(pauli):
            # For a given Pauli, see whether its circle should be shown.
            
            unhidden = True
            # first: does it act non-trivially on a qubit in `hidden`
            for j in hidden:
                unhidden = unhidden and (pauli[j]=='I')
            # second: does it contain something other than 'I' or 'Z' when only bits are shown
            if qubit==False:
                for j in range(2):
                    unhidden = unhidden and (pauli[j] in ['I','Z'])
            # third: is it a correlation pauli when these are not allowed
            if corr==False:
                unhidden = unhidden and ((pauli[0]=='I') or (pauli[1]=='I'))
            return unhidden

        def add_line(line,pauli_pos,pauli):
            """
            For mode='line', add in the line.
            
            line = the type of line to be drawn (X, Z or the other one)
            pauli = the box where the line is to be drawn
            expect = the expectation value that determines its length
            """
            
            unhidden = see_if_unhidden(pauli)
            coord = None
            p = (1-self.rho[pauli])/2 # prob of 1 output
            # in the following, white lines goes from a to b, and black from b to c
            if unhidden:
                if line=='Z':
                    a = ( self.box[pauli_pos][0], self.box[pauli_pos][1]+l/2 )
                    c = ( self.box[pauli_pos][0], self.box[pauli_pos][1]-l/2 )
                    b = ( (1-p)*a[0] + p*c[0] , (1-p)*a[1] + p*c[1] )
                    lw = 8
                    coord = (b[1] - (a[1]+c[1])/2)*1.2 + (a[1]+c[1])/2
                elif line=='X':
                    a = ( self.box[pauli_pos][0]+l/2, self.box[pauli_pos][1] )
                    c = ( self.box[pauli_pos][0]-l/2, self.box[pauli_pos][1] )
                    b = ( (1-p)*a[0] + p*c[0] , (1-p)*a[1] + p*c[1] )
                    lw = 9
                    coord = (b[0] - (a[0]+c[0])/2)*1.1 + (a[0]+c[0])/2
                else:
                    a = ( self.box[pauli_pos][0]+l/(2*np.sqrt(2)), self.box[pauli_pos][1]+l/(2*np.sqrt(2)) )
                    c = ( self.box[pauli_pos][0]-l/(2*np.sqrt(2)), self.box[pauli_pos][1]-l/(2*np.sqrt(2)) )
                    b = ( (1-p)*a[0] + p*c[0] , (1-p)*a[1] + p*c[1] )
                    lw = 9
                self.lines[pauli]['w'].pop(0).remove()
                self.lines[pauli]['b'].pop(0).remove()
                self.lines[pauli]['w'] = plt.plot( [a[0],b[0]], [a[1],b[1]], color=(1.0,1.0,1.0), lw=lw )
                self.lines[pauli]['b'] = plt.plot( [b[0],c[0]], [b[1],c[1]], color=(0.0,0.0,0.0), lw=lw )
                return coord
        
        l = 0.9 # line length
        r = 0.6 # circle radius
        L = 0.98*np.sqrt(2) # box height and width
        
        if rho==None:
            self.get_rho()

        # draw boxes
        for pauli in self.box:
            if 'I' in pauli:
                color = self.colors[1]
            else:
                color = self.colors[2]
            self.ax.add_patch( Rectangle( (self.box[pauli][0],self.box[pauli][1]-1), L, L, angle=45, color=color) )  

        # draw circles
        for pauli in self.box:
            unhidden = see_if_unhidden(pauli)
            if unhidden:
                if self.mode=='line':
                    self.ax.add_patch( Circle(self.box[pauli], r, color=(0.5,0.5,0.5)) )
                else:
                    prob = (1-self.rho[pauli])/2
                    self.ax.add_patch( Circle(self.box[pauli], r, color=(prob,prob,prob)) )

        # update bars if required
        if self.mode=='line':
            if bloch in ['0','1']:
                for other in 'IXZ':
                    px = other*(bloch=='1') + 'X' + other*(bloch=='0')
                    pz = other*(bloch=='1') + 'Z' + other*(bloch=='0')
                    z_coord = add_line('Z',pz,pz)
                    x_coord = add_line('X',pz,px)
                    for j in self.lines[pz]['c']:
                        self.lines[pz]['c'][j].center = (x_coord,z_coord)
                        self.lines[pz]['c'][j].radius = (j=='w')*0.05 + (j=='b')*0.04
                px = 'I'*(bloch=='0') + 'X' + 'I'*(bloch=='1')
                pz = 'I'*(bloch=='0') + 'Z' + 'I'*(bloch=='1')
                add_line('Z',pz,pz)
                add_line('X',px,px)
            else:
                for pauli in self.box:
                    for j in self.lines[pauli]['c']:
                        self.lines[pauli]['c'][j].radius = 0.0
                    if pauli in ['ZI','IZ','ZZ']:
                        add_line('Z',pauli,pauli)
                    if pauli in ['XI','IX','XX']: 
                        add_line('X',pauli,pauli)
                    if pauli in ['XZ','ZX']:
                        add_line('ZX',pauli,pauli)
             
        self.bottom.set_text(message)
        
        if labels:
            for pauli in self.box:
                plt.text(self.box[pauli][0]-0.18,self.box[pauli][1]-0.85, pauli)
        
        if self.y_boxes:
            self.ax.set_xlim([-4,4])
            self.ax.set_ylim([0,8])
        else:
            self.ax.set_xlim([-3,3])
            self.ax.set_ylim([0,6])
        
        self.fig.canvas.draw()
        
        
class qrng ():
    """This object generations `num` strings, each of `precision=8192/num` bits. These are then dispensed one-by-one as random integers, floats, etc, depending on the method called. Once all `num` strings are used, it'll loop back around."""
    def __init__( self, precision=None, num = 1280, sim=True, noisy=False, noise_only=False, verbose=True ):
        
        if precision:
            self.precision = precision
            self.num = int(np.floor( 5*8192/self.precision ))
        else:
            self.num = num
            self.precision = int(np.floor( 5*8192/self.num ))
        
        q = QuantumRegister(5)
        c = ClassicalRegister(5)
        qc = QuantumCircuit(q,c)
        if not noise_only:
            qc.h(q)
        qc.measure(q,c)
        
        if sim:
            backend=Aer.get_backend('qasm_simulator')
        else:
            IBMQ.load_accounts()
            backend=IBMQ.get_backend('ibmq_5_tenerife')
        
        if verbose and not sim:
            print('Sending job to quantum device')
        try:
            job = execute(qc,backend,shots=8192,noise_model=get_noise(noisy),memory=True)
        except:
            job = execute(qc,backend,shots=8192,memory=True)
        data = job.result().get_memory()
        if verbose and not sim:
            print('Results from device received')
        
        full_data = []
        for datum in data:
            full_data += list(datum)
        
        self.int_list = []
        self.bit_list = []
        n = 0
        for _ in range(num):
            bitstring = ''
            for b in range(self.precision):
                bitstring += full_data[n]
                n += 1
            self.bit_list.append(bitstring)
            self.int_list.append( int(bitstring,2) )
            
        self.n = 0
    
    def _iterate(self):
        
        self.n = self.n+1 % self.num
    
    def rand_int(self):
        
        rand_int = self.int_list[self.n]
        
        self._iterate()
        
        return rand_int
    
    def rand(self):
        
        rand_float = self.int_list[self.n] / 2**self.precision
        
        self._iterate()
        
        return rand_float

    
class random_grid ():
    
        def __init__(self,Lx,Ly):
        
            self.Lx = Lx
            self.Ly = Ly
        
            self.qr = QuantumRegister(Lx*Ly)
            self.cr = ClassicalRegister(Lx*Ly)
            self.qc = QuantumCircuit(self.qr,self.cr)
            
        def _address(self,x,y):
            return y*self.Lx + x
        
        def neighbours(self,x,y):
            neighbours = []
            for (xx,yy) in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                if (xx>=0) and (xx<=self.Lx-1) and (yy>=0) and (yy<=self.Ly-1):
                    neighbours.append( (xx,yy) )
            return neighbours
                
        def get_samples(self,device='qasm_simulator',noisy=False,shots=1024):
            
            def separate_string(string):
                string = string[::-1]
                grid = []
                for y in range(self.Ly):
                    line = ''
                    for x in range(self.Lx):
                        line += string[self._address(x,y)]
                    grid.append(line)
                return '\n'.join(grid)
            
            temp_qc = copy.deepcopy(self.qc)
            temp_qc.barrier(self.qr)
            temp_qc.measure(self.qr,self.cr)
            try:
                job = execute(temp_qc,backend=get_backend(device),noise_model=get_noise(noisy),shots=shots,memory=True)
            except:
                job = execute(temp_qc,backend=get_backend(device),shots=shots,memory=True)
            
            try:
                data = job.result().get_memory()
                grid_data = []
                for string in data:
                    grid_data.append(separate_string(string))
            except:
                grid_data = None
                
            stats = job.result().get_counts()
            grid_stats = {}
            for string in stats:
                grid_stats[separate_string(string)] = stats[string]
                
            return grid_stats, grid_data
        
        def NOT (self,coords,frac=1,axis='x'):
            '''Implement an rx or ry on the qubit for the given coords, according to the given fraction (`frac=1` is a NOT gate) and the given axis ('x' or 'y').'''
            if axis=='x':
                self.qc.rx(np.pi*frac,self.qr[self._address(coords[0],coords[1])])
            else:
                self.qc.ry(np.pi*frac,self.qr[self._address(coords[0],coords[1])])
            
        def CNOT (self,ctl,tgt,frac=1,axis='x'):
            '''Controlled version of the `NOT` above'''
            if axis=='y':
                self.qc.sdg(self.qr[self._address(tgt[0],tgt[1])])
            self.qc.h(self.qr[self._address(tgt[0],tgt[1])])
            self.qc.crz(np.pi*frac,self.qr[self._address(ctl[0],ctl[1])],self.qr[self._address(tgt[0],tgt[1])])
            self.qc.h(self.qr[self._address(tgt[0],tgt[1])])
            if axis=='y':
                self.qc.s(self.qr[self._address(tgt[0],tgt[1])])