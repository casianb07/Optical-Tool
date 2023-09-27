import streamlit as st
import pandas as pd
import plotly.graph_objs as go

import os

initial_folder = "Initial"
final_folder = "Final"


def is_excel_file(filename):
    return filename.lower().endswith(('.xls', '.xlsx'))


def read_excel_file(file_path):
    try:
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        st.error(f"Nu s-a putut citi fișierul {file_path}: {e}")
        return None


def remove_empty_rows_from_df(df):
    return df.dropna(how='all')


def extract_rows_containing_keywords1(df, keywords):
    extracted_rows = []
    white_homogeneity_previous_rows = []
    previous_row = None

    for _, row in df.iterrows():
        if "WhiteHomogeneity".lower() in row.astype(str).str.lower().tolist() and previous_row is not None:
            white_homogeneity_previous_rows.append(previous_row)

        for keyword in keywords:
            if keyword.lower() in row.astype(str).str.lower().tolist():
                extracted_rows.append(row)
                break

        previous_row = row

    return pd.DataFrame(extracted_rows), pd.DataFrame(white_homogeneity_previous_rows)


def extract_rows_containing_keywords2(df, keywords):
    extracted_rows = []
    black_homogeneity_previous_rows = []
    previous_row = None

    for _, row in df.iterrows():
        if "BlackHomogeneity".lower() in row.astype(str).str.lower().tolist() and previous_row is not None:
            black_homogeneity_previous_rows.append(previous_row)

        for keyword in keywords:
            if keyword.lower() in row.astype(str).str.lower().tolist():
                extracted_rows.append(row)
                break

        previous_row = row

    return pd.DataFrame(extracted_rows), pd.DataFrame(black_homogeneity_previous_rows)


def combine_homogeneity(df):
    df.replace('White Homogeneity', 'WhiteHomogeneity', regex=True, inplace=True)
    df.replace('Black Homogeneity', 'BlackHomogeneity', regex=True, inplace=True)


def process_files(uploaded_files, folder_type):
    data = []

    for file in uploaded_files:
        if is_excel_file(file.name):
            df = read_excel_file(file)
            if df is not None:
                cleaned_df = remove_empty_rows_from_df(df)
                combine_homogeneity(cleaned_df)

                spotmeter_white_homogeneity = None
                white_homogeneity_values = None
                spotmeter_black_homogeneity = None
                black_homogeneity_values = None

                keywords = ["Spotmeter #005", "WhiteHomogeneity", "BlackHomogeneity"]

                extracted_rows_df, white_homogeneity_prev_rows_df1 = extract_rows_containing_keywords1(cleaned_df, keywords)
                extracted_rows_df, white_homogeneity_prev_rows_df2 = extract_rows_containing_keywords1(extracted_rows_df, keywords) # we use df2

                for _, row in white_homogeneity_prev_rows_df2.iterrows():
                    if "Spotmeter #005".lower() in row.astype(str).str.lower().tolist():
                        spotmeter_white_homogeneity = row["Unnamed: 4"]
                        break

                for _, row in white_homogeneity_prev_rows_df2.iterrows():
                    if "WhiteHomogeneity".lower() in row.astype(str).str.lower().tolist():
                        white_homogeneity_values = (row["Unnamed: 4"], row["Unnamed: 5"])
                        break

                extracted_rows_df, black_homogeneity_prev_rows_df1 = extract_rows_containing_keywords2(cleaned_df, keywords)
                extracted_rows_df, black_homogeneity_prev_rows_df2 = extract_rows_containing_keywords2(extracted_rows_df, keywords)

                for _, row in black_homogeneity_prev_rows_df2.iterrows():
                    if "Spotmeter #005".lower() in row.astype(str).str.lower().tolist():
                        spotmeter_black_homogeneity = row["Unnamed: 4"]
                        break

                for _, row in black_homogeneity_prev_rows_df2.iterrows():
                    if "BlackHomogeneity".lower() in row.astype(str).str.lower().tolist():
                        black_homogeneity_values = (row["Unnamed: 4"], row["Unnamed: 5"])
                        break

                info = {
                    "file_name": os.path.basename(file.name),
                    "initial_final": folder_type,
                    "spotmeter_white_homogeneity": spotmeter_white_homogeneity,
                    "white_homogeneity_values": white_homogeneity_values,
                    "spotmeter_black_homogeneity": spotmeter_black_homogeneity,
                    "black_homogeneity_values": black_homogeneity_values
                }
                data.append(info)

    return data


def process_files_with_spinner(uploaded_files, folder_type):
    with st.spinner("### **Please wait while your data is processed...**"):
        data = process_files(uploaded_files, folder_type)
    return data


def page1():
    st.title("Black and White")

    col1, col2 = st.columns(2)

    with col1:
        st.write("Drag and drop excel files for **'Initial'** here:")
        initial_uploaded_files = st.file_uploader("", type=["xls", "xlsx"], accept_multiple_files=True,
                                                  key="initial_file_uploader")

    with col2:
        st.write("Drag and drop excel files for **'Final'** here:")
        final_uploaded_files = st.file_uploader("", type=["xls", "xlsx"], accept_multiple_files=True,
                                                key="final_file_uploader")


    if initial_uploaded_files or final_uploaded_files:
        initial_data = []
        final_data = []
        all_data = []

        if initial_uploaded_files:
            initial_data = process_files_with_spinner(initial_uploaded_files, initial_folder)
            all_data.extend(initial_data)

        if final_uploaded_files:
            final_data = process_files_with_spinner(final_uploaded_files, final_folder)
            all_data.extend(final_data)

        combined_data_white = []

        for initial_dut in initial_data:
            dut_name = initial_dut['file_name']
            for final_dut in final_data:
                if final_dut['file_name'] == dut_name:
                    combined_data_white.append({
                        "dut_name": dut_name,
                        "initial_spotmeter_white": initial_dut['spotmeter_white_homogeneity'],
                        "final_spotmeter_white": final_dut['spotmeter_white_homogeneity'],
                    })

        combined_data_black = []

        for initial_dut in initial_data:
            dut_name = initial_dut['file_name']
            for final_dut in final_data:
                if final_dut['file_name'] == dut_name:
                    combined_data_black.append({
                        "dut_name": dut_name,
                        "initial_spotmeter_black": initial_dut['spotmeter_black_homogeneity'],
                        "final_spotmeter_black": final_dut['spotmeter_black_homogeneity']
                    })

        combined_data_white_black = []

        for initial_dut in initial_data:
            dut_name = initial_dut['file_name']
            for final_dut in final_data:
                if final_dut['file_name'] == dut_name:
                    combined_data_white_black.append({
                        "dut_name": dut_name,
                        "initial_spotmeter_black": initial_dut['spotmeter_black_homogeneity'],
                        "initial_spotmeter_white": initial_dut['spotmeter_white_homogeneity'],
                        "final_spotmeter_white": final_dut['spotmeter_white_homogeneity'],
                        "final_spotmeter_black": final_dut['spotmeter_black_homogeneity']
                    })

        combined_data_first_second_value_white = []

        for initial_dut in initial_data:
            dut_name = initial_dut['file_name']
            for final_dut in final_data:
                if final_dut['file_name'] == dut_name:
                    combined_data_first_second_value_white.append({
                        "dut_name": dut_name,
                        "initial_first_value_white": initial_dut['white_homogeneity_values'][0],
                        "initial_second_value_white": initial_dut['white_homogeneity_values'][1],
                        "final_first_value_white": final_dut['white_homogeneity_values'][0],
                        "final_second_value_white": final_dut['white_homogeneity_values'][1]
                    })

        combined_data_first_second_value_black = []

        for initial_dut in initial_data:
            dut_name = initial_dut['file_name']
            for final_dut in final_data:
                if final_dut['file_name'] == dut_name:
                    combined_data_first_second_value_black.append({
                        "dut_name": dut_name,
                        "initial_first_value_black": initial_dut['black_homogeneity_values'][0],
                        "initial_second_value_black": initial_dut['black_homogeneity_values'][1],
                        "final_first_value_black": final_dut['black_homogeneity_values'][0],
                        "final_second_value_black": final_dut['black_homogeneity_values'][1]
                    })

        if all_data:
            st.subheader("Informații DUT:")
            for dut_info in all_data:
                st.write(f"Fișier: {dut_info['file_name']} - {dut_info['initial_final']}")
                st.write(f"Spotmeter #005 WhiteHomogeneity: {dut_info['spotmeter_white_homogeneity']}")
                st.write(f"WhiteHomogeneity first value: {dut_info['white_homogeneity_values'][0]}")
                st.write(f"WhiteHomogeneity second value: {dut_info['white_homogeneity_values'][1]}")
                st.write(f"Spotmeter #005 BlackHomogeneity: {dut_info['spotmeter_black_homogeneity']}")
                st.write(f"BlackHomogeneity first value: {dut_info['black_homogeneity_values'][0]}")
                st.write(f"BlackHomogeneity second value: {dut_info['black_homogeneity_values'][1]}")
                st.write("")  # Line break between entries

        if combined_data_white:        #-------------LUMINANCE WHITE CHART----------------#
            st.subheader("Luminance White Chart:")

            all_chart_data = []

            for dut_info in combined_data_white:
                dut_name = dut_info['dut_name']
                initial_value = dut_info['initial_spotmeter_white']
                final_value = dut_info['final_spotmeter_white']
                sum_values = ((final_value / initial_value) * 100) - 100

                all_chart_data.append({
                    'DUT': dut_name,
                    'Initial Value': initial_value,
                    'Final Value': final_value,
                })

                st.write(f"DUT: {dut_name}")
                st.write(f"Initial Spotmeter #005 WhiteHomogeneity: {initial_value}")
                st.write(f"Final Spotmeter #005 WhiteHomogeneity: {final_value}")
                st.write(f"Deviation White Homogeneity(%): {sum_values}")
                st.write("")  # Line break between entries

            chart_df = pd.DataFrame(all_chart_data)
            fig = go.Figure(data=[
                go.Bar(name='Initial Value', x=chart_df['DUT'], y=chart_df['Initial Value']),
                go.Bar(name='Final Value', x=chart_df['DUT'], y=chart_df['Final Value'])
            ])

            fig.update_layout(barmode='group', xaxis_title='DUT', yaxis_title='Value', width=800, height=400)

            st.write("<div style='display: flex; justify-content: center;'><h3>Luminance White Chart</h3></div>", unsafe_allow_html=True)
            st.plotly_chart(fig)
            st.write("")

        if combined_data_black:     #------------------LUMINANCE BLACK CHART------------------#
            st.subheader("Luminance Black Chart:")

            all_chart_data = []

            for dut_info in combined_data_black:
                dut_name = dut_info['dut_name']
                initial_value = dut_info['initial_spotmeter_black']
                final_value = dut_info['final_spotmeter_black']
                sum_values = ((final_value / initial_value) * 100) - 100

                all_chart_data.append({
                    'DUT': dut_name,
                    'Initial Value': initial_value,
                    'Final Value': final_value,
                })

                st.write(f"DUT: {dut_name}")
                st.write(f"Initial Spotmeter #005 BlackHomogeneity: {initial_value}")
                st.write(f"Final Spotmeter #005 BlackHomogeneity: {final_value}")
                st.write(f"Deviation Black Homogeneity(%): {sum_values}")
                st.write("")  # Line break between entries

            chart_df = pd.DataFrame(all_chart_data)
            fig = go.Figure(data=[
                go.Bar(name='Initial Value', x=chart_df['DUT'], y=chart_df['Initial Value']),
                go.Bar(name='Final Value', x=chart_df['DUT'], y=chart_df['Final Value'])
            ])

            fig.update_layout(barmode='group', xaxis_title='DUT', yaxis_title='Value', width=800, height=400)

            st.write("<div style='display: flex; justify-content: center;'><h3>Luminance Black Chart</h3></div>", unsafe_allow_html=True)
            st.plotly_chart(fig)
            st.write("")

        if combined_data_white_black:        #---------------CONTRAST CHART----------------#
            st.subheader("Contrast Chart:")

            all_chart_data = []

            for dut_info in combined_data_white_black:
                dut_name = dut_info['dut_name']
                initial_value_white = dut_info['initial_spotmeter_white']
                final_value_black = dut_info['final_spotmeter_black']
                final_value_white = dut_info['final_spotmeter_white']
                initial_value_black = dut_info['initial_spotmeter_black']

                x = initial_value_white/initial_value_black
                y = final_value_white/final_value_black

                sum_values = ((y / x) * 100) - 100

                all_chart_data.append({
                    'DUT': dut_name,
                    'Initial Value': x,
                    'Final Value': y,
                })

                st.write(f"DUT: {dut_name}")
                st.write(f"Initial Spotmeter #005 BlackHomogeneity: {initial_value_black}")
                st.write(f"Final Spotmeter #005 BlackHomogeneity: {final_value_black}")
                st.write(f"Initial Spotmeter #005 WhiteHomogeneity: {initial_value_white}")
                st.write(f"Final Spotmeter #005 WhiteHomogeneity: {final_value_white}")
                st.write(f"Initial: {x}")
                st.write(f"Final: {y}")

                st.write(f"Deviation Contrast(%): {sum_values}")
                st.write("")  # Line break between entries

            chart_df = pd.DataFrame(all_chart_data)

            fig = go.Figure()
            for col in chart_df.columns[1:]:
                fig.add_trace(go.Bar(name=col, x=chart_df['DUT'], y=chart_df[col]))

            fig.update_layout(barmode='group', xaxis_title='DUT', yaxis_title='Value', width=800, height=400)

            st.write("<div style='display: flex; justify-content: center;'><h3>Contrast Chart</h3></div>", unsafe_allow_html=True)
            st.plotly_chart(fig)
            st.write("")

        if combined_data_first_second_value_white:          #---------------HOMOGENEITY WHITE CHART----------------#
            st.subheader("Homogeneity (White) Chart:")

            all_chart_data = []

            for dut_info in combined_data_first_second_value_white:
                dut_name = dut_info['dut_name']
                initial_first_value_white = dut_info['initial_first_value_white']
                initial_second_value_white = dut_info['initial_second_value_white']
                final_first_value_white = dut_info['final_first_value_white']
                final_second_value_white = dut_info['final_second_value_white']

                try:
                    initial_first_value_white = float(initial_first_value_white)
                except (ValueError, TypeError):
                    initial_first_value_white = 0

                try:
                    initial_second_value_white = float(initial_second_value_white)
                except (ValueError, TypeError):
                    initial_second_value_white = 0

                try:
                    final_first_value_white = float(final_first_value_white)
                except (ValueError, TypeError):
                    final_first_value_white = 0

                try:
                    final_second_value_white = float(final_second_value_white)
                except (ValueError, TypeError):
                    final_second_value_white = 0

                x = initial_first_value_white / initial_second_value_white if initial_second_value_white != 0 else 0
                y = final_first_value_white / final_second_value_white if final_second_value_white != 0 else 0

                sum_values = ((y / x) * 100) - 100
                if sum_values == -100:
                    sum_values = 0

                all_chart_data.append({
                    'DUT': dut_name,
                    'Initial Value': x,
                    'Final Value': y,
                })

                st.write(f"DUT: {dut_name}")
                st.write(f"Initial first value WhiteHomogeneity: {initial_first_value_white}")
                st.write(f"Initial second value WhiteHomogeneity: {initial_second_value_white}")
                st.write(f"Final first value WhiteHomogeneity: {final_first_value_white}")
                st.write(f"Final second value WhiteHomogeneity: {final_second_value_white}")
                st.write(f"Initial: {x}")
                st.write(f"Final: {y}")

                st.write(f"Deviation White Homogeneity(%): {sum_values}")
                st.write("")  # Line break between entries

            chart_df = pd.DataFrame(all_chart_data)

            fig = go.Figure()
            for col in chart_df.columns[1:]:
                fig.add_trace(go.Bar(name=col, x=chart_df['DUT'], y=chart_df[col]))

            fig.update_layout(barmode='group', xaxis_title='DUT', yaxis_title='Value', width=800, height=400)

            st.write("<div style='display: flex; justify-content: center;'><h3>Homogeneity (White) Chart</h3></div>", unsafe_allow_html=True)
            st.plotly_chart(fig)
            st.write("")

        if combined_data_first_second_value_black:          #---------------HOMOGENEITY BLACK CHART----------------#
            st.subheader("Homogeneity (Black) Chart:")

            all_chart_data = []

            for dut_info in combined_data_first_second_value_black:
                dut_name = dut_info['dut_name']
                initial_first_value_black = dut_info['initial_first_value_black']
                initial_second_value_black = dut_info['initial_second_value_black']
                final_first_value_black = dut_info['final_first_value_black']
                final_second_value_black = dut_info['final_second_value_black']


                try:
                    initial_first_value_black = float(initial_first_value_black)
                except (ValueError, TypeError):
                    initial_first_value_black = 0

                try:
                    initial_second_value_black = float(initial_second_value_black)
                except (ValueError, TypeError):
                    initial_second_value_black = 0

                try:
                    final_first_value_black = float(final_first_value_black)
                except (ValueError, TypeError):
                    final_first_value_black = 0

                try:
                    final_second_value_black = float(final_second_value_black)
                except (ValueError, TypeError):
                    final_second_value_black = 0

                x = initial_first_value_black / initial_second_value_black if initial_second_value_black != 0 else 0
                y = final_first_value_black / final_second_value_black if final_second_value_black != 0 else 0

                sum_values = ((y / x) * 100) - 100
                if sum_values == -100:
                    sum_values = 0

                all_chart_data.append({
                    'DUT': dut_name,
                    'Initial Value': x,
                    'Final Value': y,
                })

                st.write(f"DUT: {dut_name}")
                st.write(f"Initial first value BlackHomogeneity: {initial_first_value_black}")
                st.write(f"Initial second value BlackHomogeneity: {initial_second_value_black}")
                st.write(f"Final first value BlackHomogeneity: {final_first_value_black}")
                st.write(f"Final second value BlackHomogeneity: {final_second_value_black}")
                st.write(f"Initial: {x}")
                st.write(f"Final: {y}")

                st.write(f"Deviation Black Homogeneity(%): {sum_values}")
                st.write("")  # Line break between entries

            chart_df = pd.DataFrame(all_chart_data)

            fig = go.Figure()
            for col in chart_df.columns[1:]:
                fig.add_trace(go.Bar(name=col, x=chart_df['DUT'], y=chart_df[col]))

            fig.update_layout(barmode='group', xaxis_title='DUT', yaxis_title='Value', width=800, height=400)

            st.write("<div style='display: flex; justify-content: center;'><h3>Homogeneity (Black) Chart</h3></div>",
                     unsafe_allow_html=True)
            st.plotly_chart(fig)
            st.write("")



def main():
    st.sidebar.title("Meniu")
    page = st.sidebar.radio("Navigare", ["Black and White", "Color"])

    if page == "Black and White":
        page1()
    elif page == "Color":
        st.write("pagina 2")


if __name__ == "__main__":
    main()
