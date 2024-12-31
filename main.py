from src.benchmark.problem_generator import (
    generate_problem_instance,
    generete_problem_list,
)
from src.benchmark import (
    TranspilerBenchmark,
    SolverBenchmark,
    CustomEncoder,
    plot_results_transpilation,
    plot_solver_results,
)
from src.solvers import ClassiqSolver, QiskitSolver
from qiskit.transpiler import CouplingMap
import json
import numpy as np
from qunfold import QUnfolder


problem_params = {
    "num_entries": 80,
    "num_bins": 5,
    "pdf_data": np.random.normal,
    "pdf_data_params": (0.0, 4.2),
    "pdf_smear": np.random.normal,
    "pdf_smear_params": (-0.55, 0.49),
    "efficiency": 0.85,
}

###############
# A Solver Benchmark
###############

solverBenchmark = SolverBenchmark()
qiskit_result = solverBenchmark.run_sovler_bench(
    solvers=QiskitSolver,
    iterations=8,
    problem=problem_params,
    layers=[1, 1, 1, 1, 2, 2, 2, 2],
    shots=[100, 500, 1000, 5000, 100, 500, 1000, 5000],
)

solverBenchmark = SolverBenchmark()
classiq_result = solverBenchmark.run_sovler_bench(
    solvers=ClassiqSolver,
    iterations=8,
    problem=problem_params,
    layers=[1, 1, 1, 1, 2, 2, 2, 2],
    shots=[100, 500, 1000, 5000, 100, 500, 1000, 5000],
)

plot_solver_results(qiskit_result + classiq_result)

# solverBenchmark = SolverBenchmark()
# solverBenchmark.run_sovler_bench(solvers=ClassiqSolver, iterations=5, problem=problem_params, layers=[1], shots=[5000000])

###############
# A Quick execution test
###############

# Generate problem
x, d, R, binning = generate_problem_instance(problem_params, seed=1)
qu_unfolder = QUnfolder(response=R, measured=d, binning=binning, lam=0)

print(qu_unfolder.num_bits)
print(sum(qu_unfolder.num_bits))

# average_p = []
# average_t = []

# for i in range(5):
#     qiskit = ClassiqSolver(qu_unfoler=qu_unfolder)
#     result = qiskit.solve_integer(num_layers=1, num_shots=10000)
#     results = qiskit.get_results_and_print(result, num_shots=10000, print_results=False)
#     print(results[0])
#     sol, cov = qu_unfolder.solve_gurobi_integer()
#     print(sol)

#     p, t = qiskit.get_p_t_value(results[0])
#     average_p.append(p)
#     average_t.append(t)
#     print(f"qiskit p={p}, t={t}")

# print(f"qiskit average p={sum(average_p)/len(average_p)}, t={sum(average_t)/len(average_t)}")

# average_t = []
# average_p = []

# for _ in range(5):
#     classiq = ClassiqSolver(qu_unfoler=qu_unfolder)
#     result = classiq.solve_integer(num_layers=2, num_shots=1000)
#     results = classiq.get_results_and_print(result, num_shots=1000, print=False)
#     print(results[0])
#     sol, cov = qu_unfolder.solve_gurobi_integer()
#     print(sol)

#     p, t = classiq.get_p_t_value(results)
#     average_p.append(p)
#     average_t.append(t)
#     print(f"calssiq p={p}, t={t}")

# print(f"classiq average p={sum(average_p)/len(average_p)}, t={sum(average_t)/len(average_t)}")


###############
# A Quick test to see the size of the problem
###############

# problems = generete_problem_list(nr_of_problems=2,max_entries=100)

# iqm_gates = ["cz",'rx','r', "measure"]
# ibm_gates = ["cz", "id", "rx", "rz", "rzz", "sx", "x"]

# transpiler_benchmark = TranspilerBenchmark()
# benchmarks_qiskit = transpiler_benchmark.run_benchmark(
#     problems,
#     [
#         {},
#         {
#             "coupling_map": CouplingMap().from_heavy_hex(9),
#             "native_gates": ibm_gates,
#             "additional_info": "ibm",
#         },
#         {
#             "coupling_map": CouplingMap().from_grid(12,12),
#             "native_gates": iqm_gates,
#             "additional_info": "iqm",
#         },
#     ],
#     circuit_generator_settings={"solver": "qiskit"},
# )
# benchmarks_classiq = transpiler_benchmark.run_benchmark(
#     problems,
#     [
#         {},
#         {
#             "coupling_map": CouplingMap().from_heavy_hex(9),
#             "native_gates": ibm_gates,
#             "additional_info": "ibm",
#         },
#         {
#             "coupling_map": CouplingMap().from_grid(12,12),
#             "native_gates": iqm_gates,
#             "additional_info": "iqm",
#         },
#     ],
#     circuit_generator_settings={"solver": "classiq"},
# )

# benchmarks = benchmarks_qiskit + benchmarks_classiq

# print(benchmarks[0])

# plot_results_transpilation(benchmarks)

# with open('data.json','w') as file:
#     json.dump(benchmarks, file, cls=CustomEncoder, indent=4)
