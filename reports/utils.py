import numpy as np

def pad_nan(matrix):
    """
    Take a jagged matrix, and convert it into square by filling all rows smaller than the longest with zeros.
    """
    lens = np.array(list(map(len, matrix)))
    mask = np.arange(lens.max()) < lens[:, np.newaxis]
    output = np.empty(mask.shape, dtype=np.float)
    output.fill(np.nan)
    output[mask] = np.concatenate(matrix)
    return output
