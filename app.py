import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import urllib.parse
import hashlib
import os

# -------------------------------------------------------------
# DATABASE SETUP
# -------------------------------------------------------------
def init_db():
    conn = sqlite3.connect("matharoo_orders.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            city TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            client_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            city TEXT NOT NULL,
            machine_size TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            requirements TEXT,
            status TEXT DEFAULT 'New Inquiry',
            date_submitted TEXT,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')
    conn.commit()
    return conn

conn = init_db()

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# -------------------------------------------------------------
# APP CONFIGURATION & STYLE THEME
# -------------------------------------------------------------
st.set_page_config(page_title="Matharoo Industries | Batala  ,941700731 ", page_icon="⚙️", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size: 42px; font-weight: 800; color: #B45309; text-align: center; margin-bottom: 0px; letter-spacing: 1px; }
    .tagline { font-size: 16px; color: #4B5563; text-align: center; margin-bottom: 30px; font-style: italic; font-weight: 500; }
    .legacy-banner { background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%); padding: 25px; border-radius: 15px; border: 1px solid #F59E0B; height: 100%; display: flex; flex-direction: column; justify-content: center; }
    .legacy-banner h2 { color: #78350F; font-size: 28px; margin-bottom: 15px; font-weight: 700; }
    .legacy-banner p { color: #92400E; font-size: 16px; line-height: 1.6; margin-bottom: 0px; }
    .section-header { font-size: 24px; font-weight: 700; color: #78350F; border-bottom: 3px solid #F59E0B; padding-bottom: 8px; margin-top: 40px; margin-bottom: 25px; text-transform: uppercase; letter-spacing: 0.5px; }
    .machine-card { background-color: #FFFFFF; padding: 20px; border-radius: 12px; border: 1px solid #FEF3C7; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); text-align: center; height: 100%; }
    .machine-card h3 { color: #78350F; font-size: 20px; margin-top: 15px; margin-bottom: 8px; }
    .machine-card p { color: #4B5563; font-size: 14px; margin-bottom: 15px; }
    .price-tag { font-size: 15px; font-weight: 700; color: #D97706; background-color: #FEF3C7; padding: 4px 12px; border-radius: 20px; display: inline-block; }
    .user-profile { background-color: #F0FDF4; border: 1px solid #BBF7D0; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
    .leader-title { color: #78350F; font-size: 18px; font-weight: 700; margin-top: 10px; text-align: center; }
    .leader-subtitle { color: #D97706; font-size: 14px; font-weight: 600; text-align: center; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'user_details' not in st.session_state:
    st.session_state['user_details'] = {}

WHATSAPP_NUMBER = "+917837027280"

# -------------------------------------------------------------
# SIDEBAR CONTROLS
# -------------------------------------------------------------
st.sidebar.markdown("<h2 style='color: #B45309; text-align: center;'>⚙️ MATHAROO</h2>", unsafe_allow_html=True)
st.sidebar.caption("<div style='text-align: center;'> Krishna nagar Batala, Punjab<br><b>Manufacturing Since 1970</b><br><b>mob:- 7837027280,9417007731</b></div>", unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.subheader("👤 Client Account Portal")
if not st.session_state['logged_in']:
    auth_mode = st.sidebar.radio("Account Action:", ["Login", "Sign Up"])
    if auth_mode == "Login":
        login_user = st.sidebar.text_input("Username / Email")
        login_pass = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            cursor = conn.cursor()
            cursor.execute('SELECT password, full_name, phone, city FROM users WHERE username = ?', (login_user,))
            result = cursor.fetchone()
            if result and check_hashes(login_pass, result[0]):
                st.session_state['logged_in'] = True
                st.session_state['user'] = login_user
                st.session_state['user_details'] = {"name": result[1], "phone": result[2], "city": result[3]}
                st.sidebar.success(f"Welcome back!")
                st.rerun()
            else:
                st.sidebar.error("❌ Invalid Username or Password")
    elif auth_mode == "Sign Up":
        new_user = st.sidebar.text_input("Choose Username / Email")
        new_pass = st.sidebar.text_input("Choose Password", type="password")
        new_name = st.sidebar.text_input("Full / Company Name")
        new_phone = st.sidebar.text_input("Phone Number")
        new_city = st.sidebar.text_input("City & State")
        if st.sidebar.button("Create Account"):
            if not new_user or not new_pass or not new_name or not new_phone or not new_city:
                st.sidebar.error("⚠️ All fields are mandatory.")
            else:
                cursor = conn.cursor()
                try:
                    cursor.execute('INSERT INTO users VALUES (?,?,?,?,?)', (new_user, make_hashes(new_pass), new_name, new_phone, new_city))
                    conn.commit()
                    st.sidebar.success("🎉 Account created! Please log in.")
                except sqlite3.IntegrityError:
                    st.sidebar.error("❌ Username already exists.")
else:
    st.sidebar.markdown(f"<div class='user-profile'>🟢 Logged in as:<br><b>{st.session_state['user_details']['name']}</b></div>", unsafe_allow_html=True)
    if st.sidebar.button("Logout Account"):
        st.session_state['logged_in'] = False
        st.session_state['user'] = None
        st.session_state['user_details'] = {}
        st.rerun()

st.sidebar.markdown("---")
nav_options = ["Factory Showroom & Orders"]
if st.session_state['logged_in']:
    nav_options.append("My Orders Tracking")
nav_options.append("Executive Management Panel")
page = st.sidebar.radio("Navigate To:", nav_options)

# -------------------------------------------------------------
# PAGE 1: FACTORY SHOWROOM & ORDERS
# -------------------------------------------------------------
if page == "Factory Showroom & Orders":
    st.markdown('<div class="main-title">MATHAROO INDUSTRIES</div>', unsafe_allow_html=True)
    st.markdown('<div class="tagline">Premium Quality Shaper Machine Manufacturers — Batala, Punjab</div>', unsafe_allow_html=True)
    
    # --- OUR STORY & LEGACY SECTION WITH IMAGE ---
    st.markdown('<div class="section-header">Our Story & Industrial Legacy</div>', unsafe_allow_html=True)
    story_col1, story_col2 = st.columns([1.2, 1])
    
    with story_col1:
        st.markdown("""
            <div class="legacy-banner">
                <h2>Serving the Industry Since the 1970s</h2>
                <p>For over five decades, Matharoo Industries has stood as a pioneer of precision engineering in Batala. 
                We specialize in heavy-duty grade Shaper Machines engineered with heavy-grade seasoned cast iron, high-tensile 
                gearing setups, and robust design practices trusted by machine tool rooms across India. Our commitment to 
                unsurpassed performance ensures that every single machine leaving our floor is ready for lifetime field execution.</p>
            </div>
        """, unsafe_allow_html=True)
        
    with story_col2:
        if os.path.exists("factory_machine.jpg"):
            st.image("factory_machine.jpg", caption="Matharoo Heavy-Duty Shaper Machine Assembly Setup", use_container_width=True)
        else:
            st.warning("ℹ️ To see your machine photo here, place 'factory_machine.jpg' inside your folder.")

    # --- ABOUT US / LEADERSHIP SECTION WITH IMAGES ---
    st.markdown('<div class="section-header">About Us & Leadership Team</div>', unsafe_allow_html=True)
    lead_col1, lead_col2, lead_empty = st.columns([1, 1, 2])
    
    with lead_col1:
        if os.path.exists("dady.jpg"):
            st.image("dady.jpg", use_container_width=True)
        st.markdown('<div class="leader-title">Senior Founder</div>', unsafe_allow_html=True)
        st.markdown('<div class="leader-subtitle">Matharoo Industries</div>', unsafe_allow_html=True)
        
    with lead_col2:
        if os.path.exists("papa.jpg"):
            st.image("papa.jpg", use_container_width=True)
        st.markdown('<div class="leader-title">Managing Director</div>', unsafe_allow_html=True)
        st.markdown('<div class="leader-subtitle">Production Operations Specialist</div>', unsafe_allow_html=True)

    # --- MACHINE CATALOG ---
    st.markdown('<div class="section-header">Our Shaper Machine Catalog</div>', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    machines_data = {
        "12\"": {"desc": "Ideal for Light Tool Rooms & Institutes", "img": "https://5.imimg.com/data5/IA/IL/MY-8543722/shaper-machine-250x250.jpg"},
        "18\"": {"desc": "Standard Workshop Tool Room Grade", "img": "https://encrypted-tbn2.gstatic.com/shopping?q=tbn:ANd9GcQItoC0hlQsVHSurhniKCmTQMykrb8KuJp7BnRaQ9Hk9GvvwLW_zU8TTUzDVc9rCJQDDfY-1s8f6Siv4FTGAtABHzrYuGh1"},
        "24\"": {"desc": "Heavy-Duty Production Machine", "img": "https://2.wlimg.com/product_images/bc-full/dir_17/492608/shaping-machine-1345743.jpg"},
        "30\"": {"desc": "Industrial High-Tensile Machining", "img": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRcpaKcclkIeYCYtuPBVH4LrIDQEBA8m5uPoB-vGBexCaEdKeWjvbqtlQzp&s=10"},
        "36\"": {"desc": "Massive Scale Heavy Enterprise Duty", "img": "https://5.imimg.com/data5/SELLER/Default/2023/2/VD/BK/PE/8543722/36-inch-shapper-machine.jpg"}
    }
    columns_list = [col1, col2, col3, col4, col5]
    for idx, (size, info) in enumerate(machines_data.items()):
        with columns_list[idx]:
            st.image(info["img"], caption=f"{size} Model Overview", use_container_width=True)
            st.markdown(f'<div class="machine-card"><h3>{size} Shaper</h3><p>{info["desc"]}</p><span class="price-tag">Precision Built</span></div>', unsafe_allow_html=True)
            
    # --- ORDER FORM ---
    st.markdown('<div class="section-header">Configure & Place Your Order Now</div>', unsafe_allow_html=True)
    
    default_name = st.session_state['user_details'].get('name', '') if st.session_state['logged_in'] else ''
    default_phone = st.session_state['user_details'].get('phone', '') if st.session_state['logged_in'] else ''
    default_city = st.session_state['user_details'].get('city', '') if st.session_state['logged_in'] else ''
    
    if not st.session_state['logged_in']:
        st.info("💡 Logging in via the sidebar allows you to track your production stages directly over the web dashboard!")

    with st.form("order_booking_form"):
        c1, c2 = st.columns(2)
        with c1:
            c_name = st.text_input("Your Name / Company Name *", value=default_name)
            c_phone = st.text_input("Mobile / WhatsApp Number *", value=default_phone)
            c_city = st.text_input("Delivery Destination City & State *", value=default_city)
        with c2:
            chosen_size = st.selectbox("Select Required Shaper Size *", ["12-Inch Shaper", "18-Inch Shaper", "24-Inch Shaper", "30-Inch Shaper", "36-Inch Shaper"])
            chosen_qty = st.number_input("Required Order Quantity *", min_value=1, max_value=100, value=1)
            custom_notes = st.text_area("Specific Operational Instructions / Custom Details (Optional)")
            
        submit_btn = st.form_submit_button("🔥 ORDER NOW (Send via WhatsApp)")
        
        if submit_btn:
            if not c_name or not c_phone or not c_city:
                st.error("⚠️ Please fill in all required fields.")
            else:
                cursor = conn.cursor()
                time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                username_val = st.session_state['user'] if st.session_state['logged_in'] else 'Guest'
                
                cursor.execute('''
                    INSERT INTO inquiries (username, client_name, phone, city, machine_size, quantity, requirements, date_submitted)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (username_val, c_name, c_phone, c_city, chosen_size, chosen_qty, custom_notes, time_stamp))
                conn.commit()
                
                whatsapp_text = (
                    f"✨ *NEW SHAPER MACHINE ORDER — MATHAROO INDUSTRIES*\n"
                    f"-----------------------------------------------\n"
                    f"🏭 *Legacy:* Manufacturing Quality Since 1970s\n\n"
                    f"👤 *Client Name:* {c_name}\n"
                    f"📞 *Contact Number:* {c_phone}\n"
                    f"📍 *Delivery Destination:* {c_city}\n\n"
                    f"⚙️ *Machine Model:* {chosen_size}\n"
                    f"🔢 *Quantity Demanded:* {chosen_qty} Unit(s)\n"
                    f"📝 *Custom Requirements:* {custom_notes if custom_notes else 'None Specified'}\n\n"
                    f"⏰ _Order logged via Portal at {time_stamp}_"
                )
                encoded_message = urllib.parse.quote(whatsapp_text)
                whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded_message}"
                
                st.success("✅ Order logged inside the central ledger sheet!")
                st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="text-decoration: none;"><div style="background-color: #25D366; color: white; text-align: center; padding: 12px; font-weight: bold; border-radius: 8px; cursor: pointer;">📲 Click Here to Open WhatsApp & Finalize Order Booking</div></a>', unsafe_allow_html=True)

# -------------------------------------------------------------
# PAGE 2: USER ORDERS TRACKING
# -------------------------------------------------------------
elif page == "My Orders Tracking":
    st.markdown('<div class="main-title">Your Order History</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="tagline">Tracking production lines for user: {st.session_state["user"]}</div>', unsafe_allow_html=True)
    
    cursor = conn.cursor()
    cursor.execute("SELECT id, machine_size, quantity, status, date_submitted FROM inquiries WHERE username = ? ORDER BY id DESC", (st.session_state['user'],))
    user_orders = cursor.fetchall()
    
    if len(user_orders) == 0:
        st.info("No orders found under this account profile registry.")
    else:
        df_user = pd.DataFrame(user_orders, columns=["Order ID", "Machine Model", "Quantity", "Current Stage Status", "Date Booked"])
        st.dataframe(df_user, use_container_width=True)

# -------------------------------------------------------------
# PAGE 3: ADMIN DASHBOARD PANEL
# -------------------------------------------------------------
elif page == "Executive Management Panel":
    st.markdown('<div class="main-title" style="color: #1E293B;">Matharoo Command Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="tagline">Internal Order Operations Dashboard</div>', unsafe_allow_html=True)
    
    dashboard_pass = st.sidebar.text_input("Enter Dashboard Password", type="password")
    if dashboard_pass != "batala123":
        st.warning("🔒 Enter security password to view analytical data insights.")
    else:
        st.sidebar.success("Access Verified")
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, client_name, phone, city, machine_size, quantity, requirements, status, date_submitted FROM inquiries ORDER BY id DESC")
        db_entries = cursor.fetchall()
        
        if len(db_entries) == 0:
            st.info("No incoming entries present in the database registry sheet.")
        else:
            df = pd.DataFrame(db_entries, columns=["ID", "Account", "Client Name", "Phone", "Location", "Machine Size", "Qty", "Details", "Status", "Date"])
            
            st.markdown('<div class="section-header">Operational Summary Overview</div>', unsafe_allow_html=True)
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("Total Customer Orders", len(df))
            kpi2.metric("Total Production Units Required", int(df["Qty"].sum()))
            kpi3.metric("Peak Size Velocity", df["Machine Size"].mode()[0] if not df.empty else "N/A")
            
            st.markdown('<div class="section-header">Visual Demand Pipeline Analytics</div>', unsafe_allow_html=True)
            g1, g2 = st.columns(2)
            with g1:
                st.subheader("Size Demand Allocation")
                fig1, ax1 = plt.subplots(figsize=(6, 3.5))
                counts = df['Machine Size'].value_counts()
                ax1.pie(counts, labels=counts.index, autopct='%1.1f%%', colors=sns.color_palette("YlOrBr", len(counts)))
                ax1.axis('equal')
                st.pyplot(fig1)
            with g2:
                st.subheader("Production Lifecycle Summary")
                fig2, ax2 = plt.subplots(figsize=(6, 3.5))
                sns.countplot(data=df, x='Status', palette='YlOrBr', ax=ax2)
                plt.xticks(rotation=15)
                sns.despine()
                st.pyplot(fig2)
                
            st.markdown('<div class="section-header">Central Factory Order Ledger</div>', unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True)
            
            st.markdown('<div class="section-header">Update Order Status Pipeline</div>', unsafe_allow_html=True)
            col_id, col_status, col_btn = st.columns([1, 2, 1])
            with col_id:
                order_id_to_update = st.selectbox("Select Order ID", df["ID"].tolist())
            with col_status:
                new_status = st.selectbox("Assign New Status State", ["New Inquiry", "Contacted / Price Offered", "Advance Payment Received", "Under Production in Factory", "Dispatched / Shipped", "Cancelled"])
            with col_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Apply Status Change"):
                    cursor.execute("UPDATE inquiries SET status = ? WHERE id = ?", (new_status, order_id_to_update))
                    conn.commit()
                    st.success(f"Order #{order_id_to_update} successfully updated to '{new_status}'!")
                    st.rerun()