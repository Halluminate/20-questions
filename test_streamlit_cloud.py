# #! /usr/bin/env python3

import os
import copy

import streamlit as st
from typing import Generator


st.set_page_config(page_icon="💬", layout="wide",
                   page_title="20 Questions")


st.write(st.secrets)



def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )
icon("💬")

st.header("20 Questions")
st.subheader("Are you smarter than a large language model?", divider="rainbow", anchor=False)

