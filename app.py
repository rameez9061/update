import streamlit as st
import pandas as pd
import os
from io import BytesIO
import speech_recognition as sr
from pandas_profiling import ProfileReport
import streamlit.components.v1 as components



st.set_page_config(page_title="Data Sweeper", layout="wide")
st.title("Data Sweeper")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning and visualization.")

uploaded_files = st.file_uploader("Upload your files (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"Unsupported file type: {file_ext}")
            continue

        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {file.size/1024:.2f} KB")

        st.write("Preview the Head of DataFrame")
        st.dataframe(df.head())

        # AI-Powered Data Cleaning Insights
        st.subheader("🔍 AI-Powered Data Insights")
        if st.checkbox(f"Generate AI Insights for {file.name}"):
            profile = ProfileReport(df, explorative=True)
            profile.to_file("report.html")
            with open("report.html", "r", encoding="utf-8") as f:
                html_code = f.read()
            components.html(html_code, height=600, scrolling=True)

        # Data Cleaning Options
        st.subheader("🛠 Data Cleaning Options")
        if st.checkbox(f"Clean Data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove Duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("✅ Duplicates Removed!")

            with col2:
                if st.button(f"Fill Missing values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("✅ Missing Values Filled!")

        # Voice Input for Data Commands
        st.subheader("🎙 Voice Input for Data Commands")
        if st.button("Use Voice Command"):
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                st.write("Listening...")
                audio = recognizer.listen(source)

            try:
                command = recognizer.recognize_google(audio).lower()
                st.write(f"🗣 Command received: {command}")

                if "remove duplicates" in command:
                    df.drop_duplicates(inplace=True)
                    st.write("✅ Duplicates Removed!")

                elif "fill missing values" in command:
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("✅ Missing Values Filled!")

                elif "show visualisation" in command:
                    st.bar_chart(df.select_dtypes(include='number').iloc[:, :2])

                else:
                    st.write("⚠️ Command not recognized.")

            except sr.UnknownValueError:
                st.error("Sorry, could not understand the command.")

        # Select Columns to Convert
        st.subheader("📌 Select Columns to Convert")
        columns = st.multiselect(f"Choose columns for {file.name}", df.columns, default=df.columns)
        df = df[columns]

        # Data Visualization
        st.subheader("📊 Data Visualization")
        if st.checkbox(f"Show Visualization for {file.name}"):
            st.bar_chart(df.select_dtypes(include='number').iloc[:, :2])

        # Conversion Options
        st.subheader("🔄 Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)
        buffer = BytesIO()

        if st.button(f"Convert {file.name}"):
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"
            else:
                df.to_excel(buffer, index=False)
                file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            buffer.seek(0)
            st.download_button(label=f"Download {file.name} as {conversion_type}", data=buffer, file_name=file_name, mime=mime_type)



    st.success("🎉 All files processed successfully!")
