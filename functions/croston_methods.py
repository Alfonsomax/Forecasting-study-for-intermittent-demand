import numpy as np

def croston(y_train: np.ndarray, alpha: float = 0.2) -> float:
    nz_idx = np.nonzero(y_train)[0]
    if len(nz_idx) == 0:
        return 0.0

    z = y_train[nz_idx[0]]      # tamaño inicial
    p = nz_idx[0] + 1           # intervalo inicial

    for i in range(1, len(nz_idx)):
        interval = nz_idx[i] - nz_idx[i - 1]
        z = alpha * y_train[nz_idx[i]] + (1 - alpha) * z
        p = alpha * interval + (1 - alpha) * p

    return float(z / p)


def sba(y_train: np.ndarray, alpha: float = 0.2) -> float:
    base = croston(y_train, alpha)
    return float((1 - alpha / 2) * base)


def tsb(y_train: np.ndarray, alpha: float = 0.2, beta: float = 0.2) -> float:
    nz_idx = np.nonzero(y_train)[0]
    if len(nz_idx) == 0:
        return 0.0

    first_idx = nz_idx[0]
    z = y_train[first_idx]
    p = 1.0

    for t in range(first_idx + 1, len(y_train)):
        o_t = 1 if y_train[t] != 0 else 0
        if o_t == 1:
            z = alpha * y_train[t] + (1 - alpha) * z
        p = beta * o_t + (1 - beta) * p

    return float(p * z)






## prueba funcional
""" y = np.array([0, 0, 0, 0, 50, 0, 0, 0, 0, 50, 0, 0, 0, 0, 50])
print(croston(y))  # esperado: cercano a 10
print(sba(y))       # esperado: algo por debajo de croston (corrección de sesgo)
print(tsb(y))        # esperado: en el mismo orden de magnitud

y2 = np.array([0, 0, 3, 0, 0, 0, 5, 0, 4, 0, 0, 0, 0, 0, 7, 0, 0, 2, 0, 0])

print(croston(y2))
print(sba(y2))
print(tsb(y2)) """