# coding: utf-8

from qiskit import ClassicalRegister, QuantumRegister, QuantumCircuit, get_backend, execute
import numpy as np
import random
import matplotlib.pyplot as plt
import os

from qiskit import register

#import Qconfig and set APIToken and API url
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
    pass

class ladder:
    
    def __init__(self,d,shots=1024):
        self.d = d
        self.shots = shots
        self.qr = QuantumRegister(1)
        self.cr = ClassicalRegister(1)
        self.qc = QuantumCircuit(self.qr, self.cr)
        
    def add(self,delta):
        self.qc.rx(np.pi*delta/self.d,self.qr[0])
        
    def value(self,backend='local_qasm_simulator',shots=1024):
        self.qc.measure(self.qr,self.cr)
        job = execute(self.qc, backend=get_backend(backend), shots=shots)
        if '1' in job.result().get_counts():
            p = job.result().get_counts()['1']/shots
        else:
            p = 0
        delta = round(2*np.arcsin(np.sqrt(p))*self.d/np.pi)
        return int(delta)

class interrogate:
    
    def __init__(self):
        self.qr = QuantumRegister(1)
        self.cr = ClassicalRegister(1)
        self.qc = QuantumCircuit(self.qr, self.cr)
        self.bool = None
        self.prepare({'Y':None})
        
    def prepare(self,state):
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
                
    def measure(self,basis,backend='local_qasm_simulator',shots=1024,mitigate=True):
        if basis=='X':
            self.qc.h(self.qr[0])
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
        self.bool = ( p>random.random() )
        self.prepare({basis:self.bool})

class walker:
    
    def __init__(self,length,device,start=None,samples=1,backend='local_qasm_simulator',shots=1024,method='run'):
        
        self.length = length
        self.start = start
        self.samples = samples
        self.backend = backend
        self.shots = shots
        self.method = method
        
        # device can be a string specifying a device or a number of qubits for all-to-all connectivity
        if isinstance( device, str ):
            backend = get_backend(device)
            self.num = backend.configuration['n_qubits']
            self.coupling = backend.configuration['coupling_map']
        else:
            self.num = device
            self.coupling = []
            for n in range(self.num):
                for m in list(range(n))+list(range(n+1,self.num)):
                    self.coupling.append([n,m])
         
        if method=='run':
            if start:
                self.start = start
            else:
                self.start = ''
                for n in range(self.num):
                    self.start += random.choice(['0','1'])
            self.starts, self.circuits = self.setup_walk()
        else:
            self.circuits = None
        
        self.starts,self.stats = self.get_data()
            
            
    def setup_walk(self):
        
        circuits = []
        starts = []
        for sample in range(self.samples):
            
            circuit = []
            for l in range(self.length):
                gate = random.choice(['X','Y','XX'])
                if gate=='XX':
                    n = random.choice(self.coupling)
                else:
                    n = random.randint(0,self.num-1)
                circuit.append( { 'gate':gate, 'n':n } ) 
            circuits.append(circuit)

            if not self.start:
                start = ''
                for n in range(self.num):
                    start += random.choice(['0','1'])
            else:
                start = self.start
            starts.append(start)
            
        return starts,circuits
    
    def get_data(self):
        
        if self.method=='run':
            batch = []
            for sample in range(self.samples):
                for steps in range(self.length):

                    qr = QuantumRegister(self.num)
                    cr = ClassicalRegister(self.num)
                    qc = QuantumCircuit(qr,cr)

                    for n in range(self.num):
                        if self.starts[sample][n]=='1':
                            qc.x(qr[self.num-n-1])

                    for step in range(steps):
                        gate = self.circuits[sample][step]['gate']
                        n = self.circuits[sample][step]['n']
                        if gate=='XX':
                            #qc.cx(qr[n[0]],qr[n[1]])
                            qc.rx(np.pi/4,qr[n[0]])
                            qc.cx(qr[n[0]],qr[n[1]])
                        elif gate=='X':
                            qc.rx(np.pi/4,qr[n])
                        elif gate=='Y':
                            qc.ry(np.pi/4,qr[n])

                    qc.measure(qr,cr)
                
                    batch.append(qc)
                    
            job = execute(batch, backend=get_backend(self.backend), shots=self.shots)
            
            stats = []
            j = 0
            for sample in range(self.samples):
                stats_for_sample = []
                for step in range(self.length):
                    this_stats = job.result().get_counts(batch[j])
                    for string in this_stats:
                        this_stats[string] = this_stats[string]/self.shots
                    stats_for_sample.append( this_stats )
                    j += 1
                stats.append(stats_for_sample)
                
            
            saveFile = open('results.txt', 'w')
            saveFile.write( str(stats) )
            saveFile.close()

            starts = self.starts
                
        else:
            
            saveFile = open('results.txt')
            saved_data = saveFile.readlines()
            saveFile.close()
            
            stats_string = saved_data[0]
            stats = eval(stats_string)
            starts = []
            for stats_for_sample in stats:
                starts.append( max(stats_for_sample[0], key=stats_for_sample[0].get) )
            
            saveFile.close()
            
        return starts,stats
    
        
def bell_correlation (basis,backend='local_qasm_simulator',shots=1024):
    
    qr = QuantumRegister(2)
    cr = ClassicalRegister(2)
    qc = QuantumCircuit(qr,cr)

    qc.h( qr[0] )
    qc.cx( qr[0], qr[1] )
    qc.ry( np.pi/4, qr[1])
    qc.h( qr[1] )
    qc.x( qr[0] )
    qc.z( qr[0] )
    
    for j in range(2):
        if basis[j]=='X':
            qc.h(qr[j])

    qc.measure(qr,cr)
    
    job = execute(qc, backend=get_backend(backend), shots=shots)
    stats = job.result().get_counts()
    
    P = 0
    for string in stats:
        p = stats[string]/shots
        if string in ['00','11']:
            P += p
            
    return P

def bitstring_superposer (string,backend='local_qasm_simulator',shots=1024):
    
    num = len(string[0])
    
    qr = QuantumRegister(num)
    cr = ClassicalRegister(num)
    qc = QuantumCircuit(qr,cr)
    
    diff = []
    for bit in range(num):
        
        if string[0][bit]==string[1][bit]:
            if string[0][bit]=='1':
                qc.x(qr[bit])
                
        if string[0][bit]!=string[1][bit]:
            diff.append(bit)
    
    if diff:
        qc.h(qr[diff[0]])
        for bit in diff[1:]:
            qc.cx(qr[diff[0]],qr[bit])

        for bit in diff:
            if string[0][bit]=='1':
                qc.x(qr[bit])
            
    qc.measure(qr,cr)
    
    job = execute(qc, backend=get_backend(backend), shots=shots)
    stats_raw = job.result().get_counts()
    
    stats = {}
    for string in stats_raw:
        stats[string[::-1]] = stats_raw[string]/shots

    return stats
    
def emoticon_superposer (emoticons,backend='local_qasm_simulator',shots=1024,verbose=False):
    
    string = []
    for emoticon in emoticons:
        bin4emoticon = ""
        for character in emoticon:
            bin4char = bin(ord(character))[2:]
            bin4char = (8-len(bin4char))*'0'+bin4char
            bin4emoticon += bin4char
        string.append(bin4emoticon)
        
    stats = bitstring_superposer(string,backend='local_qasm_simulator',shots=1024)
    
    filename = 'superposition'
    for string in stats:
        char = chr(int( string[0:8] ,2)) # get string of the leftmost 8 bits and convert to an ASCII character
        char += chr(int( string[8:16] ,2)) # do the same for string of rightmost 8 bits, and add it to the previous character
        prob = stats[string] # fraction of shots for which this result occurred
        # create plot with all characters on top of each other with alpha given by how often it turned up in the output
        plt.annotate( char, (0.5,0.5), va="center", ha="center", color = (0,0,0, prob ), size = 300)
        if verbose:
            if (prob>0.05): # list prob and char for the dominant results (occurred for more than 5% of shots)
                print(str(prob)+"\t"+char)
        filename += '_' + char     
            
    plt.axis('off')
   
    plt.savefig(filename+'.png')

# to be used in image superposer
'''
    # sort from least to most likely and create corresponding lists of the strings and fractions
    sorted_strings = sorted(stats,key=stats.get)
    sorted_fracs = sorted(stats.values())
    n = len(stats) # it'll also be handy to know their lengths
    
    # construct alpha values such that the final image is a weighted average of the images specified by the keys of `stats`
    alpha = [ sorted_fracs[0] ]
    for j in range(0,n-1):
        alpha.append( ( alpha[j]/(1-alpha[j]) ) * ( sorted_fracs[j+1] / sorted_fracs[j] ) )
    
    print(sorted_fracs)
    print(alpha)
    
    plt.rc('font', family='monospace')

    ax = plt.subplot(111)

    
    for j in reversed(range(n)):
        char = chr(int( sorted_strings[j][0:8] ,2)) # get string of the leftmost 8 bits and convert to an ASCII character
        char += chr(int( sorted_strings[j][8:16] ,2)) # do the same for string of rightmost 8 bits, and add it to the previous character   
        plt.annotate( char, (0.5,0.5), va="center", ha="center", color = (0,0,0, alpha[j] ), size = 300)
    plt.axis('off')
    plt.show()
'''

