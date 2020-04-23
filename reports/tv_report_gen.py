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

    def heatmap(self, color="red", filename=None):
        colormap = {
            'red': sns.color_palette("YlOrRd", 10),
            'blue': sns.color_palette("YlGnBu", 10),
        }
        height, width = self.ratings.shape
        yticks = np.arange(1, height+1)
        y_label = "Season"
        xticks = np.arange(1, width+1)
        x_label = "Episode"
        # Setting up matplotlib and seaborn
        self._setup_page_layout()
        fig = self.page["fig"]
        
        # Set up heatmap specific layout
        title_ax, footer_ax = self.page["axes"]

        if self.inverted:
            main_section = gridspec.GridSpecFromSubplotSpec(2,2, height_ratios=[height, 1], width_ratios=[width, 0.5], subplot_spec=self.page["gridspec"][1, :])
            main_ax = fig.add_subplot(main_section[0,0])
            cbar_ax = fig.add_subplot(main_section[:,])
        else:
            main_section = gridspec.GridSpecFromSubplotSpec(1,3, width_ratios=[width, 1, 0.5], subplot_spec=self.page["gridspec"][1, :])
            main_ax = fig.add_subplot(main_section[:,0])
            cbar_ax = fig.add_subplot(main_section[:,2])


        main_ax.xaxis.set_ticks_position('top')
        main_ax.xaxis.set_label_position('top')
        opts = {
            "vmax": 10,#min(10, median + 3),
            "vmin": math.floor(self.ratings[np.nonzero(self.ratings)].min()),#max(0, median - 3),
            "cmap": colormap[color],#sns.cubehelix_palette(8, start=2, rot=0, dark=0, light=.95, reverse=True, as_cmap=True),#sns.color_palette("cubehelix_r", 10),
            "mask": (self.ratings == 0),
            "annot": True,
            "square": True,
            "linewidths": 1,
            "xticklabels": xticks,
            "yticklabels": yticks,
            "ax": main_ax,
            "cbar": False
            # "cbar_ax": cbar
        }
        sns.heatmap(self.ratings, **opts);
        sm = plt.cm.ScalarMappable(cmap="YlOrRd", norm=plt.Normalize(vmin=0, vmax=1))
        fig.colorbar(main_ax.collections[0], cax=cbar_ax)
        main_ax.set_xlabel(x_label)
        main_ax.set_ylabel(y_label)
        # plt.show()
        if filename is None: filename = self.show_metadata['title'].replace(" ", "_").lower()
        fig.savefig(f"./data/{filename}.png", dpi=300, bbox_inches="tight", pad_inches=0.4)
        print("Heatmap generated, and saved to file.")
