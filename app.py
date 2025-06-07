import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import urllib.parse
import json
from typing import Dict, List
import math

# Configure page
st.set_page_config(
    page_title="شركة المهندس لقطع غيار السيارات",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern design and Arabic support
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif !important;
    }
    
    .main-header {
        text-align: center;
        color: #1e40af;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .new-order-btn {
        display: flex;
        justify-content: center;
        margin: 2rem 0;
    }
    
    .products-table {
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
    }
    
    .table-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        padding: 1rem;
        text-align: center;
    }
    
    .table-row {
        border-bottom: 1px solid #f1f5f9;
        padding: 0.75rem;
        transition: background-color 0.2s ease;
    }
    
    .table-row:hover {
        background-color: #f8fafc;
    }
    
    .table-row:last-child {
        border-bottom: none;
    }
    
    .product-name-cell {
        font-weight: 600;
        color: #1e293b;
        font-size: 1rem;
    }
    
    .origin-cell {
        color: #64748b;
        font-size: 0.9rem;
    }
    
    .price-cell {
        color: #059669;
        font-weight: 600;
        font-size: 1rem;
    }
    
    .subtotal-cell {
        color: #dc2626;
        font-weight: 700;
        font-size: 1.1rem;
    }
    
    .quantity-controls {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0.5rem 0;
    }
    
    .qty-btn {
        background: #3b82f6;
        color: white;
        border: none;
        border-radius: 6px;
        width: 30px;
        height: 30px;
        cursor: pointer;
        font-weight: bold;
    }
    
    .qty-btn:hover {
        background: #2563eb;
    }
    
    .qty-display {
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        padding: 0.25rem 0.75rem;
        min-width: 50px;
        text-align: center;
        font-weight: 600;
    }
    
    .subtotal {
        color: #dc2626;
        font-weight: 700;
        font-size: 1.2rem;
    }
    
    .pagination {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .page-btn {
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .page-btn:hover {
        background: #3b82f6;
        color: white;
    }
    
    .page-btn.active {
        background: #3b82f6;
        color: white;
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
    
    .summary-stats {
        display: flex;
        justify-content: space-around;
        margin: 1rem 0;
    }
    
    .stat-item {
        text-align: center;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        display: block;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
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
    }
    
    .whatsapp-btn:hover {
        background: #128c7e;
        transform: translateY(-2px);
    }
    
    .search-container {
        margin: 2rem 0;
        text-align: center;
    }
    
    .rtl {
        direction: rtl;
        text-align: right;
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
        credentials = Credentials.from_service_account_info(credentials_dict)
        
        # Connect to Google Sheets
        gc = gspread.authorize(credentials)
        sheet_id = st.secrets["google"]["sheet_id"]
        sheet = gc.open_by_key(sheet_id).sheet1
        
        # Get all data
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        # Ensure required columns exist
        required_columns = ['البند', 'المنشأ', 'السعر']
        for col in required_columns:
            if col not in df.columns:
                st.error(f"Missing required column: {col}")
                return pd.DataFrame()
        
        # Convert price to numeric
        df['السعر'] = pd.to_numeric(df['السعر'], errors='coerce').fillna(0)
        
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
    
    message_lines = ["🧾 شركة المهندس لقطع غيار السيارات", "", "طلب جديد:", ""]
    
    for product_name, details in st.session_state.cart.items():
        qty = details['quantity']
        price = details['price']
        subtotal = qty * price
        message_lines.append(f"- {product_name}: {qty} × {price} = {subtotal} جنيه")
    
    total_items, total_cost = get_cart_summary()
    message_lines.extend([
        "",
        f"📦 عدد الأصناف: {total_items}",
        f"✅ الإجمالي: {total_cost} جنيه"
    ])
    
    message = "\n".join(message_lines)
    return urllib.parse.quote(message)

def display_products_table(products_df):
    """Display products in a table format with controls"""
    if products_df.empty:
        st.warning("لا توجد منتجات للعرض")
        return
    
    # Create table header
    st.markdown("""
    <div class="products-table">
        <div style="display: grid; grid-template-columns: 3fr 1fr 1fr 1fr 1fr 1fr; gap: 1rem; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; font-weight: 600;">
            <div class="rtl">البند</div>
            <div class="rtl">المنشأ</div>
            <div class="rtl">السعر</div>
            <div class="rtl">الكمية</div>
            <div class="rtl">التحكم</div>
            <div class="rtl">الإجمالي</div>
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
        
        # Create table row
        col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1, 1, 1])
        
        with col1:
            st.markdown(f'<div class="product-name-cell rtl">{product_name}</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'<div class="origin-cell rtl">{origin}</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown(f'<div class="price-cell">{price} ج.م</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown(f'<div class="qty-display" style="text-align: center; padding: 0.25rem; background: #f1f5f9; border-radius: 4px; font-weight: 600;">{current_qty}</div>', unsafe_allow_html=True)
        
        with col5:
            # Quantity controls in a row
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("➖", key=f"minus_{idx}", help="تقليل الكمية", use_container_width=True):
                    update_quantity(product_name, -1)
                    st.rerun()
            with btn_col2:
                if st.button("➕", key=f"plus_{idx}", help="زيادة الكمية", use_container_width=True):
                    if product_name not in st.session_state.cart:
                        st.session_state.cart[product_name] = {'quantity': 0, 'price': price}
                    update_quantity(product_name, 1)
                    st.rerun()
        
        with col6:
            if subtotal > 0:
                st.markdown(f'<div class="subtotal-cell">{subtotal} ج.م</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="subtotal-cell">-</div>', unsafe_allow_html=True)
        
        # Add row separator
        st.markdown('<div style="border-bottom: 1px solid #f1f5f9; margin: 0.5rem 0;"></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

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
        
        # Search functionality
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        search_query = st.text_input("🔍 البحث في المنتجات", value=st.session_state.search_query, 
                                   placeholder="ابحث عن قطعة غيار...")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Filter data based on search
        if search_query:
            filtered_df = df[df['البند'].str.contains(search_query, case=False, na=False)]
        else:
            filtered_df = df
        
        # Pagination settings
        items_per_page = 10
        total_items = len(filtered_df)
        total_pages = math.ceil(total_items / items_per_page)
        
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
                st.markdown(f'<div style="text-align: center; padding: 0.5rem;">الصفحة {st.session_state.current_page} من {total_pages}</div>', 
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
            
            # Order details
            st.markdown("### 📋 تفاصيل الطلبية")
            for product_name, details in st.session_state.cart.items():
                qty = details['quantity']
                price = details['price']
                subtotal = qty * price
                
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    st.write(f"**{product_name}**")
                with col2:
                    st.write(f"{qty} قطعة")
                with col3:
                    st.write(f"{price} جنيه")
                with col4:
                    st.write(f"**{subtotal} جنيه**")
            
            # WhatsApp send button
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("📱 إرسال الطلبية عبر واتساب", use_container_width=True, type="primary"):
                    whatsapp_number = st.secrets["whatsapp"]["number"]
                    message = generate_whatsapp_message()
                    whatsapp_url = f"https://wa.me/{whatsapp_number}?text={message}"
                    
                    st.success("سيتم فتح واتساب لإرسال الطلبية...")
                    st.markdown(f'<meta http-equiv="refresh" content="1;url={whatsapp_url}">', unsafe_allow_html=True)
                    st.markdown(f"[اضغط هنا إذا لم يتم فتح واتساب تلقائياً]({whatsapp_url})")

if __name__ == "__main__":
    main()
