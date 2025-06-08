import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import urllib.parse
import json
from typing import Dict, List
import math
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="شركة المهندس لقطع غيار السيارات",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern design and Arabic support with improved mobile responsiveness
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif !important;
        box-sizing: border-box;
    }
    
    .main-header {
        text-align: center;
        color: #1e40af;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Mobile-first responsive table container */
    .mobile-table-container {
        width: 100%;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
    }
    
    .products-table {
        min-width: 800px; /* Minimum width to maintain table structure */
        width: 100%;
        background: white;
        border-radius: 12px;
        overflow: hidden;
    }
    
    .table-header {
        display: grid;
        grid-template-columns: 3fr 1.5fr 1.2fr 1fr 1.5fr 1.2fr;
        gap: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        padding: 1rem;
        direction: rtl;
        text-align: center;
        position: sticky;
        top: 0;
        z-index: 10;
    }
    
    .table-row {
        display: grid;
        grid-template-columns: 3fr 1.5fr 1.2fr 1fr 1.5fr 1.2fr;
        gap: 0.5rem;
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #f1f5f9;
        transition: background-color 0.2s ease;
        direction: rtl;
        align-items: center;
        min-height: 60px;
    }
    
    .table-row:last-child {
        border-bottom: none;
    }
    
    .product-name-cell {
        font-weight: 600;
        color: #fffff;
        font-size: 0.95rem;
        text-align: right;
        word-wrap: break-word;
        line-height: 1.4;
    }
    
    .origin-cell {
        color: #ffffff;
        font-size: 0.9rem;
        text-align: center;
    }
    
    .price-cell {
        color: #2f855a;
        font-weight: 600;
        font-size: 0.95rem;
        text-align: center;
    }
    
    .qty-display {
        background: #ffffff;
        border: 2px solid #3b82f6;
        border-radius: 6px;
        padding: 0.25rem;
        text-align: center;
        font-weight: 700;
        color: #2d3748;
        font-size: 0.9rem;
        min-width: 40px;
    }
    
    .control-buttons {
        display: flex;
        gap: 0.25rem;
        justify-content: center;
        align-items: center;
    }
    
    .qty-btn {
        background: #3b82f6;
        color: white;
        border: none;
        border-radius: 4px;
        width: 24px;
        height: 24px;
        cursor: pointer;
        font-weight: bold;
        font-size: 0.8rem;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background-color 0.2s;
    }
    
    .qty-btn:hover {
        background: #2563eb;
    }
    
    .subtotal-cell {
        color: #c53030;
        font-weight: 700;
        font-size: 0.95rem;
        text-align: center;
        background: #fed7d7;
        padding: 0.25rem;
        border-radius: 4px;
    }
    
    .summary-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .summary-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        display: block;
        color: white !important;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
        color: white !important;
    }
    
    .whatsapp-btn {
        background: #25d366;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 1rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
        width: 100%;
        text-decoration: none;
        display: inline-block;
        text-align: center;
    }
    
    .whatsapp-btn:hover {
        background: #128c7e;
        transform: translateY(-2px);
        color: white;
    }
    
    .search-container {
        margin: 2rem 0;
        text-align: center;
    }
    
    .page-info {
        text-align: center; 
        padding: 0.5rem;
        background: #ffffff;
        border: 2px solid #3b82f6;
        border-radius: 8px;
        font-weight: 600;
        color: #1e293b;
    }
    
    .rtl {
        direction: rtl;
        text-align: right;
    }
    
    /* Mobile responsive design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.8rem;
            margin-bottom: 1rem;
        }
        
        .mobile-table-container {
            margin: 0.5rem -1rem; /* Extend to screen edges on mobile */
            border-radius: 0;
        }
        
        .products-table {
            min-width: 700px; /* Reduced minimum width for mobile */
        }
        
        .table-header,
        .table-row {
            grid-template-columns: 2.5fr 1.2fr 1fr 0.8fr 1.2fr 1fr;
            padding: 0.5rem;
            font-size: 0.85rem;
        }
        
        .product-name-cell {
            font-size: 0.85rem;
            line-height: 1.3;
        }
        
        .origin-cell,
        .price-cell {
            font-size: 0.8rem;
        }
        
        .qty-btn {
            width: 20px;
            height: 20px;
            font-size: 0.7rem;
        }
        
        .qty-display {
            font-size: 0.8rem;
            padding: 0.2rem;
            min-width: 35px;
        }
        
        .subtotal-cell {
            font-size: 0.8rem;
            padding: 0.2rem;
        }
        
        .summary-card {
            margin: 0.5rem 0;
            padding: 1rem;
        }
        
        .summary-title {
            font-size: 1.1rem;
        }
        
        .stat-number {
            font-size: 1.5rem;
        }
        
        .whatsapp-btn {
            padding: 0.8rem 1.5rem;
            font-size: 1rem;
        }
    }
    
    @media (max-width: 480px) {
        .table-header,
        .table-row {
            grid-template-columns: 2fr 1fr 0.8fr 0.7fr 1fr 0.8fr;
            padding: 0.4rem;
            font-size: 0.8rem;
            gap: 0.3rem;
        }
        
        .product-name-cell {
            font-size: 0.8rem;
        }
        
        .qty-btn {
            width: 18px;
            height: 18px;
            font-size: 0.6rem;
        }
        
        .qty-display {
            font-size: 0.75rem;
            min-width: 30px;
        }
    }
    
    /* Force table to maintain structure */
    .stColumn {
        min-width: auto !important;
    }
    
    /* Hide JSON preview */
    .stJson {
        display: none;
    }
    
    /* Order details styling */
    .order-detail-row {
        display: grid;
        grid-template-columns: 3fr 1fr 1fr 1fr;
        gap: 1rem;
        padding: 0.75rem;
        border-bottom: 1px solid #e2e8f0;
        align-items: center;
        direction: rtl;
    }
    
    .order-detail-row:last-child {
        border-bottom: none;
    }
    
    .order-detail-item {
        color: #fffff;
        font-weight: 600;
        text-align: right;
    }
    
    .order-detail-qty {
        color: #4a5568;
        text-align: center;
    }
    
    .order-detail-price {
        color: #2f855a;
        font-weight: 600;
        text-align: center;
    }
    
    .order-detail-subtotal {
        color: #c53030;
        font-weight: 700;
        text-align: center;
        background: #fed7d7;
        padding: 0.25rem;
        border-radius: 4px;
    }
    
    @media (max-width: 768px) {
        .order-detail-row {
            grid-template-columns: 2fr 1fr 1fr 1fr;
            gap: 0.5rem;
            padding: 0.5rem;
            font-size: 0.9rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'cart' not in st.session_state:
    st.session_state.cart = {}
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1
if 'show_order_form' not in st.session_state:
    st.session_state.show_order_form = False
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

@st.cache_data
def load_google_sheet():
    """Load data from Google Sheets"""
    try:
        # Get credentials from Streamlit secrets
        credentials_dict = dict(st.secrets["gcp_service_account"])
        
        # Define the required scopes for Google Sheets
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets.readonly',
            'https://www.googleapis.com/auth/drive.readonly'
        ]
        
        # Create credentials with proper scopes
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
        
        # Connect to Google Sheets
        gc = gspread.authorize(credentials)
        sheet_id = st.secrets["google"]["sheet_id"]
        sheet = gc.open_by_key(sheet_id).sheet1
        
        # Get all data
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        # If DataFrame is empty, try getting all values
        if df.empty:
            all_values = sheet.get_all_values()
            if all_values:
                df = pd.DataFrame(all_values[1:], columns=all_values[0])
        
        # Ensure required columns exist
        required_columns = ['البند', 'المنشأ', 'السعر']
        for col in required_columns:
            if col not in df.columns:
                st.error(f"Missing required column: {col}")
                return pd.DataFrame()
        
        # Convert price to numeric, handling Arabic numerals
        df['السعر'] = pd.to_numeric(df['السعر'], errors='coerce').fillna(0)
        
        # Remove empty rows
        df = df.dropna(subset=['البند'])
        df = df[df['البند'] != '']
        
        return df
    except Exception as e:
        st.error(f"Error loading Google Sheet: {str(e)}")
        return pd.DataFrame()

def update_quantity(product_name: str, change: int):
    """Update product quantity in cart"""
    if product_name not in st.session_state.cart:
        st.session_state.cart[product_name] = {'quantity': 0, 'price': 0}
    
    new_quantity = st.session_state.cart[product_name]['quantity'] + change
    st.session_state.cart[product_name]['quantity'] = max(0, new_quantity)
    
    if st.session_state.cart[product_name]['quantity'] == 0:
        del st.session_state.cart[product_name]

def get_cart_summary():
    """Get cart summary statistics"""
    total_items = sum(item['quantity'] for item in st.session_state.cart.values())
    total_cost = sum(item['quantity'] * item['price'] for item in st.session_state.cart.values())
    return total_items, total_cost

def generate_whatsapp_message():
    """Generate WhatsApp message with proper Arabic formatting"""
    if not st.session_state.cart:
        return ""
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message_lines = [
        "🌟 *شركة المهندس لقطع غيار السيارات* 🌟",
        "",
        f"📅 *تاريخ الطلب:* {now}",
        "",
        "📋 *تفاصيل الطلبية:*",
        ""
    ]
    
    # Add products with proper formatting
    for product_name, details in st.session_state.cart.items():
        qty = details['quantity']
        price = details['price']
        subtotal = qty * price
        message_lines.append(f"🔹 *{product_name}*")
        message_lines.append(f"   - الكمية: {qty}")
        message_lines.append(f"   - السعر: {price} ج.م")
        message_lines.append(f"   - الإجمالي: *{subtotal} ج.م*")
        message_lines.append("")
    
    total_items, total_cost = get_cart_summary()
    message_lines.extend([
        "📊 *ملخص الطلبية:*",
        f"   - عدد الأصناف: {total_items}",
        f"   - الإجمالي النهائي: *{total_cost} ج.م*",
        "",
        "شكراً لثقتكم بنا!",
        "سيتم التواصل معكم قريباً لتأكيد الطلبية."
    ])
    
    message = "\n".join(message_lines)
    return urllib.parse.quote(message)

def display_products_table(products_df):
    """Display products in a responsive table format"""
    if products_df.empty:
        st.warning("لا توجد منتجات للعرض")
        return
    
    # Create mobile-responsive table container
    st.markdown('<div class="mobile-table-container">', unsafe_allow_html=True)
    st.markdown('<div class="products-table">', unsafe_allow_html=True)
    
    # Table header
    st.markdown("""
    <div class="table-header">
        <div>البند</div>
        <div>المنشأ</div>
        <div>السعر</div>
        <div>الكمية</div>
        <div>التحكم</div>
        <div>الإجمالي</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display each product row
    for idx, (_, product) in enumerate(products_df.iterrows()):
        product_name = product['البند']
        origin = product['المنشأ']
        price = product['السعر']
        
        # Get current quantity from cart
        current_qty = st.session_state.cart.get(product_name, {}).get('quantity', 0)
        subtotal = current_qty * price if current_qty > 0 else 0
        
        # Update cart with current price
        if product_name in st.session_state.cart:
            st.session_state.cart[product_name]['price'] = price
        
        # Create table row with embedded controls
        st.markdown(f"""
        <div class="table-row">
            <div class="product-name-cell">{product_name}</div>
            <div class="origin-cell">{origin}</div>
            <div class="price-cell">{price} ج.م</div>
            <div class="qty-display">{current_qty}</div>
            <div class="control-buttons">
        """, unsafe_allow_html=True)
        
        # Add quantity control buttons using columns for proper alignment
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➖", key=f"minus_{idx}_{st.session_state.current_page}", 
                        help="تقليل الكمية", use_container_width=True):
                update_quantity(product_name, -1)
                st.rerun()
        with col2:
            if st.button("➕", key=f"plus_{idx}_{st.session_state.current_page}", 
                        help="زيادة الكمية", use_container_width=True):
                if product_name not in st.session_state.cart:
                    st.session_state.cart[product_name] = {'quantity': 0, 'price': price}
                update_quantity(product_name, 1)
                st.rerun()
        
        # Close control buttons div and add subtotal
        subtotal_display = f"{subtotal} ج.م" if subtotal > 0 else "-"
        st.markdown(f"""
            </div>
            <div class="subtotal-cell">{subtotal_display}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def display_order_details():
    """Display order details in a responsive format"""
    if not st.session_state.cart:
        return
    
    st.markdown("### 📋 تفاصيل الطلبية")
    
    # Header row
    st.markdown("""
    <div class="order-detail-row" style="background: #f7fafc; font-weight: 700;">
        <div>المنتج</div>
        <div>الكمية</div>
        <div>السعر</div>
        <div>الإجمالي</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Product rows
    for product_name, details in st.session_state.cart.items():
        qty = details['quantity']
        price = details['price']
        subtotal = qty * price
        
        st.markdown(f"""
        <div class="order-detail-row">
            <div class="order-detail-item">{product_name}</div>
            <div class="order-detail-qty">{qty} قطعة</div>
            <div class="order-detail-price">{price} ج.م</div>
            <div class="order-detail-subtotal">{subtotal} ج.م</div>
        </div>
        """, unsafe_allow_html=True)

def main():
    # Main header
    st.markdown('<h1 class="main-header rtl">شركة المهندس لقطع غيار السيارات 🚗</h1>', unsafe_allow_html=True)
    
    # New Order button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🛒 طلبية جديدة", use_container_width=True, type="primary"):
            st.session_state.show_order_form = True
            st.session_state.cart = {}
            st.session_state.current_page = 1
            st.rerun()
    
    if st.session_state.show_order_form:
        # Load data
        df = load_google_sheet()
        
        if df.empty:
            st.error("لا يمكن تحميل البيانات من Google Sheets")
            return
        
        # Search functionality with filter options
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input("🔍 البحث في المنتجات", 
                                       value=st.session_state.search_query, 
                                       placeholder="ابحث عن قطعة غيار...")
        with col2:
            origin_filter = st.selectbox("تصفية حسب المنشأ", 
                                       ["الكل"] + list(df['المنشأ'].unique()))
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Filter data based on search and origin
        filtered_df = df.copy()
        
        if search_query:
            filtered_df = filtered_df[filtered_df['البند'].str.contains(search_query, case=False, na=False)]
        
        if origin_filter and origin_filter != "الكل":
            filtered_df = filtered_df[filtered_df['المنشأ'] == origin_filter]
        
        # Show results count
        st.markdown(f"**عدد النتائج: {len(filtered_df)} منتج**")
        
        # Pagination settings
        items_per_page = 15
        total_items = len(filtered_df)
        total_pages = math.ceil(total_items / items_per_page) if total_items > 0 else 1
        
        if total_items == 0:
            st.warning("لا توجد منتجات تطابق البحث")
            return
        
        # Ensure current page is valid
        st.session_state.current_page = min(st.session_state.current_page, total_pages)
        st.session_state.current_page = max(st.session_state.current_page, 1)
        
        # Calculate pagination
        start_idx = (st.session_state.current_page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        current_products = filtered_df.iloc[start_idx:end_idx]
        
        # Display products
        st.markdown(f"### المنتجات (الصفحة {st.session_state.current_page} من {total_pages})")
        
        # Display products table
        display_products_table(current_products)
        
        # Pagination controls
        if total_pages > 1:
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
            
            with col1:
                if st.button("⏮️ الأولى", disabled=st.session_state.current_page == 1):
                    st.session_state.current_page = 1
                    st.rerun()
            
            with col2:
                if st.button("⬅️ السابقة", disabled=st.session_state.current_page == 1):
                    st.session_state.current_page -= 1
                    st.rerun()
            
            with col3:
                st.markdown(f'<div class="page-info">الصفحة {st.session_state.current_page} من {total_pages}</div>', 
                          unsafe_allow_html=True)
            
            with col4:
                if st.button("التالية ➡️", disabled=st.session_state.current_page == total_pages):
                    st.session_state.current_page += 1
                    st.rerun()
            
            with col5:
                if st.button("الأخيرة ⏭️", disabled=st.session_state.current_page == total_pages):
                    st.session_state.current_page = total_pages
                    st.rerun()
        
        # Order summary and review
        if st.session_state.cart:
            st.markdown("---")
            
            total_items, total_cost = get_cart_summary()
            
            # Summary cards
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class="summary-card">
                    <div class="summary-title">📦 عدد الأصناف</div>
                    <div class="stat-number">{total_items}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="summary-card">
                    <div class="summary-title">💰 الإجمالي</div>
                    <div class="stat-number">{total_cost}</div>
                    <div class="stat-label">جنيه مصري</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Order details using the new responsive display
            display_order_details()
            
            # WhatsApp send button
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                whatsapp_number = st.secrets["whatsapp"]["number"]
                whatsapp_message = generate_whatsapp_message()
                whatsapp_url = f"https://wa.me/{whatsapp_number}?text={whatsapp_message}"
                
                st.markdown(
                    f'<a href="{whatsapp_url}" target="_blank" class="whatsapp-btn">📱 إرسال الطلبية عبر واتساب</a>',
                    unsafe_allow_html=True
                )

if __name__ == "__main__":
    main()
