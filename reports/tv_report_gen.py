import math

import numpy as np
import seaborn as sns
from matplotlib import gridspec, pyplot as plt

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

        # can't use np.mean() or np.average() because we have to ignore non-zero elements in ratings
        self.season_averages = np.true_divide(self.ratings.sum(axis),(self.ratings!=0).sum(axis)).reshape(average_shape) # use count of non zero items to find the average

    @property
    def is_square(self):
        return 1 <  max(self.ratings.shape)/min(self.ratings.shape) < 1.3 

    def _get_2d_array(self):
        ratings = []
        for season in self.data:
            episodes = [np.float(episode["rating"]) for episode in season["episodes"] if episode["rating"]]
            ratings.append(episodes)
        return pad_zeroes(np.array(ratings))

    def _setup_page_layout(self, size="A4"):
        size_map = {
            "A4": (11.69, 8.27), # (width, height)
            "A3": (16.53, 11.69)
        }
        assert size in size_map
        page_width, page_height = size_map[size]
        relative_heights = [1,5,3]
        status = "Not Square"
        optional_params = dict(xy=(0.5, 0.5), 
            xycoords='axes fraction',
            va='center', 
            ha='center')
        if self.is_square: 
            status = "Square"
            # relative_heights = [1,3,5]
            page_height, page_width = page_width, page_height

        fig = plt.figure(figsize=(page_width, page_height), dpi=300, constrained_layout=True)
        fig.set_size_inches(page_width, page_height)
        spec = gridspec.GridSpec(figure=fig, ncols=1, nrows=3, height_ratios=relative_heights)
        title = fig.add_subplot(spec[0, :]).annotate(f"{self.show_metadata['title']}", **optional_params)
        info = fig.add_subplot(spec[2, :]).annotate('Info', **optional_params)
        self.page = {
            "fig": fig,
            "axes": [title, info],
            "gridspec": spec
        }

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
            average_ax = fig.add_subplot(main_section[1,0])
            cbar_ax = fig.add_subplot(main_section[:,])
        else:
            main_section = gridspec.GridSpecFromSubplotSpec(1,3, width_ratios=[width, 1, 0.5], subplot_spec=self.page["gridspec"][1, :])
            main_ax = fig.add_subplot(main_section[:,0])
            average_ax = fig.add_subplot(main_section[:,1])
            cbar_ax = fig.add_subplot(main_section[:,2])


        main_ax.xaxis.set_ticks_position('top')
        main_ax.xaxis.set_label_position('top')
        average_ax.xaxis.set_ticks_position('top')
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
        average_opts = opts.copy()
        average_opts.update({
                "yticklabels": False,
                "xticklabels": ["Average"],
                "ax": average_ax
            })
        if self.inverted: 
            y_label, x_label = x_label, y_label
            average_opts.update({
                "yticklabels": ["Average"],
                "xticklabels": False,
            })

        average_opts.pop("mask")
        sns.heatmap(self.ratings, **opts);
        sns.heatmap(self.season_averages, **average_opts)
        sm = plt.cm.ScalarMappable(cmap="YlOrRd", norm=plt.Normalize(vmin=0, vmax=1))
        fig.colorbar(main_ax.collections[0], cax=cbar_ax)
        main_ax.set_xlabel(x_label)
        main_ax.set_ylabel(y_label)
        # plt.show()
        if filename is None: filename = self.show_metadata['title'].replace(" ", "_").lower()
        fig.savefig(f"./data/{filename}.png", dpi=300, bbox_inches="tight", pad_inches=0.4)
        print("Heatmap generated, and saved to file.")
