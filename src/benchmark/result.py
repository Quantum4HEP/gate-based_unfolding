from typing import List
import json


class Problem:
    def __init__(self, num_entries=0, num_bins=0):
        self.num_entries = num_entries
        self.num_bins = num_bins
        


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
        self.type = 'TranspiledResults'
        self.type = 'Result'
        


class Result:
    def __init__(
        self,
        circuit_creationMode="",
        transpliedCircuits: List[TranspiledResults]=None,
        cx_count=0,
        QAOA_type="",
        QAOA_layers=1,
        width=0,
        problem:Problem=None,
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
        

    def __str__(self) -> str:
        print_string = f"""
Result: 
    cicruit created with: {self.circuit_creationMode}
    QAOA type: {self.QAOA_type}
    QAOA layers: {self.QAOA_layers}
    cx count: {self.cx_count}
    width: {self.width}
Problem:
    number of entries: {self.problem.num_entries}
    number of bins: {self.problem.num_bins}
Transpiled cicuits: 
"""
        for transpiledResult in self.transpliedCircuits:
            print_string = (
                print_string
                + f""" 
Transpiler name: {transpiledResult.transpiler_name}
    Depth: {transpiledResult.transpiled_depth}
    additional info: { transpiledResult.additional_info}
    hardware targe: { transpiledResult.hardware_target}
            """
            )

        return print_string


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (Problem, TranspiledResults, Result)):
            return obj.__dict__
        return super().default(obj)

class CustomDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if 'type' in obj:
            if obj['type'] == 'Problem':
                return Problem.from_dict(obj)
            elif obj['type'] == 'TranspiledResults':
                return TranspiledResults.from_dict(obj)
            elif obj['type'] == 'Result':
                return Result.from_dict(obj)
        return obj
