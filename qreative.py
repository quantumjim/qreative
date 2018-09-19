# coding: utf-8

# Aug 2018 version: Copyright © 2018 James Wootton, University of Basel
# Later versions:   Copyright © 2018 IBM Research

from qiskit import ClassicalRegister, QuantumRegister, QuantumCircuit, get_backend, available_backends, execute
from qiskit import register

import numpy as np
import random
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
import os
import copy
import networkx as nx

try:
    import sys
    sys.path.append("../") # go to parent dir
    import Qconfig
    qx_config = {
        "APItoken": Qconfig.APItoken,
        "url": Qconfig.config['url']}
    #set api
    register(qx_config['APItoken'], qx_config['url'])
except Exception as e:
    print("Warning: Credentials required for using remote IBMQ devices hae not been set up")

    
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
        
    def value(self,backend='local_qasm_simulator',shots=1024):
        """Returns the current version of the ladder operator as an int. If floats have been added to this value, the sum of all floats added thus far are rounded.
        
        backend = A string specifying a backend. The noisy behaviour from a real device will result in some randomness in the value given, and can lead to the reported value being less than the true value on average. These effects will be more evident for high `d`.
        shots = Number of shots used when extracting results from the qubit. A low value will result in randomness in the value given. This should be neglible when the value is a few orders of magnitude greater than `d`. """  
        temp_qc = copy.deepcopy(self.qc)
        temp_qc.barrier(self.qr)
        temp_qc.measure(self.qr,self.cr)
        job = execute(temp_qc, backend=get_backend(backend), shots=shots)
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
        """Supplying `state={basis,b}` prepares a twobit with the boolean `b` stored using the measurement type specified by `basis` (which can be 'X' or 'Z').
        
        Supplying `basis='Y'` (and arbitrary `b`) will result in the twobit giving a random result for both measurement types. """
        self.qc = QuantumCircuit(self.qr, self.cr)
        if 'Y' in state:
            self.qc.h(self.qr[0])
            self.qc.s(self.qr[0])
        elif 'X' in state:
            if state['X']:
                self.qc.x(self.qr[0])
            self.qc.h(self.qr[0])
        elif 'Z' in state:
            if state['Z']:
                self.qc.x(self.qr[0])
                
    def value (self,basis,backend='local_qasm_simulator',shots=1024,mitigate=True):
        """Extracts the boolean value for the given measurement type. The twobit is also reinitialized to ensure that the same value would if the same call to `measure()` was repeated.
        
        basis = 'X' or 'Z', specifying the desired measurement type.
        backend = A string specifying a backend. The noisy behaviour from a real device will result in some randomness in the value given, even if it has been set to a definite value for a given measurement type. This effect can be reduced using `mitigate=True`.
        shots = Number of shots used when extracting results from the qubit. A value of greater than 1 only has any effect for `mitigate=True`, in which case larger values of `shots` allow for better mitigation.
        mitigate = Boolean specifying whether mitigation should be applied. If so the values obtained over `shots` samples are considered, and the fraction which output `True` is calculated. If this is more than 90%, measure will return `True`. If less than 10%, it will return `False`, otherwise it returns a random value using the fraction as the probability."""
        if basis=='X':
            self.qc.h(self.qr[0])
        self.qc.barrier(self.qr)
        self.qc.measure(self.qr,self.cr)
        job = execute(self.qc, backend=get_backend(backend), shots=shots)
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

        
def bell_correlation (basis,backend='local_qasm_simulator',shots=1024):
    """Prepares a rotated Bell state of two qubits. Measurement is done in the specified basis for each qubit. The fraction of results for which the two qubits agree is returned.
    
    basis = String specifying measurement bases. 'XX' denotes X measurement on each qubit, 'XZ' denotes X measurement on qubit 0 and Z on qubit 1, vice-versa for 'ZX', and 'ZZ' denotes 'Z' measurement on both.
    backend = A string specifying a backend. The noisy behaviour from a real device will result in the correlations being less strong than in the ideal case.
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
    
    job = execute(qc, backend=get_backend(backend), shots=shots)
    stats = job.result().get_counts()
    
    P = 0
    for string in stats:
        p = stats[string]/shots
        if string in ['00','11']:
            P += p
            
    return P

def bitstring_superposer (strings,backend='local_qasm_simulator',shots=1024):
    """Prepares the superposition of the two given n bit strings. The number of qubits used is equal to the length of the string. The superposition is measured, and the process repeated many times. A dictionary with the fraction of shots for which each string occurred is returned.
    
    string = List of two binary strings. If the list has more than two elements, all but the first two are ignored.
    backend = A string specifying a backend. The noisy behaviour from a real device will result in strings other than the two supplied occuring with non-zero fraction.
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

        if len(strings)==2**num:
            for n in range(num):
                qc.h(qr[n])
        else:
            diff = []
            for bit in range(num):
                if strings[0][bit]==strings[1][bit]:
                    if strings[0][bit]=='1':
                        qc.x(qr[bit])
                if strings[0][bit]!=strings[1][bit]:
                    diff.append(bit)
            if diff:
                qc.h(qr[diff[0]])
                for bit in diff[1:]:
                    qc.cx(qr[diff[0]],qr[bit])
                for bit in diff:
                    if strings[0][bit]=='1':
                        qc.x(qr[bit])

        qc.barrier(qr)
        qc.measure(qr,cr)
        
        batch.append(qc)

    job = execute(batch, backend=get_backend(backend), shots=shots)
    
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
    
def emoticon_superposer (emoticons,backend='local_qasm_simulator',shots=1024,figsize=(20,20)):
    """Creates superposition of two emoticons.
    
    A dictionary is returned, which supplies the relative strength of each pair of ascii characters in the superposition. An image representing the superposition, with each pair of ascii characters appearing with an weight that represents their strength in the superposition, is also created.
    
    emoticons = A list of two strings, each of which is composed of two ascii characters, such as [ ";)" , "8)" ].
    backend = A string specifying a backend. The noisy behaviour from a real device will result in emoticons other than the two supplied occuring with non-zero strength.
    shots = Number of times the process is repeated to calculate the fractions used as strengths. For shots=1, only a single randomnly generated emoticon is return (as the key of the dict)."""
    
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
                bin4char = (8-len(bin4char))*'0'+bin4char
                bin4emoticon += bin4char
            string.append(bin4emoticon)
        strings.append(string)
        
    stats = bitstring_superposer(strings,backend=backend,shots=shots)
    
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
            char = chr(int( string[0:8] ,2)) # get string of the leftmost 8 bits and convert to an ASCII character
            char += chr(int( string[8:16] ,2)) # do the same for string of rightmost 8 bits, and add it to the previous character
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


def image_superposer (all_images,images,backend='local_qasm_simulator',shots=1024,figsize=(20,20)):
    """Creates superposition of two images from a set of images.
    
    A dictionary is returned, which supplies the relative strength of each pair of ascii characters in the superposition. An image representing the superposition, with each of the original images appearing with an weight that represents their strength in the superposition, is also created.
    
    all_images = List of strings that are filenames for a set of images.  The files should be located in 'images/<filename>.png.
    images = List of strings for image files to be superposed. This can either contain the strings for two files, or for all in all_images. Other options are not currently supported.
    backend = A string specifying a backend. The noisy behaviour from a real device will result in images other than those intended appearing with non-zero strength.
    shots = Number of times the process is repeated to calculate the fractions used as strengths. For shots=1, only a single randomnly generated emoticon is return (as the key of the dict)."""
    image_num = len(all_images)
    bit_num = int(np.ceil( np.log2(image_num) ))
    all_images += [None]*(2**bit_num-image_num)
    
    # make it so that the input is a list of list of strings, even if it was just a list of strings
    if type(images[0])==str:
        images_list = [images]
    else:
        images_list = images
    
    strings = []
    for images in images_list:
        string = []
        for image in images:
            bin4pic = "{0:b}".format(all_images.index(image))
            bin4pic = '0'*(bit_num-len(bin4pic)) + bin4pic
            string.append( bin4pic )
        strings.append(string)
    
    full_stats = bitstring_superposer(strings,backend=backend,shots=shots)
        
    # make a list of dicts from stats
    if type(full_stats) is dict:
        full_stats_list = [full_stats]
    else:
        full_stats_list = full_stats
    
    stats_list = []
    for full_stats in full_stats_list:
        Z = 0
        for j in range(image_num):
            string = "{0:b}".format(j)
            string = '0'*(bit_num-len(string)) + string
            if string in full_stats:
                Z += full_stats[string]    
        stats = {}
        for j in range(image_num):
            string = "{0:b}".format(j)
            string = '0'*(bit_num-len(string)) + string
            if string in full_stats:
                stats[string] = full_stats[string]/Z
        stats_list.append(stats)
            
        # sort from least to most likely and create corresponding lists of the strings and fractions
        sorted_strings = sorted(stats,key=stats.get)
        sorted_fracs = sorted(stats.values())
        n = len(stats)
        # construct alpha values such that the final image is a weighted average of the images specified by the keys of `stats`
        alpha = [ sorted_fracs[0] ]
        for j in range(0,n-1):
            alpha.append( ( alpha[j]/(1-alpha[j]) ) * ( sorted_fracs[j+1] / sorted_fracs[j] ) )

        fig, ax = plt.subplots(figsize=figsize)
        for j in reversed(range(n)):
            filename = all_images[int(sorted_strings[j],2)]
            if filename:
                image = plt.imread("images/"+filename+".png")
                plt.imshow(image,alpha=alpha[j])
        plt.axis('off')
        plt.show()
    
    image_stats_list = []
    for stats in stats_list:
        image_stats = {}
        for string in stats:
            image_stats[ all_images[int(string,2)] ] = stats[string]
        image_stats_list.append(image_stats)
    
    # if only one instance was given, output dict rather than list with a single dict
    if len(image_stats_list)==1:
        image_stats_list = image_stats_list[0]
    
    return image_stats_list


class layout:
    """Processing and display of data in ways that depend on the layout of a quantum device."""
    
    def __init__(self,device):
        """Given a device, specified by
        
        device = A string specifying a device, or a list of two integers to define a grid.
        
        the following properties are determined.
        
        num = Number of qubits on the device.
        pairs = Dictionary detailing the pairs of qubits for which cnot gates can be directly implemented. Each value is a list of two qubits for which this is possible. The corresponding key is a string that is used as the name of the pair.
        pos = A dictionary of positions for qubits, to be used in plots.
        """
        if device in ['ibmqx2', 'ibmqx4', 'ibmqx5']:
                        
            backend = get_backend(device)
            self.num = backend.configuration['n_qubits']
            coupling = backend.configuration['coupling_map']
            self.pairs = {}
            char = 65
            for pair in coupling:
                self.pairs[chr(char)] = pair
                char += 1
            if device in ['ibmqx2','ibmqx4']:
                self.pos = { 0: [1,1], 1: [1,0], 2: [0.5,0.5], 3: [0,0], 4: [0,1] }        
            elif device=='ibmqx5':
                self.pos = { 0: [0,0], 1: [0,1],  2: [1,1],  3: [2,1],  4: [3,1],  5: [4,1],  6: [5,1],  7: [6,1],
8: [7,1], 9: [7,0], 10: [6,0], 11: [5,0], 12: [4,0], 13: [3,0], 14: [2,0], 15: [1,0] }
            
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
        
class pauli_grid:

    def __init__(self,rho):
                
        self.box = {'ZI':(-1, 2),'XI':(-2, 3),'IZ':( 1, 2),'IX':( 2, 3),'ZZ':( 0, 3),'ZX':( 1, 4),'XZ':(-1, 4),'XX':( 0, 5)}
        
        self.rho = {}
        for pauli in self.box:
            self.rho[pauli] = 0.0
        for pauli in ['ZI','IZ','ZZ']:
            self.rho[pauli] = 1.0
            
        self.qr = QuantumRegister(2)
        self.cr = ClassicalRegister(2)
        self.qc = QuantumCircuit(self.qr, self.cr)
    
    def get_rho(self,backend='local_qasm_simulator',shots=1024):
        
        bases = ['ZZ','ZX','XZ','XX']
        results = {}
        for basis in bases:
            temp_qc = copy.deepcopy(self.qc)
            for j in range(2):
                if basis[j]=='X':
                    temp_qc.h(self.qr[j])
            temp_qc.barrier(self.qr)
            temp_qc.measure(self.qr,self.cr)
            job = execute(temp_qc, backend=get_backend(backend), shots=shots)
            results[basis] = job.result().get_counts()
            for string in results[basis]:
                results[basis][string] = results[basis][string]/shots
          
        prob = {}
        # prob of expectation value -1 for single qubit observables
        for j in range(2):
            for p in ['X','Z']:
                pauli = {}
                for pp in 'IXZ':
                    pauli[pp] = (j==1)*pp + p + (j==0)*pp
                prob[pauli['I']] = 0
                for basis in [pauli['X'],pauli['Z']]:
                    for string in results[basis]:
                        if string[(j+1)%2]=='1':
                            prob[pauli['I']] += results[basis][string]/2
        # prob of expectation value -1 for two qubit observables
        for basis in ['ZZ','ZX','XZ','XX']:
            prob[basis] = 0
            for string in results[basis]:
                if string[0]!=string[1]:
                    prob[basis] += results[basis][string]

        for pauli in prob:
            self.rho[pauli] = 1-2*prob[pauli]

    
    def show_grid(self,rho=None,labels=False,bloch=None,hidden=[],mode='line',backend='local_qasm_simulator',shots=1024):
        
        l = 1 # line length
        r = 0.6 # circle radius
        L = 0.98*np.sqrt(2) # box height and width
        
        # colors are background, qubit circles and correlation circles, respectively
        if mode=='line':
            self.colors = [(0.9,0.9,0.9),(0.75,0.75,0.75),(0.5,0.5,0.5)]
        else:
            self.colors = [(0.8,0.9,0.9),(0.6,0.8,0.8),(0.3,0.7,0.7)]
        
        plt.rcParams['figure.facecolor'] = self.colors[0]
        
        if rho==None:
            self.get_rho(backend='local_qasm_simulator',shots=1024)
            rho = self.rho
        else:
            if type(rho)==list: # assume that it is a list of counts dicts and therefore requires conversion
                rho = {}
                for pauli in self.box:
                    rho[pauli] = 1-2*random.random()  
        
        def add_line(line,pauli,expect):
            # line = the type of line to be drawn (X, Z or the other one)
            # pauli = the box where the line is to be drawn
            # expect = the expectation value that determines its length
            unhidden = True
            for j in hidden:
                unhidden = unhidden and pauli[j]=='I'
            coord = None
            if unhidden:
                if line=='Z':
                    a = ( self.box[pauli][0], self.box[pauli][1]+l/2 )
                    b = ( self.box[pauli][0], self.box[pauli][1]-(-expect/2)*l )
                    c = ( self.box[pauli][0], self.box[pauli][1]-l/2 )
                    plt.plot( [a[0],b[0]], [a[1],b[1]], color=(0.0,0.0,1.0), lw=15 )
                    plt.plot( [b[0],c[0]], [b[1],c[1]], color=(0.75,0.75,1.0), lw=15 )
                    coord = b[1]
                elif line=='X':
                    a = ( self.box[pauli][0]+l/2, self.box[pauli][1] )
                    b = ( self.box[pauli][0]-(-expect/2)*l, self.box[pauli][1] )
                    c = ( self.box[pauli][0]-l/2, self.box[pauli][1] )
                    plt.plot( [a[0],b[0]], [a[1],b[1]], color=(1.0,0.0,0.0), lw=15 )
                    plt.plot( [b[0],c[0]], [b[1],c[1]], color=(1.0,0.75,0.75), lw=15 )
                    coord = b[0]
                else:
                    a = ( self.box[pauli][0]+l/(2*np.sqrt(2)), self.box[pauli][1]+l/(2*np.sqrt(2)) )
                    b = ( self.box[pauli][0]-(-expect/2)*l/(np.sqrt(2)), self.box[pauli][1]-(-expect/2)*l/(np.sqrt(2)) )
                    c = ( self.box[pauli][0]-l/(2*np.sqrt(2)), self.box[pauli][1]-l/(2*np.sqrt(2)) )
                    plt.plot( [a[0],b[0]], [a[1],b[1]], color=(0.0,0.8,0.0), lw=15 )
                    plt.plot( [b[0],c[0]], [b[1],c[1]], color=(0.75,0.9,0.75), lw=15 )
            return coord
        
        fig, ax = plt.subplots(figsize=[12,10])

        # draw boxes
        for pauli in self.box:
            if 'I' in pauli:
                color = self.colors[1]
            else:
                color = self.colors[2]
            ax.add_patch( Rectangle( (self.box[pauli][0],self.box[pauli][1]-1), L, L, angle=45, color=color) )  

        # draw circles
        for pauli in self.box:
            if mode=='line':
                ax.add_patch( Circle(self.box[pauli], r, color=(0.95,0.95,0.95)) )
            else:
                prob = (1-rho[pauli])/2
                ax.add_patch( Circle(self.box[pauli], r, color=(prob,prob,prob)) )

        if mode=='line':
            # add bars
            if bloch in [0,1]:
                for other in 'IXZ':
                    px = other*(bloch==1) + 'X' + other*(bloch==0)
                    pz = other*(bloch==1) + 'Z' + other*(bloch==0)
                    z_coord = add_line('Z',pz,rho[pz])
                    x_coord = add_line('X',pz,rho[px])
                    ax.add_patch( Circle((x_coord,z_coord), 0.05, color='black', zorder=10) )
                px = 'I'*(bloch==0) + 'X' + 'I'*(bloch==1)
                pz = 'I'*(bloch==0) + 'Z' + 'I'*(bloch==1)
                add_line('Z',pz,rho[pz])
                add_line('X',px,rho[px])

            else:
                for pauli in self.box:
                    if pauli in ['ZI','IZ','ZZ']:
                        add_line('Z',pauli,rho[pauli])
                    if pauli in ['XI','IX','XX']: 
                        add_line('X',pauli,rho[pauli])
                    if pauli in ['XZ','ZX']:
                        add_line('ZX',pauli,rho[pauli])
        
        if labels:
            for pauli in box:
                plt.text(self.box[pauli][0]-0.05,self.box[pauli][1]-0.85, pauli)

        plt.plot()
        plt.axis('off')
        plt.show()
