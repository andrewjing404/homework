def AIC(y_true, y_hat, coeff_used):
    resid = y_true - y_hat
    sse = sum(resid**2)
    n = len(y_hat)
    return (n*np.log(sse/n) + 2*coeff_used)

def BIC(y_true, y_hat, coeff_used):
    resid = y_true - y_hat
    sse = sum(resid**2)
    n = len(y_hat)
    return (n*np.log(sse/n) + np.log(n)*coeff_used)