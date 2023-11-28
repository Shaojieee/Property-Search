import streamlit as st

import os
import sys
sys.path.append('./')


from section_1 import section_1
from section_2 import section_2
from section_1_instruction import section_1_instruction
from section_2_instruction import section_2_instruction

from dotenv import load_dotenv
load_dotenv()

st.set_page_config(layout='wide')

section_1_instruction()
section_1()

if 'best_location' in st.session_state and 'properties' in st.session_state:

    section_2_instruction()
    section_2()