import math

import numpy as np
import seaborn as sns
from matplotlib import gridspec, offsetbox, pyplot as plt

from reports.utils import pad_nan, wrap_text


class TVReport:
    def __init__(self, data_provider):
        sns.set(font_scale=0.7)
        self.data = data_provider.seasons
        self.show_metadata = data_provider.show_metadata
        self.ratings = self._get_2d_array()
        self.mean = math.floor(np.nanmean(self.ratings))
        self.median = math.floor(np.nanmedian(self.ratings))
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

        self.season_averages = np.nanmean(self.ratings, axis=axis).reshape(
            average_shape
        )

    @property
    def is_square(self):
        return 1 <= max(self.ratings.shape) / min(self.ratings.shape) < 1.3

    def _get_2d_array(self):
        ratings = []
        for season in self.data:
            episodes = [
                np.float(episode["rating"])
                for episode in season["episodes"]
                if episode["rating"]
            ]
            ratings.append(episodes)
        return pad_nan(np.array(ratings))

    def _setup_page_layout(self, size="A4"):
        size_map = {"A4": (11.69, 8.27), "A3": (16.53, 11.69)}  # (width, height)
        assert size in size_map
        page_width, page_height = size_map[size]
        relative_heights = [1, 5, 2, 2]

        title_params = dict(
            xy=(0.5, 0.7), xycoords="axes fraction", va="center", ha="center", size=32
        )

        subtitle_params = dict(
            xy=(0.5, 0.2), xycoords="axes fraction", va="center", ha="center", size=14
        )

        if self.is_square:
            # Change orientation to portrait
            page_height, page_width = page_width, page_height
            title_params["size"] = 32
            relative_heights = [1, 5, 1, 2]

        fig = plt.figure(
            figsize=(page_width, page_height), dpi=300, constrained_layout=True
        )
        fig.set_size_inches(page_width, page_height)
        spec = gridspec.GridSpec(
            figure=fig, ncols=1, nrows=4, height_ratios=relative_heights
        )
        ep_info = gridspec.GridSpecFromSubplotSpec(1, 5, subplot_spec=spec[3, :])

        with sns.axes_style("dark"):

            title_ax = fig.add_subplot(spec[0, :])
            show_info_ax = fig.add_subplot(spec[2, :])
            misc = fig.add_subplot(ep_info[:, 2])
            best_ep_ax = fig.add_subplot(ep_info[:, :2])
            worst_ep_ax = fig.add_subplot(ep_info[:, 3:])
            for ax in [title_ax, best_ep_ax, worst_ep_ax, show_info_ax, misc]:
                sns.despine(ax=ax, bottom=True, left=True)  # , top=True, right=True)
                ax.axes.xaxis.set_ticks([])
                ax.axes.yaxis.set_ticks([])

        title_ax.annotate(f"{self.show_metadata['title']}", **title_params)
        running_date = self.show_metadata.get(
            "running_date", ""
        )  # running date can be blank
        if running_date:
            title_ax.annotate(f"({running_date})", **subtitle_params)
        self._fill_episode_info(best_ep_ax, cat="best")
        self._fill_episode_info(worst_ep_ax, cat="worst")
        self.page = {
            "fig": fig,
            "axes": [title_ax, best_ep_ax, worst_ep_ax],
            "gridspec": spec,
        }

    def _fill_episode_info(self, ax, cat="best"):
        best = cat == "best"
        info_params = dict(
            xycoords="axes fraction", va="center", ha="left" if best else "right",
        )
        ep_list = self._get_episode(cat=cat)
        horizontal_margin = 0.02 if best else 0.98
        rating = ep_list[0]["rating"]
        rating_box_params = dict()
        rating_color = "#27ae60" if best else "#e74c3c"
        # at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
        # at.patch.set_edgecolor(rating_color)
        # at.patch.set_facecolor(rating_color)
        # ax.add_artist(at)
        title = ax.annotate(
            f"{cat.title()} rated episode(s)",
            xy=(horizontal_margin, 0.8),
            color="#2980b9",
            size=16,
            **info_params,
        )
        title_box = title.get_window_extent(
            renderer=title.get_figure().canvas.get_renderer()
        )
        rating_loc = (title_box.width + 50, 0) if best else (-title_box.width - 50, 0)
        rating = ax.annotate(
            rating,
            xy=(horizontal_margin, 0.8),
            size=14,
            color="w",
            xytext=rating_loc,
            textcoords="offset pixels",
            bbox=dict(boxstyle="round", fc=rating_color),
            **info_params,
        )
        vertical = 0.6
        info_params.update(
            {
                # "ha": "left" if cat == "best" else "right",
                "size": 12,
            }
        )
        vertical_dist = 0.15 if self.is_square else 0.25
        for ep in ep_list:
            title = ep["title"]
            s = ep["season"]
            e = int(ep["episode_number"])
            plot = wrap_text(ep["plot"], 45)
            ax.annotate(
                f"S{s:02d}E{e:02d} - {title}",
                xy=(horizontal_margin, vertical),
                **info_params,
            )
            vertical -= vertical_dist
            if len(ep_list) == 1:
                info_params["size"] = 11
                ep_plot = ax.annotate(
                    "\n".join(plot),
                    xy=(horizontal_margin, vertical),
                    style="italic",
                    **info_params,
                )
                info_params["size"] = 12
                vertical -= 0.1 * len(plot)
            vertical -= 0.05  # Episode differentiation buffer
            if vertical < 0:
                break

    def _get_episode(self, cat="best"):
        criteria = np.nanmax if cat == "best" else np.nanmin
        result = np.where(
            self.ratings == criteria(self.ratings)
        )  # two tuples, with row, column indices respectively
        episode_list = []
        for season, episode in zip(*result):
            if self.inverted:
                episode, season = season, episode  # season will be across columns
            episode_data = self.data[season]["episodes"][episode]
            episode_data["season"] = int(season)
            episode_list.append(episode_data)
        return episode_list

    def heatmap(self, color="red", filename=None):
        colormap = {
            "red": sns.color_palette("YlOrRd", 10),
            "blue": sns.color_palette("YlGnBu", 10),
        }
        height, width = self.ratings.shape
        yticks = np.arange(1, height + 1)
        y_label = "Season"
        xticks = np.arange(1, width + 1)
        x_label = "Episode"
        # Setting up matplotlib and seaborn
        self._setup_page_layout()
        fig = self.page["fig"]

        # Set up heatmap specific layout
        title_ax, best_ep_ax, worst_ep_ax = self.page["axes"]

        if self.inverted:
            main_section = gridspec.GridSpecFromSubplotSpec(
                2,
                2,
                height_ratios=[height, 1],
                width_ratios=[width, 0.1],
                subplot_spec=self.page["gridspec"][1, :],
            )
            main_ax = fig.add_subplot(main_section[0, 0])
            average_ax = fig.add_subplot(main_section[1, 0])
            cbar_ax = fig.add_subplot(main_section[:, 1])
        else:
            main_section = gridspec.GridSpecFromSubplotSpec(
                1,
                3,
                width_ratios=[width, 1, 0.5],
                subplot_spec=self.page["gridspec"][1, :],
            )
            main_ax = fig.add_subplot(main_section[:, 0])
            average_ax = fig.add_subplot(main_section[:, 1])
            cbar_ax = fig.add_subplot(main_section[:, 2])

        main_ax.xaxis.set_ticks_position("top")
        main_ax.xaxis.set_label_position("top")
        average_ax.xaxis.set_ticks_position("top")
        opts = {
            "vmax": 10,  # min(10, median + 3),
            "vmin": math.floor(np.nanmin(self.ratings)),  # max(0, median - 3),
            "cmap": colormap[
                color
            ],  # sns.cubehelix_palette(8, start=2, rot=0, dark=0, light=.95, reverse=True, as_cmap=True),#sns.color_palette("cubehelix_r", 10),
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
        average_opts.update(
            {"yticklabels": False, "xticklabels": ["Average"], "ax": average_ax}
        )
        if self.inverted:
            y_label, x_label = x_label, y_label
            average_opts.update(
                {"yticklabels": ["Average"], "xticklabels": False,}
            )

        average_opts.pop("mask")
        sns.heatmap(self.ratings, **opts)
        sns.heatmap(self.season_averages, **average_opts)
        sm = plt.cm.ScalarMappable(cmap="YlOrRd", norm=plt.Normalize(vmin=0, vmax=1))
        fig.colorbar(main_ax.collections[0], cax=cbar_ax)
        main_ax.set_xlabel(x_label)
        main_ax.set_ylabel(y_label)
        # plt.show()
        if filename is None:
            filename = self.show_metadata["title"].replace(" ", "_").lower()
        fig.savefig(
            f"./data/{filename}.png", dpi=300, bbox_inches="tight", pad_inches=0.2
        )
        plt.close(fig)
        print("Heatmap generated, and saved to file.")
