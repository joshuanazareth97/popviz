import math

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from reports.utils import pad_zeroes

class TVReport:

    def __init__(self, data_provider):
        sns.set(font_scale=0.7)
        self.data = data_provider.seasons
        self.show_metadata = data_provider.show_metadata
        self.ratings = self._get_2d_array()
        self.mean = math.floor(np.concatenate(self.ratings).mean())
        self.median = math.floor(np.median(np.concatenate(self.ratings)))
        self.n_seasons, self.n_episodes = self.ratings.shape
        self.inverted = False
        axis = 1
        average_shape = (self.n_seasons, 1)
        # Always ensure that the matrix is more or less landscape
        if self.n_seasons > self.n_episodes and not self.is_square:
            # Put seasons make seasons rows
            self.inverted = True
            axis = 0
            self.ratings = self.ratings.transpose()
            average_shape = (1, self.n_seasons)

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