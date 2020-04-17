import math

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from reports.utils import pad_zeroes

class TVReport:

    def __init__(self, data):
        sns.set()
        self.data = data

    def _get_2d_array(self):
        ratings = []
        for season in self.data:
            episodes = [np.float(episode["rating"]) for episode in season["episodes"] if episode["rating"]]
            ratings.append(episodes)
        return pad_zeroes(np.array(ratings))

    def heatmap(self):
        ratings = self._get_2d_array()
        plt.figure(figsize=(8, 8))
        mean = math.floor(np.concatenate(ratings).mean())
        vmax = min(10, mean+5)
        vmin = max(0, mean-5)
        cmap = sns.cubehelix_palette(light=1, as_cmap=True)
        ax = sns.heatmap(ratings, cmap=cmap, annot=True, square=True, linewidths=3, mask=(ratings==0), vmax=10, vmin=math.floor(ratings[np.nonzero(ratings)].min()));
        plt.show()