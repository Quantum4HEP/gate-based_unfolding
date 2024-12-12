from src.benchmark.problem_generator import (
    generate_problem_instance,
    generete_problem_list,
)
from src.benchmark import (
    TranspilerBenchmark,
    CustomEncoder,
    CustomDecoder,
    plot_results,
)
from src.solvers import ClassiqSolver
from qiskit.transpiler import CouplingMap
import json
import numpy as np
from qunfold import QUnfolder


###############
# A Quick execution test
###############


problem_params = {
    "num_entries": 70,
    "num_bins": 5,
    "pdf_data": np.random.normal,
    "pdf_data_params": (0.0, 4.2),
    "pdf_smear": np.random.normal,
    "pdf_smear_params": (-0.55, 0.49),
    "efficiency": 0.85,
}

# Generate problem
x, d, R, binning = generate_problem_instance(problem_params, seed=1)
qu_unfolder = QUnfolder(response=R, measured=d,binning=binning,lam=0)

classiqSolver = ClassiqSolver(qu_unfoler=qu_unfolder)
result = classiqSolver.solve_integer(num_layers=3, num_shots=10000)
results = classiqSolver.get_results_and_print(result, num_shots=10000)

p = classiqSolver.get_p_value(results)
print(p)

###############
# A Quick test to see the size of the problem
###############

# problems = generete_problem_list(nr_of_problems=8,max_entries=1000)

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

# plot_results(benchmarks, ["qiskit"], ["generic", "ibm"])

# with open('data.json','w') as file:
#     json.dump(benchmarks, file, cls=CustomEncoder, indent=4)
