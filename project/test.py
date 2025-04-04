# imports
import numpy as np
import math
import qiskit
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.circuit.library import Initialize
from qiskit.circuit import QuantumCircuit
from qiskit.quantum_info import random_statevector, Statevector
from qiskit.visualization import plot_bloch_multivector, plot_histogram

# printing function to show the statevector
def get_braket_string(statevector):
    num_qubits = log2(len(statevector))
    assert num_qubits.is_integer(), 'Expected a 2**n state'
    num_qubits = int(num_qubits)
    
    assert abs(np.linalg.norm(statevector) - 1) < 1e-4, 'Norm of state is too far from 1'
    
    
    simpler_state = []
    # discards 0 values
    for amplitude in statevector:
        if amplitude.imag == 0 and amplitude.real == 0:
            simpler_state.append(0)
        elif amplitude.imag == 0:
            simpler_state.append(amplitude.real)
        elif amplitude.real == 0:
            simpler_state.append(amplitude.imag)
        else:
            simpler_state.append(amplitude)


    out_str = ''
    skip_plus = False
    for index, amplitude in enumerate(simpler_state):
        if amplitude == 0:
            skip_plus = True
            continue
        
        if not skip_plus and index > 0:
            out_str += '+'

        state = format(index, f'0{num_qubits}b')
        
        # g defaults to 6 digits of precision but ignores zeros        
        out_str += f'{amplitude : g}|{state}>'
    return out_str



# ---------- CREATING THE CIRCUIT ------------
q = QuantumRegister(3) # one register with three qubits
c = ClassicalRegister(3) # one register with three classical bits
qc= QuantumCircuit(q,c) # circuit object
qc.x(q[0]) # apply X on first qubit
qc.y(q[1]) # apply Y on second qubit
qc.z(q[2]) # apply Z on third qubit
qc.barrier() # explicitly tells the compiler to avoid merging gates (don't optimize)
qc.id(q[0])
qc.h(q[2])
qc.measure(q, c)
print("*********************CIRCUIT*********************")
print(qc) # this is the circuit

# ---------- SIMULATING THE CIRCUIT & VIEWING PROBABILITY DISTR ------------
simulator = AerSimulator()
result = simulator.run(qc,shots=10000).result() # one shot = running bits through the circuit and measuring them once
counts = result.get_counts(qc)
plot_histogram(counts, title='State counts')