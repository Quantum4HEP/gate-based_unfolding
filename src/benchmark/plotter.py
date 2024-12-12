from typing import List
from .result import Result
import matplotlib.pyplot as plt


def plot_results(results: List[Result], unique_providers, unique_tranpilation_options):

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

    # Extracting data for plotting
    def extract_data(total_result):
        x = []
        y = []
        for item in total_result:
            for key, value in item.items():
                x.append(key)
                y.append(value)
        return x, y

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
