from qunfold import QUnfolder
import math
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.primitives import SamplerV2 as Sampler
from typing import Dict, List, Callable, Tuple
import numpy as np
import scipy
from scipy import stats
from matplotlib.ticker import MaxNLocator
from matplotlib import pyplot as plt
from typing import Tuple

class Solver:

    def __init__(self, qu_unfoler: QUnfolder, solver_options: object = {}) -> None:
        self.simulator = AerSimulator(device="CPU")
        self.qu_unfolder = qu_unfoler
        self.solver_options = solver_options
        self.sampler = Sampler().from_backend(self.simulator)
        self.circuit = None
        self.cost_values = []

    def solve_binary(self):
        pass

    def solve_integer(self):
        pass

    def _sample_with_params(
        self, params: List[float], num_shots: int = 1000, num_layers=1
    ) -> List[Dict[str, float]]:
        job = self.sampler.run(
            [(self.circuit, self._gen_param_dict(params))], shots=num_shots
        )
        result = job.result()
        parsed_results = []

        for key, value in result[0].data.meas.get_counts().items():
            integers = self._split_string_by_indices(key, self.qu_unfolder.num_bits)
            parsed_results.append({"values": integers, "counts": value})

        return parsed_results

    def _split_string_by_indices(self, s, indices) -> List[int]:
        parts = []
        start = 0
        for index in indices:
            parts.append(s[start : start + index])
            start += index

        return [int(chunk, 2) for chunk in parts]

    def _gen_param_dict(self, params: List[float]) -> Dict[str, float]:
        new_dict = {}
        for idx, param in enumerate(params):
            new_dict[f"params_param_{idx}"] = float(param)

        return new_dict

    def get_costs(self, params, cost_function: Callable, num_shots: int) -> float:
        parsed_results = self._sample_with_params(params, num_shots=num_shots)

        counts = np.vectorize(lambda result: result["counts"])(parsed_results)
        costs = np.vectorize(lambda result: cost_function(result["values"]))(
            parsed_results
        )
        estimated_cost = float(np.average(costs, weights=counts))
        self.cost_values.append(estimated_cost)
        return estimated_cost

    def _execute_circ(
        self,
        cost_function: Callable = None,
        num_layers=1,
        num_shots=1000,
    ) -> List[float]:
        if cost_function is None:
            raise ValueError("Cost function could not be None")

        self.cost_values = []

        initial_params = (
            np.concatenate(
                (np.linspace(0, 1, num_layers), np.linspace(1, 0, num_layers))
            )
            * math.pi
        )

        final_params = scipy.optimize.minimize(
            fun=self.get_costs,
            args=(cost_function, num_shots),
            x0=initial_params,
            method="COBYLA",
            options={"maxiter": 120},
        ).x.tolist()

        return final_params

    def _cost_binary_inference(self, input: List[float]):
        np_input = np.array(input)
        return np_input @ self.qu_unfolder.qubo_matrix @ np_input

    def _cost_integer_inference(self, input: List[float]):
        np_input = np.array(input)
        return (self.qu_unfolder.R @ np_input - self.qu_unfolder.d) @ (
            self.qu_unfolder.R @ np_input - self.qu_unfolder.d
        )

    def get_results_and_print(
        self, final_params, cost_function: callable = None, num_shots=1000, print=True
    ) -> List[int]:
        res = self._sample_with_params(final_params, num_shots=num_shots)

        top_results = []

        sorted_counts = sorted(
            res, key=lambda pc: self._cost_integer_inference(pc["values"])
        )
        for sampled in sorted_counts[0:10]:
            top_results.append(sampled["values"])
            if print:
                print(
                    f"solution={sampled['values']} probability={sampled['counts']/num_shots} cost={self._cost_integer_inference(sampled['values'])}"
                )

        return top_results

    def get_p_t_value(self, best_results: List[float]):
        sol, cov = self.qu_unfolder.solve_gurobi_integer()
        t_stat, p_value = stats.ttest_ind(best_results[0], sol)
        return p_value, t_stat
    
    def plot_convergence(self, p:float=None):
        fig, axes = plt.subplots(nrows=1, ncols=1)
        axes.plot(self.cost_values)
        axes.set_xlabel("Iterations")
        axes.set_ylabel("Cost")
        axes.set_title(f"Cost convergence, iters: {len(self.cost_values)} p={p}")
        axes.xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.savefig(f'my_plot-{p}.png')
        plt.show()