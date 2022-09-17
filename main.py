import streamlit as st

from backend import Backend

if "pdf_file" not in st.session_state:
    st.session_state.pdf_file = None

if "gpx_file" not in st.session_state:
    st.session_state.gpx_file = None

if "backend" not in st.session_state:
    backend = Backend(
        background_pdf_path="./background.pdf",
        plot_pdf_path="./plot.pdf",
        merge_pdf_path="./merged.pdf",
    )
    st.session_state.backend = backend
else:
    backend = st.session_state.backend

st.title("Plot GPX Distance-Elevation data on a PDF background")


pdf_file = st.file_uploader("Choose your background *.pdf file:", type="pdf")
if pdf_file is not None:
    if pdf_file != st.session_state.pdf_file:
        with open(backend.background_pdf_path, "wb") as f:
            f.write(pdf_file.getbuffer())
        backend.set_pdf_size()
        st.session_state.pdf_file = pdf_file
else:
    st.session_state.pdf_file = None


gpx_file = st.file_uploader("Choose your *.gpx file:", type="gpx")
if gpx_file is not None:
    if gpx_file != st.session_state.gpx_file:
        backend.read_gpx(gpx_file)
        st.session_state.gpx_file = gpx_file
else:
    st.session_state.gpx_file = None

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
            value=int(backend.zero_elevation_level()),  # type: ignore
        )
        x_label_text = st.text_input("X-label text:", value="Entfernung - [km]")
        y_label_text = st.text_input("Y-label text:", value="Höhe - [hm]")

if pdf_file is not None and gpx_file is not None:

    backend.plot(
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

    backend.merge_pdfs()
    backend.pdf_to_png()

    st.image(backend.pdf_snip_path, caption="Preview")

    pdf_name = st.text_input("PDF name:", value="pdf_with_gpx")
    st.download_button(
        label="Download PDF with GPX plot",
        data=backend.load_pdf_byte(backend.merge_pdf_path),
        file_name=f"{pdf_name}.pdf",
        mime="application/octet-stream",
    )
else:
    st.info("Nothing to show. Please select a a background PDF and GPX file.")
