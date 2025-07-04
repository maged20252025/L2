import streamlit as st
import os
import sqlite3
import uuid
import time
import pandas as pd

DATABASE_FILE = os.path.join(os.path.dirname(__file__), "user_data.db")
TRIAL_DURATION = 300 # يجب أن تتطابق مع التطبيق الرئيسي

def init_db():
    """تهيئة قاعدة البيانات وإنشاء الجداول إذا لم تكن موجودة."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            is_activated INTEGER DEFAULT 0,
            trial_start_time REAL,
            last_activity_time REAL,
            activation_code_used TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS activation_codes (
            code TEXT PRIMARY KEY,
            is_used INTEGER DEFAULT 0,
            used_by_user_id TEXT,
            FOREIGN KEY (used_by_user_id) REFERENCES users(user_id)
        )
    ''')
    # جدول طلبات التفعيل الجديدة (يجب أن يكون مطابقاً لـ main.py)
    c.execute('''
        CREATE TABLE IF NOT EXISTS activation_requests (
            request_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            activation_code TEXT,
            request_time REAL NOT NULL,
            status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (activation_code) REFERENCES activation_codes(code)
        )
    ''')
    conn.commit()
    conn.close()

def generate_activation_codes(num_codes):
    """توليد أكواد تفعيل فريدة وإضافتها إلى قاعدة البيانات."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    generated_codes = []
    for _ in range(num_codes):
        code = str(uuid.uuid4()).replace('-', '')[:10].upper() # توليد كود فريد
        try:
            c.execute("INSERT INTO activation_codes (code, is_used) VALUES (?, 0)", (code,))
            generated_codes.append(code)
        except sqlite3.IntegrityError:
            # في حال تكرار الكود (نادراً جداً)، جرب كوداً آخر
            pass
    conn.commit()
    conn.close()
    return generated_codes

def get_all_activation_codes():
    """الحصول على جميع أكواد التفعيل وحالتها."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT code, is_used, used_by_user_id FROM activation_codes")
    codes = c.fetchall()
    conn.close()
    return codes

def get_all_users():
    """الحصول على جميع المستخدمين وحالاتهم."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id, is_activated, trial_start_time, last_activity_time, activation_code_used FROM users")
    users = c.fetchall()
    conn.close()
    return users

def delete_activation_code(code):
    """حذف كود تفعيل من قاعدة البيانات."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM activation_codes WHERE code = ?", (code,))
    conn.commit()
    conn.close()

def reset_user_activation(user_id):
    """إعادة تعيين حالة التفعيل لمستخدم معين."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET is_activated = 0, trial_start_time = NULL, activation_code_used = NULL WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# --- بداية الدوال الجديدة لإدارة الطلبات ---
def get_pending_activation_requests():
    """الحصول على جميع طلبات التفعيل المعلقة."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT request_id, user_id, activation_code, request_time FROM activation_requests WHERE status = 'pending'")
    requests = c.fetchall()
    conn.close()
    return requests

def approve_activation_request(request_id, user_id, activation_code):
    """الموافقة على طلب تفعيل."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    try:
        # 1. تفعيل المستخدم
        c.execute("UPDATE users SET is_activated = 1, activation_code_used = ? WHERE user_id = ?", (activation_code, user_id))
        # 2. تحديث حالة الكود (يجب أن يكون قد تم تعيينه إلى is_used=1 عند الإرسال)
        # هنا نتأكد فقط من ربط المستخدم بالكود بشكل نهائي.
        c.execute("UPDATE activation_codes SET is_used = 1, used_by_user_id = ? WHERE code = ?", (user_id, activation_code))
        # 3. تحديث حالة الطلب
        c.execute("UPDATE activation_requests SET status = 'approved' WHERE request_id = ?", (request_id,))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"حدث خطأ أثناء الموافقة: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def reject_activation_request(request_id, activation_code):
    """رفض طلب تفعيل."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    try:
        # 1. تحديث حالة الكود ليصبح متاحاً مرة أخرى
        c.execute("UPDATE activation_codes SET is_used = 0, used_by_user_id = NULL WHERE code = ?", (activation_code,))
        # 2. تحديث حالة الطلب
        c.execute("UPDATE activation_requests SET status = 'rejected' WHERE request_id = ?", (request_id,))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"حدث خطأ أثناء الرفض: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
# --- نهاية الدوال الجديدة لإدارة الطلبات ---

st.set_page_config(page_title="لوحة تحكم القوانين اليمنية", layout="centered")
st.markdown("<h1 style='text-align: center;'>لوحة تحكم تطبيق القوانين اليمنية</h1>", unsafe_allow_html=True)
# تم تحديث st.experimental_rerun() إلى st.rerun()
st.button("🔄 تحديث البيانات", on_click=lambda: st.rerun())

# تهيئة قاعدة البيانات عند بدء تشغيل لوحة التحكم
init_db()

menu_options = ["توليد أكواد التفعيل", "عرض الأكواد والمستخدمين", "إدارة المستخدمين", "إدارة طلبات التفعيل"]
selected_option = st.sidebar.selectbox("اختر خيارًا:", menu_options)

if selected_option == "توليد أكواد التفعيل":
    st.header("توليد أكواد تفعيل جديدة")
    num_to_generate = st.number_input("عدد الأكواد لتوليدها:", min_value=1, max_value=100, value=1)
    if st.button("توليد وحفظ الأكواد"):
        new_codes = generate_activation_codes(num_to_generate)
        if new_codes:
            st.success(f"تم توليد {len(new_codes)} كود تفعيل جديد:")
            for code in new_codes:
                st.code(code)
            st.info("الرجاء نسخ هذه الأكواد وتوزيعها بعناية.")
        else:
            st.warning("لم يتم توليد أي أكواد جديدة.")

elif selected_option == "عرض الأكواد والمستخدمين":
    st.header("عرض أكواد التفعيل")
    codes_data = get_all_activation_codes()
    if codes_data:
        df_codes = pd.DataFrame(codes_data, columns=["كود التفعيل", "مستخدم", "معرف المستخدم الذي استخدمه"])
        df_codes["مستخدم"] = df_codes["مستخدم"].apply(lambda x: "نعم" if x == 1 else "لا")
        st.dataframe(df_codes, height=300)

        st.subheader("حذف كود تفعيل")
        code_to_delete = st.text_input("أدخل الكود الذي تريد حذفه:")
        if st.button("حذف الكود"):
            if code_to_delete:
                delete_activation_code(code_to_delete.strip())
                st.success(f"تم حذف الكود '{code_to_delete}' بنجاح.")
                st.rerun() 
            else:
                st.warning("الرجاء إدخال كود لحذفه.")
    else:
        st.info("لا توجد أكواد تفعيل حاليًا.")

    st.header("عرض المستخدمين")
    users_data = get_all_users()
    if users_data:
        df_users = pd.DataFrame(users_data, columns=["معرف المستخدم", "مفعل", "وقت بدء التجربة", "آخر نشاط", "الكود المستخدم"])
        df_users["مفعل"] = df_users["مفعل"].apply(lambda x: "نعم" if x == 1 else "لا")
        df_users["وقت بدء التجربة"] = df_users["وقت بدء التجربة"].apply(lambda x: pd.to_datetime(x, unit='s') if x else "N/A")
        df_users["آخر نشاط"] = df_users["آخر نشاط"].apply(lambda x: pd.to_datetime(x, unit='s') if x else "N/A")

        st.dataframe(df_users, height=300)
    else:
        st.info("لا يوجد مستخدمون مسجلون حاليًا.")

elif selected_option == "إدارة المستخدمين":
    st.header("إدارة المستخدمين")
    users_data = get_all_users()
    if users_data:
        df_users = pd.DataFrame(users_data, columns=["معرف المستخدم", "مفعل", "وقت بدء التجربة", "آخر نشاط", "الكود المستخدم"])
        df_users["مفعل"] = df_users["مفعل"].apply(lambda x: "نعم" if x == 1 else "لا")
        df_users["وقت بدء التجربة"] = df_users["وقت بدء التجربة"].apply(lambda x: pd.to_datetime(x, unit='s') if x else "N/A")
        df_users["آخر نشاط"] = df_users["آخر نشاط"].apply(lambda x: pd.to_datetime(x, unit='s') if x else "N/A")
        
        st.dataframe(df_users, height=300)

        st.subheader("إعادة تعيين تفعيل مستخدم")
        user_id_to_reset = st.text_input("أدخل معرف المستخدم لإعادة تعيين التفعيل:")
        if st.button("إعادة تعيين التفعيل"):
            if user_id_to_reset:
                reset_user_activation(user_id_to_reset.strip())
                st.success(f"تم إعادة تعيين تفعيل المستخدم '{user_id_to_reset}' بنجاح.")
                st.rerun()
            else:
                st.warning("الرجاء إدخال معرف المستخدم.")
    else:
        st.info("لا يوجد مستخدمون حاليًا لإدارتهم.")

# --- قسم جديد لإدارة طلبات التفعيل ---
elif selected_option == "إدارة طلبات التفعيل":
    st.header("طلبات التفعيل المعلقة")
    pending_requests = get_pending_activation_requests()

    if pending_requests:
        df_requests = pd.DataFrame(pending_requests, columns=["معرف الطلب", "معرف المستخدم", "كود التفعيل", "وقت الطلب"])
        df_requests["وقت الطلب"] = df_requests["وقت الطلب"].apply(lambda x: pd.to_datetime(x, unit='s'))
        st.dataframe(df_requests, height=300)

        st.subheader("إدارة الطلبات")
        for req in pending_requests:
            request_id, user_id, activation_code, request_time = req
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**المستخدم:** `{user_id}`")
                st.write(f"**الكود:** `{activation_code}`")
                st.write(f"**وقت الطلب:** `{pd.to_datetime(request_time, unit='s')}`")
            with col2:
                if st.button(f"✅ موافقة (ID: {request_id[:4]}...)", key=f"approve_{request_id}"):
                    if approve_activation_request(request_id, user_id, activation_code):
                        st.success(f"تمت الموافقة على طلب المستخدم {user_id[:8]}...")
                        st.rerun()
                    else:
                        st.error("فشل الموافقة.")
            with col3:
                if st.button(f"❌ رفض (ID: {request_id[:4]}...)", key=f"reject_{request_id}"):
                    if reject_activation_request(request_id, activation_code):
                        st.warning(f"تم رفض طلب المستخدم {user_id[:8]}...")
                        st.rerun()
                    else:
                        st.error("فشل الرفض.")
            st.markdown("---") # خط فاصل بين الطلبات
    else:
        st.info("لا توجد طلبات تفعيل معلقة حاليًا.")
