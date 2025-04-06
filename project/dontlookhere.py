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
# Function to apply a controlled-controlled RY (ccry)
def apply_ccry(qc, theta, control1, control2, target):
    """
    Applies a doubly-controlled RY gate (CCRY) using ancilla-free decomposition.
    control1, control2: control qubits
    target: target qubit
    """
    qc.cx(control2, target)
    qc.cry(theta / 2, control1, target)
    qc.cx(control2, target)
    qc.cry(-theta / 2, control1, target)

# Create circuit with 3 qubits and 3 classical bits (all start in |0⟩)
q = QuantumRegister(3)
c = ClassicalRegister(3)
qc = QuantumCircuit(q, c)

# === First branching: split between states 0-3 and 4-7 ===
qc.ry(math.pi / 2, q[0])

# === Second branching: controlled rotations on qubit 1 ===
qc.x(q[0])
qc.cry(3.048, q[0], q[1])
qc.x(q[0])

qc.cry(0.1286, q[0], q[1])

# === Third branching: controlled-controlled RY on qubit 2 ===

# Branch (0,0): q[0] = 0, q[1] = 0
qc.x(q[0])
qc.x(q[1])
apply_ccry(qc, 3.04, q[0], q[1], q[2])
qc.x(q[0])
qc.x(q[1])

# Branch (0,1): q[0] = 0, q[1] = 1
qc.x(q[0])
apply_ccry(qc, 2.428, q[0], q[1], q[2])
qc.x(q[0])

# Branch (1,0): q[0] = 1, q[1] = 0
qc.x(q[1])
apply_ccry(qc, 0.700, q[0], q[1], q[2])
qc.x(q[1])

# Branch (1,1): rotation angle ≈ 0 → skip

qc.barrier()
qc.measure(q, c)
print("*********************CIRCUIT*********************")
print(qc) # this is the circuit

# ---------- SIMULATING THE CIRCUIT & VIEWING PROBABILITY DISTR ------------
simulator = AerSimulator()
result = simulator.run(qc,shots=10000).result() # one shot = running bits through the circuit and measuring them once
counts = result.get_counts(qc)
plot_histogram(counts, title='State counts')