
import streamlit as st
import pandas as pd
import os
import random

st.set_page_config(page_title="لوحة إدارة التطبيق", layout="wide")
st.title("🛠️ لوحة إدارة تطبيق القوانين اليمنية")

# ✅ الدخول تلقائي بدون كلمة مرور
st.success("✅ تم الدخول كمسؤول")

# ----------------------------------------------------
# المستخدمين الذين استخدموا النسخة التجريبية
# ----------------------------------------------------
st.header("📊 مستخدمو النسخة التجريبية")
trial_file = "trial_users.txt"
if os.path.exists(trial_file):
    try:
        df = pd.read_csv(trial_file)
        st.dataframe(df)
        st.download_button("📥 تحميل ملف المستخدمين", data=df.to_csv(index=False), file_name="trial_users.csv")
    except Exception as e:
        st.error("حدث خطأ أثناء قراءة ملف المستخدمين.")
        st.exception(e)
else:
    st.info("لا يوجد أي مستخدمين مسجلين حتى الآن.")

# ----------------------------------------------------
# عرض الأكواد المتبقية
# ----------------------------------------------------
st.header("🔐 الأكواد المتاحة للتفعيل")
codes_file = "activation_codes.txt"
codes = []
if os.path.exists(codes_file):
    with open(codes_file, "r", encoding="utf-8") as f:
        codes = f.read().splitlines()
    st.write(f"عدد الأكواد المتبقية: {len(codes)}")
    st.code("\n".join(codes), language="text")
    st.download_button("📥 تحميل الأكواد", data="\n".join(codes), file_name="activation_codes.txt")
else:
    st.info("لا يوجد ملف أكواد حتى الآن.")

# ----------------------------------------------------
# إضافة أكواد جديدة
# ----------------------------------------------------
st.header("➕ إضافة أكواد تفعيل جديدة")
new_codes = st.text_area("أدخل الأكواد الجديدة (كل كود في سطر منفصل)")

if st.button("إضافة الأكواد"):
    new_list = [c.strip() for c in new_codes.splitlines() if c.strip()]
    if new_list:
        if os.path.exists(codes_file):
            with open(codes_file, "r", encoding="utf-8") as f:
                existing_codes = set(f.read().splitlines())
        else:
            existing_codes = set()

        unique_new = [c for c in new_list if c not in existing_codes]

        with open(codes_file, "a", encoding="utf-8") as f:
            for code in unique_new:
                f.write(code + "\n")
        st.success(f"تمت إضافة {len(unique_new)} كود جديد (تم تجاهل التكرارات).")
        st.experimental_rerun()
    else:
        st.warning("لم يتم إدخال أي كود.")

# ----------------------------------------------------
# توليد أكواد تلقائيًا
# ----------------------------------------------------
st.header("⚙️ توليد أكواد تلقائيًا")
num = st.number_input("عدد الأكواد المراد توليدها", min_value=1, max_value=500, value=10, step=1)
if st.button("توليد الأكواد"):
    generated = [str(random.randint(100000, 999999)) for _ in range(num)]
    with open(codes_file, "a", encoding="utf-8") as f:
        for code in generated:
            f.write(code + "\n")
    st.success(f"✅ تم توليد {num} كود جديد.")
    st.code("\n".join(generated), language="text")
