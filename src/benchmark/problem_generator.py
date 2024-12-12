import numpy as np
from sklearn.preprocessing import KBinsDiscretizer
from qunfold.utils import normalize_response
from qunfold import QUnfolder
from typing import List


def generate_problem_instance(problem_params, seed):
    np.random.seed(seed)

    # Generate Monte Carlo truth and measured data distributions
    truth_data = problem_params["pdf_data"](
        *problem_params["pdf_data_params"], size=problem_params["num_entries"]
    )
    smearing = problem_params["pdf_smear"](
        *problem_params["pdf_smear_params"], size=problem_params["num_entries"]
    )
    eff_mask = (
        np.random.rand(problem_params["num_entries"]) < problem_params["efficiency"]
    )
    measured_data = (truth_data + smearing)[eff_mask]

    # Define histograms binning by adaptive KMeans algorithm
    kbd = KBinsDiscretizer(
        n_bins=problem_params["num_bins"], encode="ordinal", strategy="kmeans"
    )
    kbd.fit(measured_data.reshape(-1, 1))
    bin_edges = kbd.bin_edges_[0].tolist()
    binning = np.array([-np.inf] + bin_edges + [np.inf])

    # Build truth histogram (x vector) and measured histogram (d vector)
    truth, _ = np.histogram(truth_data, bins=binning)
    measured, _ = np.histogram(measured_data, bins=binning)

    # Build and normalize detector response (R matrix)
    response, _, _ = np.histogram2d(measured_data, truth_data[eff_mask], bins=binning)
    response = normalize_response(response=response, truth_mc=truth)

    return truth, measured, response, binning

# Will return a array of i elements evenly spaced numbers between x and y
def _evenly_spaced_numbers(x, y, i):
    if i < 2:
        raise ValueError("i must be at least 2 to have numbers spaced apart.")
    
    step = (y - x) / (i - 1)
    return [x + step * n for n in range(i)]

def generete_problem_list(
    nr_of_problems=4, min_bins=4, max_bins=8, min_entries=20, max_entries=200, seed=1
)-> List[QUnfolder]:
    bins = _evenly_spaced_numbers(min_bins, max_bins, nr_of_problems)
    entries = _evenly_spaced_numbers(min_entries, max_entries, nr_of_problems)

    problems = []
    
    for i in range(nr_of_problems):
        problem_params = {
            "num_entries": int(entries[i]),
            "num_bins": int(bins[i]),
            "pdf_data": np.random.normal,
            "pdf_data_params": (0.0, 4.2),
            "pdf_smear": np.random.normal,
            "pdf_smear_params": (-0.55, 0.49),
            "efficiency": 0.85,
        }
        
        problems.append(problem_params)
        

    return problems