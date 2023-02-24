"""Copyright (C) 2022  Sascha Saralajew

Licensed under GNU Affero General Public License (see LICENSE)
"""
import io
from pathlib import Path
from typing import Tuple

import fitz
import numpy as np
import streamlit as st
from gpxplotter import read_gpx_file
from matplotlib import pyplot as plt
from scipy.ndimage import gaussian_filter1d


def zero_elevation_level(gpx_segment) -> float:
    if gpx_segment is None:
        return 0
    else:
        return np.min(gpx_segment["elevation"]) * 0.95


def plot(
    gpx_segment,
    pdf_size: Tuple[float, float],
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
) -> io.BytesIO:
    fpath = Path(__file__).resolve().parent / "./Itim/Itim-Regular.ttf"

    if zero_level is None:
        zero_level = zero_elevation_level(gpx_segment)

    if filter_sigma == 0:
        elevation_data = gpx_segment["elevation"]
    else:
        elevation_data = gaussian_filter1d(gpx_segment["elevation"], sigma=filter_sigma)

    fig = plt.figure(0, figsize=pdf_size)

    plt.grid(visible=True, color="gray", linestyle="dashed", linewidth=line_width_grid)

    plt.plot(
        gpx_segment["Distance / km"],
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

    plt.xlim(0, np.max(gpx_segment["Distance / km"]))
    plt.ylim(bottom=zero_level)

    plt.locator_params(axis="x", nbins=bins_x_axis)
    plt.locator_params(axis="y", nbins=bins_y_axis)
    ax.tick_params(axis="both", which="major", labelsize=ticks_font_size)

    plt.fill_between(
        gpx_segment["Distance / km"],
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

    buf = io.BytesIO()
    plt.savefig(buf, transparent=True, format="pdf")

    return buf


st.title("Plot GPX Distance-Elevation data on a PDF background")


pdf_file = st.file_uploader("Choose your background *.pdf file:", type="pdf")
if pdf_file is not None:
    background_pdf = fitz.open("pdf", pdf_file.getvalue())

    # 72px = 1in
    pdf_size = (background_pdf[0].rect.width / 72, background_pdf[0].rect.height / 72)
else:
    background_pdf = None


gpx_file = st.file_uploader("Choose your *.gpx file:", type="gpx")
if gpx_file is not None:
    gpx = read_gpx_file(gpx_file)

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

    gpx_segment = track["segments"][0]
else:
    gpx_segment = None


with st.sidebar:
    st.header("Modify the settings:")
    with st.expander("Title text settings."):
        title_text = st.text_input("Title text:", value="Downhill XC Race")
        title_text_font_size = st.slider(
            "Font size text:",
            min_value=50,
            max_value=100,
            value=70,
            key="title_text_font_size",
        )
        x_position_title_text = st.number_input(
            "X position of text:",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            key="x_position_title_text",
        )
        y_position_title_text = st.number_input(
            "Y position of text:",
            min_value=0.0,
            max_value=1.0,
            value=0.9,
            key="y_position_title_text",
        )

    with st.expander("Subtitle text settings."):
        subtitle_text = st.text_input(
            "Subtitle text:",
            value="Berlin - Wien",
        )
        subtitle_text_font_size = st.slider(
            "Font size text:",
            min_value=30,
            max_value=80,
            value=60,
            key="subtitle_text_font_size",
        )
        x_position_subtitle_text = st.number_input(
            "X position of text:",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            key="x_position_subtitle_text",
        )
        y_position_subtitle_text = st.number_input(
            "Y position of text:",
            min_value=0.0,
            max_value=1.0,
            value=0.82,
            key="y_position_subtitle_text",
        )

    with st.expander("Information text settings."):
        information_text = st.text_area(
            "Enter text:",
            value="Day 1 - difficult\nBerlin-Chemnitz\n1211 km and 1987 hm",
        )
        information_text_font_size = st.slider(
            "Font size text:",
            min_value=20,
            max_value=60,
            value=36,
            key="information_text_font_size",
        )
        x_position_information_text = st.number_input(
            "X position of text:",
            min_value=0.0,
            max_value=1.0,
            value=0.15,
            key="x_position_information_text",
        )
        y_position_information_text = st.number_input(
            "Y position of text:",
            min_value=0.0,
            max_value=1.0,
            value=0.86,
            key="y_position_information_text",
        )

    with st.expander("Distance-elevation plot settings."):
        left_position_plot = st.number_input(
            "Left position of plot:",
            min_value=0.0,
            max_value=1.0,
            value=0.05,
        )
        bottom_position_plot = st.number_input(
            "Bottom position of plot:",
            min_value=0.0,
            max_value=1.0,
            value=0.05,
        )
        right_position_plot = st.number_input(
            "Right position of plot:",
            min_value=0.0,
            max_value=1.0,
            value=0.93,
        )
        top_position_plot = st.number_input(
            "Top position of plot:",
            min_value=0.0,
            max_value=1.0,
            value=0.6,
        )

        filter_sigma = st.slider(
            "Smoothing of elevation:", min_value=0.0, max_value=10.0, value=0.0
        )
        label_font_size = st.slider(
            "Font size labels:", min_value=10, max_value=50, value=20
        )
        ticks_font_size = st.slider(
            "Font size ticks:", min_value=10, max_value=50, value=16
        )
        line_width_grid = st.slider(
            "Line width grid:", min_value=1, max_value=10, value=3
        )
        bins_x_axis = st.slider(
            "Number of tick's bins x axis:", min_value=10, max_value=50, value=25
        )
        bins_y_axis = st.slider(
            "Number of tick's bins y axis:", min_value=10, max_value=50, value=25
        )

        zero_level = st.number_input(
            "Set the zero elevation level:",
            min_value=0,
            max_value=8848,
            value=int(zero_elevation_level(gpx_segment)),
        )
        x_label_text = st.text_input("X-label text:", value="Entfernung - [km]")
        y_label_text = st.text_input("Y-label text:", value="Höhe - [hm]")

if background_pdf is not None and gpx_segment is not None:

    buf = plot(
        gpx_segment=gpx_segment,
        pdf_size=pdf_size,
        zero_level=zero_level,
        label_font_size=label_font_size,
        ticks_font_size=ticks_font_size,
        x_label_text=x_label_text,
        y_label_text=y_label_text,
        line_width_grid=line_width_grid,
        bins_x_axis=bins_x_axis,
        bins_y_axis=bins_y_axis,
        left_position_plot=left_position_plot,
        bottom_position_plot=bottom_position_plot,
        right_position_plot=right_position_plot,
        top_position_plot=top_position_plot,
        filter_sigma=filter_sigma,
        information_text=information_text,
        information_text_font_size=information_text_font_size,
        x_position_information_text=x_position_information_text,
        y_position_information_text=y_position_information_text,
        title_text=title_text,
        title_text_font_size=title_text_font_size,
        x_position_title_text=x_position_title_text,
        y_position_title_text=y_position_title_text,
        subtitle_text=subtitle_text,
        subtitle_text_font_size=subtitle_text_font_size,
        x_position_subtitle_text=x_position_subtitle_text,
        y_position_subtitle_text=y_position_subtitle_text,
    )

    foreground_pdf = fitz.open("pdf", buf.getvalue())

    page = background_pdf.load_page(0)
    page_front = fitz.open()
    page_front.insert_pdf(foreground_pdf, from_page=0, to_page=0)
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

    doc = background_pdf
    zoom = 2.0
    mat = fitz.Matrix(zoom, zoom)

    page = doc[0]
    pix = page.get_pixmap(matrix=mat)
    st.image(pix.tobytes(), caption="Preview")

    pdf_name = st.text_input("PDF name:", value="pdf_with_gpx")
    st.download_button(
        label="Download PDF with GPX plot",
        data=background_pdf.tobytes(),
        file_name=f"{pdf_name}.pdf",
        mime="application/octet-stream",
    )
else:
    st.info("Nothing to show. Please select a a background PDF and GPX file.")
