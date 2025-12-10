import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer import Aer
from matplotlib import pyplot as plt
from qiskit.visualization import plot_histogram, plot_bloch_multivector, array_to_latex
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime import SamplerV2 as Sampler

# TODO DO NOT PUSH TO GITHUB WTHOUT REMOVING THIS
IBM_API_KEY = "REMOVED"

service = QiskitRuntimeService(channel="ibm_cloud", token=IBM_API_KEY,
instance="open-instance")
service.backends()

backend = service.backend(name="ibm_fez")

def getOutputBit(input):
    outputBit = {"0": 0, "1": 0}
    for outKey in outputBit.keys():
        for inKey in input.keys():
            if inKey[0] == outKey:
                outputBit[outKey] = outputBit[outKey] + input[inKey]
    return outputBit

def Teleport(source, entangled, dest):
    qc = QuantumCircuit(3, 3)

    # Entangled Pair
    qc.h(entangled)
    qc.cx(entangled, dest)

    qc.barrier()

    # Alice
    qc.cx(source, entangled)
    qc.h(source)

    qc.barrier()

    qc.measure([source, entangled], [0, 1])

    qc.barrier()

    with qc.if_test((1, 1)):
        qc.x(dest)

    with qc.if_test((0, 1)):
        qc.z(dest)

    qc.barrier()

    return qc

# Consecutive Teleportation Experiment

print("Starting")
outputResults = {}
for i in range(5): # 5
    print(i)
    stages = 2 ** (i+1) # How many teleporations to perform

    qc = QuantumCircuit(3, 3)

    # Setup Qbit; Perfect would be 50/50 result unless drifting
    qc.h(0)

    qc.barrier()

    for i in range(int(stages/2)):
        # Teleport
        qc.compose(Teleport(0, 1, 2), inplace=True)

        qc.reset(0)
        qc.reset(1)

        qc.compose(Teleport(2, 1, 0), inplace=True)

        qc.reset(1)
        qc.reset(2)

    # Measure Result
    qc.measure([0,1,2], [2,1,0]) # Top measurement into 3rd bit

    # Draw the circuit
    # print(qc.draw(fold=4000))

    simulator = AerSimulator()
    compiled_circuit = transpile(qc, simulator)
    job = simulator.run(compiled_circuit, shots=1000)
    result = job.result()
    outputResults.update({stages: getOutputBit(result.get_counts())})

    print("Running")

    # qc_transpiled = transpile(qc, backend, optimization_level=2)
    # sampler = Sampler(mode=backend)
    # qc_job = sampler.run([qc_transpiled], shots=1000)
    # counts = qc_job.result()[0].data.c.get_counts()
    # outputResults.update({stages: getOutputBit(counts)})
    # print(stages, counts)

print(outputResults)
