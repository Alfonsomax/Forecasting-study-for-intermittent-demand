import numpy as np

def scale_mae(y_train: np.ndarray) -> float:
    return float(np.mean(np.abs(np.diff(y_train))))

def scale_mse(y_train: np.ndarray) -> float:
    return float(np.mean(np.diff(y_train) ** 2))

def mase(y_real: np.ndarray, y_pred: np.ndarray, scales: np.ndarray) -> float:
    errors = np.abs(np.asarray(y_real) - np.asarray(y_pred))
    return float(np.mean(errors / scales))

def rmsse(y_real: np.ndarray, y_pred: np.ndarray, scales2: np.ndarray) -> float:
    errors2 = (np.asarray(y_real) - np.asarray(y_pred)) ** 2
    return float(np.sqrt(np.mean(errors2 / scales2)))

def cfe(y_real: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sum(np.asarray(y_real) - np.asarray(y_pred)))



## prueba funcional
""" y_real = [15, 17]
y_pred = [13, 16]
scales = [2.0, 2.0]
scales2 = [4.0, 4.0]

print(mase(y_real, y_pred, scales))    # expected: 0.75
print(rmsse(y_real, y_pred, scales2))  # expected: ≈0.7906
print(cfe(y_real, y_pred))             # expected: 3.0 """