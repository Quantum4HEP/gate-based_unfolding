from typing import List
import json


class Problem:
    def __init__(self, num_entries=0, num_bins=0):
        self.num_entries = num_entries
        self.num_bins = num_bins

    def __str__(self):
        lines = [self.__class__.__name__ + ":"]
        for key, val in vars(self).items():
            lines += "{}: {}".format(key, val).split("\n")
        return "\n    ".join(lines)


class TranspiledResults:
    def __init__(
        self,
        transpiler_name="",
        transpiled_depth=0,
        hardware_target="",
        additional_info="",
        ops_count=None,
    ):
        if ops_count is None:
            ops_count = {}
        self.transpiler_name = transpiler_name
        self.transpiled_depth = transpiled_depth
        self.hardware_target = hardware_target
        self.additional_info = additional_info
        self.ops_count = ops_count
        self.type = "TranspiledResults"
        self.type = "Result"

    def __str__(self):
        lines = [self.__class__.__name__ + ":"]
        for key, val in vars(self).items():
            lines += "{}: {}".format(key, val).split("\n")
        return "\n    ".join(lines)


class Result:
    def __init__(
        self,
        circuit_creationMode="",
        transpliedCircuits: List[TranspiledResults] = None,
        cx_count=0,
        QAOA_type="",
        QAOA_layers=1,
        width=0,
        problem: Problem = None,
    ):
        if transpliedCircuits is None:
            transpliedCircuits = []
        if problem is None:
            problem = Problem()
        self.circuit_creationMode = circuit_creationMode
        self.transpliedCircuits = transpliedCircuits
        self.cx_count = cx_count
        self.QAOA_type = QAOA_type
        self.QAOA_layers = QAOA_layers
        self.width = width
        self.problem = problem

    def __str__(self):
        lines = [self.__class__.__name__ + ":"]
        for key, val in vars(self).items():
            if type(val) == list:
                for key_nested, val_nested in enumerate(val):
                    lines += "{}: {}".format(key_nested, val_nested).split("\n")
            else:
                lines += "{}: {}".format(key, val).split("\n")
        return "\n    ".join(lines)


class SolverRun:
    def __init__(self):

        self.p: float
        self.t: float
        self.chi_squared_statistic: float
        self.chi_squared_p: float
        self.solver_result: List[int]
        self.perfect_result: List[int]
        self.absolute_difference: int
        self.solver_final_params: List[float]
        self.solver_costs: List[float]

    def __str__(self):
        lines = [self.__class__.__name__ + ":"]
        for key, val in vars(self).items():
            lines += "{}: {}".format(key, val).split("\n")
        return "\n    ".join(lines)


class SolverResults:
    def __init__(
        self,
        problem: Problem = None,
        solver: str = None,
        iterations: int = 1,
        num_bits: int = 0,
        layers: int = 1,
        shots: int = 1000,
    ):
        if problem is None:
            problem = Problem()
        self.problem = problem
        self.solver = solver
        self.iterations = iterations
        self.num_bits: int = num_bits
        self.solverRuns: List[SolverRun] = []
        self.layers = layers
        self.shots = shots
        self.avg_abs_difference: float = 0
        self.avg_itirations: float = 0

    def __str__(self):
        lines = [self.__class__.__name__ + ":"]
        for key, val in vars(self).items():
            if type(val) == list:
                for key_nested, val_nested in enumerate(val):
                    lines += "{}: {}".format(key_nested, val_nested).split("\n")
            else:
                lines += "{}: {}".format(key, val).split("\n")
        return "\n    ".join(lines)


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (Problem, TranspiledResults, Result)):
            return obj.__dict__
        return super().default(obj)
