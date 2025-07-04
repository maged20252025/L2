
import streamlit as st
import streamlit.components.v1 as components
from docx import Document
import re
import os
import time
import base64
import sqlite3
import uuid

# ✅ مسار قاعدة البيانات المعدل
DATABASE_FILE = os.path.join(os.path.dirname(__file__), "user_data.db")
TRIAL_DURATION = 300

# ⬇️ بقية الكود يتم نسخه كما هو بدون تغيير
# يرجى لصق باقي الكود الأصلي هنا بعد هذا السطر في مشروعك
