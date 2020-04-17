import numpy as np

def pad_zeroes(matrix):
    """
    Take a jagged matrix, and convert it into square by filling all rows smaller than the longest with zeros.
    """
    lens = np.array(list(map(len, matrix)))
    mask = np.arange(lens.max()) < lens[:, np.newaxis]
    output = np.zeros(mask.shape, dtype=np.float)
    output[mask] = np.concatenate(matrix)
    return output
