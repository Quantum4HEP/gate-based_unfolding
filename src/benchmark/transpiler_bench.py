from .result import Result, TranspiledResults
from ..solvers.classiq import ClassiqSolver
from ..solvers.qiskit import QiskitSolver
from ..solvers.transpiler import *
from qunfold import QUnfolder
from .problem_generator import generate_problem_instance

from typing import List

class TranspilerBenchmark():
    """A simple class to help running benchmark to compare different transpiled circuits
    """
    def __init__(self) -> None:
        pass
        
    def run_benchmark(self,problems:List[dict],transpile_settings:List[object],circuit_generator_settings:object ={}, seed=1) -> List[Result]:
        """A function to create multiple problem instances and transpile these various instances to specified targets.

        Args:
            problems (List[dict]): The problem defenitions 
            transpile_settings (List[object]): Various transpilation settings, like coupling map and native gates of the target device.
            circuit_generator_settings (object, optional): Settings for the generation of the circuits, like the number of QAOA layers. Defaults to {}.
            seed (int, optional): Seed for the generation of the problem. Defaults to 1.

        Returns:
            List[Result]: A list of the various transpiled results.
        """
        benchResults:List[Result] = []
        
        for problem in problems:
            
            result = Result()
            result.problem.num_bins = problem['num_bins']
            result.problem.num_entries = problem['num_entries']
            result.circuit_creationMode = circuit_generator_settings.get('solver','classiq')
            result.QAOA_layers = 1
            result.QAOA_type = "vanila"
            
            x, d, R, binning = generate_problem_instance(problem, seed=seed)
            qu_unfolder = QUnfolder(response=R, measured=d,binning=binning,lam=0)
            
            quantum_solver = {}
            if circuit_generator_settings.get('solver','classiq') == 'classiq':
                quantum_solver = ClassiqSolver(qu_unfoler=qu_unfolder)
            
            elif circuit_generator_settings.get('solver','classiq') == 'qiskit':
                quantum_solver = QiskitSolver(qu_unfoler=qu_unfolder)
            
            qprogram = quantum_solver._create_quantumcricuit_integer()
            result.width = qprogram.width()
            
            for transpile_setting in transpile_settings:
                transpiled_circ = get_transpiled_circuit_from_quantumProgram(qprogram,coupling_map=transpile_setting.get('coupling_map',None),native_gates=transpile_setting.get('native_gates',['u','cx']))
                
                coupling_map_description = None
                if transpile_setting.get('coupling_map',None) != None:
                    coupling_map_description = f"{transpile_setting.get('coupling_map',None).description}_{transpile_setting.get('coupling_map',None).size()}"
                
                transpiledResults = TranspiledResults()
                transpiledResults.transpiled_depth = transpiled_circ.depth()
                transpiledResults.cx_count = transpiled_circ.count_ops()
                transpiledResults.transpiler_name = "Qiskit"
                transpiledResults.hardware_target = f"coupling_map:{coupling_map_description};native_gates:{transpile_setting.get('native_gates',['u','cx'])}"
                transpiledResults.additional_info = transpile_setting.get('additional_info','generic')
                result.transpliedCircuits.append(transpiledResults)
            
            benchResults.append(result)
            
        return benchResults