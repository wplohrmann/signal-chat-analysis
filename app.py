import re
import sqlite3
from matplotlib import pyplot as plt
import numpy as np
import streamlit as st
import pandas as pd
import os

title = os.environ["APP_TITLE"]
subheader = os.environ["APP_SUBHEADER"]
message_path = os.environ["MESSAGE_PATH"]
big_password = os.environ["PASSWORD"]

password = st.text_input("Password")
if password not in big_password:
    st.stop()

st.title(title)
st.subheader(subheader)

@st.cache
def get_data() -> pd.DataFrame:
    df = pd.read_csv(message_path)
    # Message, Name, Datetime columns
    df["Datetime"] = pd.to_datetime(df["Datetime"])
    df.sort_values("Datetime", ascending=True, inplace=True)
    return df

def num_messages_sent():
    fig, ax = plt.subplots()
    counts = data.groupby("Name").count()["Message"]
    counts.plot.bar(ax=ax)
    ax.set_ylabel("Number of messages")
    ax.set_xlabel("")
    st.write(fig)

def normalised_messages_over_time():
    fig, ax = plt.subplots()
    do_normalise = st.checkbox("Normalise")
    for name, messages in data.groupby("Name"):
        if do_normalise:
            y = np.linspace(0, 1, len(messages))
        else:
            y = 1 + np.arange(len(messages))
        ax.plot(messages["Datetime"], y, label=name)
    ax.legend()
    st.write(fig)

def custom_word_search():
    num_variables = st.number_input("Number of words, phrases etc. to track", min_value=1)
    expressions = []
    is_valid = True
    for i in range(num_variables):
        col0, col1 = st.columns(2)
        expression_type = col0.selectbox("Expression type", options=["Literal", "Regex (search)", "Calculated"], key=f"type_{i}")
        txt = col1.text_input("Expression", key=f"txt_{i}")
        expressions.append((expression_type, txt))
        if txt == "":
            is_valid = False
    do_normalise = st.checkbox("Normalise by total message count")

    if not is_valid:
        st.error("Invalid expression specification")
        st.stop()

    all_counts = []
    for name, messages in data.groupby("Name"):
        e_counts = {}
        for expression_type, txt in expressions:
            if expression_type == "Literal":
                e_counts[txt] = sum(messages["Message"].apply(lambda x: txt in str(x).lower()))
            elif expression_type == "Regex (search)":
                r = re.compile(txt)
                e_counts[txt] = sum(messages["Message"].apply(lambda x: r.search(str(x).lower()) is not None))
            else:
                st.error("Not implemented")
                st.stop()
            if do_normalise:
                e_counts[txt]  = e_counts[txt] / len(messages)
        all_counts.append({**e_counts, "Name": name})
    df = pd.DataFrame(all_counts).set_index("Name")
    fig, ax = plt.subplots()
    df.plot.bar(ax=ax)
    st.write(fig)


data = get_data()

plots = {
    "Number of messages sent": num_messages_sent,
    "Number of messages over time": normalised_messages_over_time,
    "Custom": custom_word_search,
}

plot_key = st.selectbox("Choose a plot", plots.keys())

plots[plot_key]()
