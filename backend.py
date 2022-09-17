from pathlib import Path
from typing import Optional, Tuple

import fitz
import numpy as np
from gpxplotter import read_gpx_file
from matplotlib import pyplot as plt
from scipy.ndimage import gaussian_filter1d


class Backend:
    def __init__(
        self, background_pdf_path: str, plot_pdf_path: str, merge_pdf_path: str
    ):
        self._background_pdf_path = background_pdf_path
        self._plot_pdf_path = plot_pdf_path
        self._merge_pdf_path = merge_pdf_path

        self._pdf_size: Optional[Tuple[float, float]] = None
        self._gpx_segment: dict = {}

        self._pdf_snip_path = str(Path(self._merge_pdf_path).parent / "pdf_snip.png")

    def input_pdfs_available(self) -> bool:
        if not Path(self.background_pdf_path).exists():
            return False

        if not Path(self.plot_pdf_path).exists():
            return False

        return True

    @property
    def background_pdf_path(self) -> str:
        return self._background_pdf_path

    @property
    def plot_pdf_path(self) -> str:
        return self._plot_pdf_path

    @property
    def merge_pdf_path(self) -> str:
        return self._merge_pdf_path

    @property
    def pdf_snip_path(self) -> str:
        return self._pdf_snip_path

    def set_pdf_size(self) -> None:
        pages = fitz.open(self.background_pdf_path)

        # 72px = 1in
        self._pdf_size = (pages[0].rect.width / 72, pages[0].rect.height / 72)

    @staticmethod
    def load_pdf_byte(file_path: str) -> bytes:
        with open(file_path, "rb") as pdf_file:
            pdf_byte = pdf_file.read()

        return pdf_byte

    def pdf_to_png(self) -> None:
        if Path(self.merge_pdf_path).exists():
            path = self.merge_pdf_path
        elif self.background_pdf_path is not None:
            path = self.background_pdf_path
        else:
            return None

        # To get better resolution
        zoom_x = 2.0  # horizontal zoom
        zoom_y = 2.0  # vertical zoom
        mat = fitz.Matrix(zoom_x, zoom_y)  # zoom factor 2 in each dimension

        doc = fitz.open(path)  # open document
        page = doc[0]
        pix = page.get_pixmap(matrix=mat)  # render page to an image
        pix.save(self.pdf_snip_path)  # store image as a PNG

    def merge_pdfs(self) -> None:
        background = fitz.open(self.background_pdf_path)
        foreground = fitz.open(self.plot_pdf_path)

        page = background.load_page(0)
        page_front = fitz.open()
        page_front.insert_pdf(foreground, from_page=0, to_page=0)
        page.show_pdf_page(
            page.rect,
            page_front,
            pno=0,
            keep_proportion=True,
            overlay=True,
            oc=0,
            rotate=0,
            clip=None,
        )

        background.save(self.merge_pdf_path, encryption=fitz.PDF_ENCRYPT_KEEP)

    def read_gpx(self, gpx_file_path: str) -> None:
        gpx = read_gpx_file(gpx_file_path)

        try:
            track = next(gpx)
        except StopIteration:
            raise ValueError("No track in GPX file.")

        try:
            next(gpx)
            raise ValueError("More than one tracks in GPX file. This not supported!")
        except StopIteration:
            pass

        if len(track["segments"]) > 1:
            raise ValueError("More than one segments in GPX file. This not supported!")

        self._gpx_segment = track["segments"][0]

    def zero_elevation_level(self) -> Optional[float]:
        if self._gpx_segment is not None:
            zero_level = np.min(self._gpx_segment["elevation"]) * 0.95
            return zero_level
        else:
            return None

    def plot(
        self,
        zero_level: float = None,
        label_font_size: int = 20,
        ticks_font_size: int = 16,
        x_label_text: str = "Entfernung - [km]",
        y_label_text: str = "Höhe - [hm]",
        line_width_grid: int = 3,
        bins_x_axis: int = 25,
        bins_y_axis: int = 25,
        left_position_plot: float = 0.05,
        bottom_position_plot: float = 0.05,
        right_position_plot: float = 0.93,
        top_position_plot: float = 0.6,
        filter_sigma: float = 0.0,
        information_text: str = "None",
        information_text_font_size: int = 30,
        x_position_information_text: float = 0.8,
        y_position_information_text: float = 0.2,
        title_text: str = "None",
        title_text_font_size: int = 50,
        x_position_title_text: float = 0.5,
        y_position_title_text: float = 0.9,
        subtitle_text: str = "None",
        subtitle_text_font_size: int = 50,
        x_position_subtitle_text: float = 0.5,
        y_position_subtitle_text: float = 0.8,
    ) -> None:

        fpath = Path(__file__).resolve().parent / "./Itim/Itim-Regular.ttf"

        if self._gpx_segment is None:
            return

        if zero_level is None:
            zero_level = self.zero_elevation_level()

        if filter_sigma == 0:
            elevation_data = self._gpx_segment["elevation"]
        else:
            elevation_data = gaussian_filter1d(
                self._gpx_segment["elevation"], sigma=filter_sigma
            )

        fig = plt.figure(figsize=self._pdf_size)

        plt.grid(
            visible=True, color="gray", linestyle="dashed", linewidth=line_width_grid
        )

        plt.plot(
            self._gpx_segment["Distance / km"],
            elevation_data,
            color="k",
        )

        plt.xlabel(x_label_text, fontsize=label_font_size, fontweight="bold")
        plt.ylabel(y_label_text, fontsize=label_font_size, fontweight="bold")

        ax = plt.gca()
        ax.set_position(
            [
                left_position_plot,
                bottom_position_plot,
                right_position_plot,
                top_position_plot,
            ]
        )

        plt.xlim(0, np.max(self._gpx_segment["Distance / km"]))
        plt.ylim(bottom=zero_level)

        plt.locator_params(axis="x", nbins=bins_x_axis)
        plt.locator_params(axis="y", nbins=bins_y_axis)
        ax.tick_params(axis="both", which="major", labelsize=ticks_font_size)

        plt.fill_between(
            self._gpx_segment["Distance / km"],
            zero_level,
            elevation_data,
            alpha=0.5,
            color="forestgreen",
        )

        ax.text(
            x_position_information_text,
            y_position_information_text,
            information_text,
            size=information_text_font_size,
            transform=fig.transFigure,
            font=fpath,
            ha="center",
            va="center",
        )

        ax.text(
            x_position_title_text,
            y_position_title_text,
            title_text,
            size=title_text_font_size,
            transform=fig.transFigure,
            font=fpath,
            ha="center",
            va="center",
            color=(250 / 255, 67 / 255, 37 / 255),
        )

        ax.text(
            x_position_subtitle_text,
            y_position_subtitle_text,
            subtitle_text,
            size=subtitle_text_font_size,
            transform=fig.transFigure,
            font=fpath,
            ha="center",
            va="center",
        )

        plt.savefig(self.plot_pdf_path, transparent=True)
