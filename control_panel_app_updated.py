
import streamlit as st
import sqlite3
import uuid
import time
import pandas as pd
import os

# ✅ مسار قاعدة البيانات المعدل
DATABASE_FILE = os.path.join(os.path.dirname(__file__), "user_data.db")
TRIAL_DURATION = 300

# ⬇️ بقية الكود يتم نسخه كما هو بدون تغيير
# يرجى لصق باقي الكود الأصلي هنا بعد هذا السطر في مشروعك
