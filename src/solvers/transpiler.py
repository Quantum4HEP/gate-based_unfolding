import qiskit.qasm3
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit import QuantumCircuit, transpile


def get_transpiled_circuit_from_qasm(
    qasm: str, num_qubits: int = 200, native_gates=["u", "cx"], coupling_map=None
) -> QuantumCircuit:
    qiskit_circ = qiskit.qasm3.loads(qasm)

    return get_transpiled_circuit_from_quantumProgram(
        qiskit_circ,
        num_qubits=num_qubits,
        native_gates=native_gates,
        coupling_map=coupling_map,
    )


def get_transpiled_circuit_from_quantumProgram(
    circ: QuantumCircuit,
    num_qubits: int = 200,
    native_gates=["u", "cx"],
    coupling_map=None,
) -> QuantumCircuit:
    circ.measure_all()

    if coupling_map != None:
        num_qubits = coupling_map.size()
    fake_backend = GenericBackendV2(
        num_qubits, basis_gates=native_gates, coupling_map=coupling_map
    )
    transpiled_circ = transpile(circ, optimization_level=3, backend=fake_backend)

    return transpiled_circ
