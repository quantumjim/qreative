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
        
        # device can be a string specifying a device or a tuble specifying a grid
        if isinstance( device, str ):
            backend = get_backend(device)
            self.num = backend.configuration['n_qubits']
            coupling_array = backend.configuration['coupling_map']
            self.coupling = {}
            for n in range(self.num):
                self.coupling[n] = []
            for pair in coupling_array:
                for j in range(2):
                    self.coupling[pair[j]].append(pair[(j+1)%2])
                    self.coupling[pair[(j+1)%2]].append(pair[j])
        else:
            Lx = device[0]
            Ly = device[1]
            self.num = Lx*Ly
            self.coupling = {}
            for n in range(self.num):
                self.coupling[n] = []
            for x in range(Lx-1):
                for y in range(Ly):
                    n = x + y*Ly
                    m = n+1
                    self.coupling[n].append(m)
                    self.coupling[m].append(n)
            for x in range(Lx):
                for y in range(Ly-1):
                    n = x + y*Ly
                    m = n+Ly
                    self.coupling[n].append(m)
                    self.coupling[m].append(n)
         
        if method=='run':
            self.starts, self.walks = self.setup_walks()
        else:
            self.walks = None
        
        self.starts,self.stats = self.get_data()
        
            
    def setup_walks(self):
        
        walks = []
        starts = []
        for sample in range(self.samples):
            
            if not self.start:
                start = random.choice( range(self.num) )
            else:
                start = self.start
            starts.append(start)
            
            walk = [start]
            for l in range(self.length):
                neighbours = list( set(self.coupling[walk[-1]]) - set(walk) )
                if neighbours:
                    walk.append( random.choice( neighbours ) )
                else:
                    walk.append( random.choice( self.coupling[ walk[-1] ] ) )
            walks.append(walk)
            
        return starts, walks
    
    
    def get_data(self):
        
        if self.method=='run':
            batch = []
            for sample in range(self.samples):
                for steps in range(1,self.length+1):

                    qr = QuantumRegister(self.num)
                    cr = ClassicalRegister(self.num)
                    qc = QuantumCircuit(qr,cr)
                    
                    qc.h(qr[self.walks[sample][0]])

                    for step in range(1,steps):
                        n = self.walks[sample][step-1]
                        m = self.walks[sample][step]
                        qc.cx(qr[n],qr[m])
                        qc.h(qr[m])

                    qc.measure(qr,cr)
                
                    batch.append(qc)
                    
            job = execute(batch, backend=get_backend(self.backend), shots=self.shots)
            
            probs = []
            j = 0
            for sample in range(self.samples):
                probs_for_sample = []
                for step in range(self.length):
                    stats = job.result().get_counts(batch[j])
                    prob = [0]*self.num
                    for string in stats:
                        for n in range(self.num):
                            if string[n]=='1':
                                prob[n] += stats[string]/self.shots
                    probs_for_sample.append( prob )
                    j += 1
                probs.append(probs_for_sample)
               
            starts = self.starts
            
            saveFile = open('results.txt', 'w')
            saveFile.write( str(probs) )
            saveFile.write( str(starts) )
            saveFile.close()
        
        else:
            
            saveFile = open('results.txt')
            saved_data = saveFile.readlines()
            saveFile.close()
            
            probs_string = saved_data[0]
            starts_string = saved_data[1]
            probs = eval(probs_string)
            starts = eval(starts_string)
            
        return starts,probs 
        
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

