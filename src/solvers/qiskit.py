from qunfold import QUnfolder
from ..solver import Solver
import gurobipy
from qiskit_optimization.translators import from_gurobipy
from qiskit_optimization.converters import QuadraticProgramToQubo
from qiskit.circuit.library import qaoa_ansatz
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter

from .transpiler import *


class QiskitSolver(Solver):
    def __init__(self, qu_unfoler: QUnfolder, solver_options: object = ...) -> None:
        super().__init__(qu_unfoler, solver_options)

    def solve_binary(self, num_layers=1, num_shots=1000):
        self.qu_unfolder.initialize_qubo_model()
        self.Q = self.qu_unfolder._get_qubo_matrix().tolist()
        cric = self._create_qaoa_binary(self)
        circ = self._update_param_names(circ)
        traspiled_circ = get_transpiled_circuit_from_quantumProgram(circ)
        final_params = self._execute_circ(
            self._cost_integer, num_layers=num_layers, num_shots=num_shots
        )
        return final_params

    def solve_integer(self, num_layers=1, num_shots=1000):
        circ = self._create_quantumcricuit_integer(num_layers=num_layers)
        circ = self._update_param_names(circ)
        traspiled_circ = get_transpiled_circuit_from_quantumProgram(circ)
        self.circuit = traspiled_circ
        final_params = self._execute_circ(
            self._cost_integer, num_layers=num_layers, num_shots=num_shots
        )
        return final_params

    # This function will return this objective function: (R @ x - d) @ (R @ x - d)
    def _cost_integer(self, x: list[int]) -> int:
        def dot_product_vec_vec(vec_1, vec_2):
            return sum([a * b for a, b in zip(vec_1, vec_2)])

        # (R @ x - d)
        def dot_product_vec_mat_with_subtraction(vec, mat, sub):
            dot = [
                sum([mat[i][j] * vec[j] for j in range(len(mat))])
                for i in range(len(mat))
            ]

            return [sub[i] - dot[i] for i in range(len(sub))]

        return dot_product_vec_vec(
            dot_product_vec_mat_with_subtraction(
                x, self.qu_unfolder.R, self.qu_unfolder.d
            ),
            dot_product_vec_mat_with_subtraction(
                x, self.qu_unfolder.R, self.qu_unfolder.d
            ),
        )

    # cost function: x @ Q @ x
    def _cost_binary(self, v: list[int]) -> int:

        step1 = [
            sum([self.Q[i][j] * v[j] for j in range(len(self.Q))])
            for i in range(len(self.Q))
        ]
        return sum([step1[i] * v[i] for i in range(len(step1))])

    def _create_quantumcricuit_integer(self, num_layers=1) -> QuantumCircuit:
        model = gurobipy.Model()
        vtype = gurobipy.GRB.INTEGER
        sense = gurobipy.GRB.MINIMIZE
        model.setParam("OutputFlag", 0)
        x = [
            model.addVar(vtype=vtype, lb=0, ub=2**b - 1)
            for b in self.qu_unfolder.num_bits
        ]
        R, d = self.qu_unfolder.R, self.qu_unfolder.d
        objective = (R @ x - d) @ (R @ x - d)
        model.setObjective(objective, sense=sense)

        qp = from_gurobipy(model)

        conv = QuadraticProgramToQubo()
        mod = conv.convert(qp)
        op, offset = mod.to_ising()

        ansatz = qaoa_ansatz(op, reps=num_layers, insert_barriers=True, flatten=True)

        return ansatz

    def _create_qaoa_binary(self, num_layers=1) -> QuantumCircuit:
        modelGBP = gurobipy.Model()
        vtype = gurobipy.GRB.BINARY
        sense = gurobipy.GRB.MINIMIZE
        x = [
            modelGBP.addVar(vtype=vtype)
            for i in range(self.qu_unfolder.num_bins)
            for _ in range(self.qu_unfolder.num_bits[i])
        ]
        Q = self.qu_unfolder.qubo_matrix
        modelGBP.setObjective(x @ Q @ x, sense=sense)

        qp = from_gurobipy(modelGBP)

        conv = QuadraticProgramToQubo()
        mod = conv.convert(qp)
        op, offset = mod.to_ising()

        ansatz = qaoa_ansatz(op, reps=num_layers, insert_barriers=True, flatten=True)

        return ansatz

    def _update_param_names(self, circ: QuantumCircuit) -> QuantumCircuit:
        for idx, param in enumerate(circ.parameters):
            new_param = Parameter(f"params_param_{idx}")
            circ.assign_parameters({param: new_param}, inplace=True)

        return circ
