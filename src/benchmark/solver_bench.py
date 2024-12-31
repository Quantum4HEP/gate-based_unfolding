from ..solvers import ClassiqSolver, QiskitSolver
from typing import List
from .result import SolverResults, SolverRun
from .problem_generator import generate_problem_instance
from qunfold import QUnfolder
from ..solver import Solver


class SolverBenchmark:
    """
    Simple Class to run some execution benchmarks to see how acurate the QAOA result is vs a classical Gurobi solver result.
    """

    def __init__(self):
        pass

    def run_sovler_bench(
        self,
        solvers: Solver = None,
        problem={},
        iterations=5,
        layers: List[int] = [1],
        shots: List[int] = [1000],
        all_combinations: bool = False,
    ) -> List[SolverResults]:
        """
        Create different runs of a specific problem.

        Args:
            solvers (QiskitSolver | ClassiqSolver, optional): The specifc solver that should be used to solve the problem.
            problem (dict, optional): The problem parameters
            iterations (int, optional): The number of times each test configuration should be run
            layers (List[int], optional): Diffrent numbers of layers to test for each execution
            shots (List[int], optional): Different numbers of shots to test
            all_combinations (bool):If this is true, it will test all possible combiations between layers and shots
            If this is false, it will loop though the layers list and pick the corresponding
            index out of the shots list. This will create less test runs.

        Raises:
            AssertionError: If all_combinations is false and the lenght of layers and shots are not same length

        Returns:
            the list of of SolverResults
        """
        if not all_combinations:
            assert len(layers) == len(shots)

        end_result: List[SolverResults] = []

        for idx, layer in enumerate(layers):
            current_result = SolverResults(
                problem=problem, solver=solvers.__name__, iterations=iterations, shots=shots[idx], layers=layer
            )

            average_p = []
            average_absolute_difference = []
            average_iterations = []
            x, d, R, binning = generate_problem_instance(problem, seed=1)
            qu_unfolder = QUnfolder(response=R, measured=d, binning=binning, lam=0)

            solver = solvers(qu_unfolder)
            for i in range(iterations):
                try:
                    solver_run = SolverRun()
                    final_params, cost = solver.solve_integer(
                        num_layers=layer, num_shots=shots[idx]
                    )
                    solver_run.solver_final_params = final_params
                    solver_run.solver_costs = cost
                    average_iterations.append(len(cost))
                    top_results = solver.get_results_and_print(
                        final_params, num_shots=shots[idx], print_results=False
                    )
                    print(top_results[0])
                    sol, cov = qu_unfolder.solve_gurobi_integer()
                    print(sol)
                    p, t = solver.get_p_t_value(top_results[0])

                    average_p.append(p)

                    solver_run.t = t
                    solver_run.p = p
                    solver_run.absolute_difference = sum(abs(a - b) for a, b in zip(top_results[0], sol))
                    print(solver_run.absolute_difference)
                    average_absolute_difference.append(
                        solver_run.absolute_difference
                    )

                    solver_run.solver_result = top_results[0]
                    solver_run.perfect_result = sol
                    solver_run.shots = shots[idx]
                    print(f"{solvers.__name__} p={p}, abs_dif={solver_run.absolute_difference} iterations={len(cost)}")

                    current_result.solverRuns.append(solver_run)
                    
                except Exception as e:
                    print("An exception occurred:", e)
                    print("Failed to run this iteration")


            
            current_result.avg_abs_difference = sum(average_absolute_difference)/len(average_absolute_difference)
            current_result.avg_itirations = sum(average_iterations)/len(average_iterations)
            print(
                f"{solvers.__name__}, layers={layer}, shots={shots[idx]}, iterations={iterations} average p={sum(average_p)/len(average_p)} abs_dif = {current_result.avg_abs_difference} average iterations={current_result.avg_itirations}"
            )
            end_result.append(current_result)
            
        return end_result
