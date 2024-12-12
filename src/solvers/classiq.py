from qunfold import QUnfolder
from ..solver import Solver
from classiq import *
import numpy as np
from typing import List, Dict
from .transpiler import *

from qiskit import QuantumCircuit


class ClassiqSolver(Solver):
    def __init__(self, qu_unfoler: QUnfolder, solver_options: object = ...) -> None:
        super().__init__(qu_unfoler, solver_options)
        self.Q = self.qu_unfolder._get_qubo_matrix().tolist()

    def solve_binary(self) -> List[float]:
        qprog = self._create_qprog_binary()
        transpiled_circ = get_transpiled_circuit_from_qasm(qprog.qasm)
        return super().solve_binary()

    def solve_integer(self, num_shots=1000, num_layers=1) -> List[float]:
        qprog = self._create_qprog_integer(num_layers=num_layers)
        transpiled_circ = get_transpiled_circuit_from_qasm(qasm=qprog.qasm)
        self.circuit = transpiled_circ
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
    def _cost_binary(self, v: QArray[QBit] | list[int]) -> int:

        step1 = [
            sum([self.Q[i][j] * v[j] for j in range(len(self.Q))])
            for i in range(len(self.Q))
        ]
        return sum([step1[i] * v[i] for i in range(len(step1))])

    def _create_ws_angles(self):
        ws_bit_array = []

        for idx, value in enumerate(self.q_unfold.d):
            str_value = format(value, f"0{self.q_unfold.num_bits[idx]}b")
            ws_bit_array.extend(list(str_value))

        ws_bit_array = [int(element) for element in ws_bit_array]

        ws_bit_array_angles = [
            2 * np.arcsin(np.sqrt(element)) for element in ws_bit_array
        ]

        return ws_bit_array_angles

    @qfunc
    def _mixer_layer(beta: CReal, qba: QArray):
        apply_to_all(lambda q: RX(beta, q), qba)

    @qfunc
    def _prepare_start_state(qba: QArray[QBit]):
        hadamard_transform(qba)

    def _create_quantumcricuit_integer(
        self,
        num_layers=1,
        constraints=Constraints(optimization_parameter="depth"),
        preferences=Preferences(),
    ) -> QuantumCircuit:
        qprogram = self._create_qprog_integer(
            num_layers=num_layers, constraints=constraints, preferences=preferences
        )
        self.circuit = qiskit.qasm3.loads(qprogram.qasm)
        return qiskit.qasm3.loads(qprogram.qasm)

    def _create_qprog_integer(
        self, num_layers=1, constraints=Constraints(), preferences=Preferences()
    ) -> QuantumProgram:
        class V(QStruct):
            pass

        V.__annotations__ = {
            f"n_{idx}": QNum[qnum_size, UNSIGNED, 0]
            for idx, qnum_size in enumerate(self.qu_unfolder.num_bits)
        }

        @qfunc
        def qaoa_ansatz(
            cost_layer: QCallable[CReal, V],
            num_layers: CInt,
            gammas: CArray[CReal],
            betas: CArray[CReal],
            qba: V,
        ):
            self._prepare_start_state(qba)
            repeat(
                num_layers,
                lambda i: [
                    cost_layer(gammas[i], qba),
                    self._mixer_layer(betas[i], qba),
                ],
            )

        @qfunc
        def cost_layer_integer(gamma: CReal, v: V):
            phase(self._cost_integer(list(v._fields.values())), gamma)

        @qfunc
        def main(params: CArray[CReal, num_layers * 2], v: Output[V]): # type: ignore
            allocate(sum(self.qu_unfolder.num_bits), v)
            qaoa_ansatz(
                cost_layer_integer,
                num_layers,
                params[0:num_layers],
                params[num_layers : 2 * num_layers],
                v,
            )

        model = create_model(main, constraints=constraints, preferences=preferences)
        qprog = synthesize(model)

        qprogram = QuantumProgram.from_qprog(qprog)

        return qprogram

    def _create_qprog_binary(
        self, num_layers=1, constraints=Constraints(), preferences=Preferences()
    ) -> QuantumProgram:

        @qfunc
        def qaoa_ansatz(
            cost_layer: QCallable[CReal, QArray[QBit]],
            num_layers: CInt,
            gammas: CArray[CReal],
            betas: CArray[CReal],
            qba: QArray[QBit],
        ):
            self._prepare_start_state(qba)
            repeat(
                num_layers,
                lambda i: [
                    cost_layer(gammas[i], qba),
                    self._mixer_layer(betas[i], qba),
                ],
            )

        @qfunc
        def cost_layer_binary(gamma: CReal, v: QArray[QBit]):
            phase(self._cost_binary(v), gamma)

        @qfunc
        def main(params: CArray[CReal, num_layers * 2], v: Output[QArray[QBit]]): # type: ignore
            allocate(sum(self.qu_unfolder.num_bits), v)
            qaoa_ansatz(
                cost_layer_binary,
                num_layers,
                params[0:num_layers],
                params[num_layers : 2 * num_layers],
                v,
            )

        model = create_model(main, constraints=constraints, preferences=preferences)
        qprog = synthesize(model)

        qprogram = QuantumProgram.from_qprog(qprog)
        self.qprogram = qprogram

        return qprogram
