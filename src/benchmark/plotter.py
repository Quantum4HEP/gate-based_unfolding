from typing import List
from .result import Result, SolverResults
import matplotlib.pyplot as plt
import datetime

def extract_data(total_result):
    x = []
    y = []
    for item in total_result:
        for key, value in item.items():
            x.append(key)
            y.append(value)
    return x, y

def plot_results_transpilation(results: List[Result]):

    total_result = {}

    for result in results:
        for transpiled in result.transpliedCircuits:
            if (
                f"{result.circuit_creationMode}-{transpiled.additional_info}"
                in total_result
            ):
                total_result[
                    f"{result.circuit_creationMode}-{transpiled.additional_info}"
                ].append({result.problem.num_entries: transpiled.transpiled_depth})
            else:
                total_result[
                    f"{result.circuit_creationMode}-{transpiled.additional_info}"
                ] = [{result.problem.num_entries: transpiled.transpiled_depth}]

    markers = {"qiskit": "o", "classiq": "s", "iqm": "1"}
    line_style = {"qiskit": "-", "classiq": "--", "iqm": "solid"}

    for key, value in total_result.items():
        x, y = extract_data(total_result[key])
        provider = key.split("-", 1)[0]
        plt.plot(
            x, y, label=key, marker=markers[provider], linestyle=line_style[provider]
        )

    # Adding titles and labels
    plt.title("QUnfold Performance Comparison")
    plt.xlabel("Problem size (entries)")
    plt.ylabel("Transpiled circuit depth")

    # Adding a legend
    plt.legend()

    # Showing the plot
    plt.show()


def plot_solver_results(results: List[SolverResults]):

    total_results = {}

    # Step 1: create list of all different possible problem instances
    for solver_result in results:
        if (
            f"{solver_result.solver}-{solver_result.problem['num_entries']}-{solver_result.problem['num_bins']}-{solver_result.layers}"
            in total_results
        ):
            total_results[
                f"{solver_result.solver}-{solver_result.problem['num_entries']}-{solver_result.problem['num_bins']}-{solver_result.layers}"
            ].append({solver_result.shots: solver_result.avg_abs_difference})
        else:
            total_results[
                f"{solver_result.solver}-{solver_result.problem['num_entries']}-{solver_result.problem['num_bins']}-{solver_result.layers}"
            ] = [{solver_result.shots: solver_result.avg_abs_difference}]

    
    # Step 2: plot the results
    for key, value in total_results.items():
        x, y = extract_data(total_results[key])
        plt.plot(
            x, y, label=key
        )

    # Adding titles and labels
    plt.title("QUnfold Performance Comparison")
    plt.xlabel("Nr of shots")
    plt.ylabel("Abs difference")

    # Adding a legend
    plt.legend()

    plt.savefig(f"solver_results {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.png")
    
    try:
        # Showing the plot if there is an interactive session
        plt.show()
    except:
        pass
