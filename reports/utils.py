import numpy as np
from regex import regex as re


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


def wrap_text(text, column_width=60):
    char_count = 0
    lines = []
    line = ""
    for word in text.split(" "):
        char_count += len(word)
        line += word + " "
        if char_count >= column_width:
            char_count = 0
            lines.append(line)
            line = ""
    if line:
        lines.append(line)
    return lines


def format_filename(string):
    string = string.lower()
    filename = re.sub(r"[<>:\'\"\/\|?.*]", "", string)
    filename = filename.replace(" ", "_")
    return filename
