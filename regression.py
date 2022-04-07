from data import DataReader
from sklearn.linear_model import LinearRegression

def generate_linear_model_params(training_data):
    if training_data.lower() == "none": return 0, 1
    prob_data = DataReader(training_data).get_probability_data()
    X, y = [], []
    for spread, probability in prob_data:
        X.append([spread])
        y.append([probability])
    reg = LinearRegression(fit_intercept=False).fit(X, y)
    return reg.coef_[0][0] * -1, 1.0