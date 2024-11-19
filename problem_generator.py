import numpy as np
from sklearn.preprocessing import KBinsDiscretizer
from qunfold.utils import normalize_response


def generate_problem_instance(problem_params, seed):
    np.random.seed(seed)

    # Generate Monte Carlo truth and measured data distributions
    truth_data = problem_params["pdf_data"](*problem_params["pdf_data_params"], size=problem_params["num_entries"])
    smearing = problem_params["pdf_smear"](*problem_params["pdf_smear_params"], size=problem_params["num_entries"])
    eff_mask = np.random.rand(problem_params["num_entries"]) < problem_params["efficiency"]
    measured_data = (truth_data + smearing)[eff_mask]

    # Define histograms binning by adaptive KMeans algorithm
    kbd = KBinsDiscretizer(n_bins=problem_params["num_bins"], encode="ordinal", strategy="kmeans")
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
