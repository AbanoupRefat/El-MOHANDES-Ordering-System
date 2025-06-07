import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import urllib.parse
import json
from typing import Dict, List
import math

# Page config
st.set_page_config(
    page_title="شركة المهندس لقطع غيار السيارات",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for RTL and Arabic styling
st.markdown("""
<style>
    .main > div {
        direction: rtl;
        text-align: right;
    }
    
    .stButton > button {
        direction: rtl;
        width: 100%;
        background-color: #0066cc;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-size: 16px;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background-color: #0052a3;
    }
    
    .main-title {
        text-align: center;
        color: #0066cc;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
        direction: rtl;
    }
    
    .search-box {
        direction: rtl;
        text-align: right;
    }
    
    .product-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 12px;
        padding: 16px;
        margin: 10px 0;
        direction: rtl;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .product-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    
    .product-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 12px;
        flex-wrap: wrap;
        gap: 12px;
    }
    
    .product-info {
        flex: 1;
        min-width: 200px;
    }
    
    .product-name {
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 6px;
        color: #333;
        line-height: 1.4;
    }
    
    .product-origin {
        font-size: 13px;
        color: #666;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    .product-price {
        font-weight: bold;
        color: #0066cc;
        font-size: 15px;
    }
    
    .quantity-controls {
        display: flex;
        align-items: center;
        background-color: white;
        border: 2px solid #e9ecef;
        border-radius: 25px;
        padding: 4px;
        min-width: 140px;
        justify-content: center;
    }
    
    .qty-btn {
        background-color: #0066cc;
        color: white;
        border: none;
        border-radius: 50%;
        width: 32px;
        height: 32px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
        user-select: none;
    }
    
    .qty-btn:hover {
        background-color: #0052a3;
        transform: scale(1.1);
    }
    
    .qty-btn:active {
        transform: scale(0.95);
    }
    
    .qty-btn:disabled {
        background-color: #ccc;
        cursor: not-allowed;
        transform: none;
    }
    
    .qty-display {
        min-width: 40px;
        text-align: center;
        font-weight: bold;
        font-size: 16px;
        color: #333;
        margin: 0 8px;
    }
    
    .product-footer {
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid #e9ecef;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
    }
    
    .subtotal {
        font-size: 14px;
        color: #28a745;
        font-weight: bold;
        background-color: #d4edda;
        padding: 4px 8px;
        border-radius: 4px;
    }
    
    .category-header {
        background: linear-gradient(135deg, #0066cc, #004499);
        color: white;
        padding: 16px 20px;
        border-radius: 12px;
        margin: 24px 0 16px 0;
        text-align: center;
        font-weight: bold;
        font-size: 18px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .summary-card {
        background: linear-gradient(135deg, #f0f2f6, #e9ecef);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        text-align: center;
        direction: rtl;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .pagination-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 12px;
        margin: 24px 0;
        padding: 16px;
        background-color: #f8f9fa;
        border-radius: 12px;
        direction: ltr;
    }
    
    .pagination-btn {
        background-color: #0066cc;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        cursor: pointer;
        font-size: 14px;
        font-weight: bold;
        transition: all 0.2s ease;
    }
    
    .pagination-btn:hover {
        background-color: #0052a3;
        transform: translateY(-1px);
    }
    
    .pagination-btn:disabled {
        background-color: #ccc;
        cursor: not-allowed;
        transform: none;
    }
    
    .pagination-info {
        background-color: white;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: bold;
        color: #333;
        border: 2px solid #0066cc;
    }
    
    .empty-state {
        text-align: center;
        padding: 40px 20px;
        color: #666;
        font-size: 16px;
    }
    
    .floating-summary {
        position: sticky;
        bottom: 20px;
        background: linear-gradient(135deg, #0066cc, #004499);
        color: white;
        padding: 12px 20px;
        border-radius: 25px;
        margin: 20px 0;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 100;
    }
    
    /* Mobile optimizations */
    @media (max-width: 768px) {
        .product-header {
            flex-direction: column;
            align-items: stretch;
        }
        
        .product-info {
            text-align: right;
            margin-bottom: 12px;
        }
        
        .quantity-controls {
            align-self: center;
        }
        
        .main-title {
            font-size: 1.8rem;
        }
        
        .product-footer {
            flex-direction: column;
            align-items: stretch;
            text-align: center;
        }
        
        .pagination-container {
            flex-wrap: wrap;
            gap: 8px;
        }
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #0066cc;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #0052a3;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'show_products' not in st.session_state:
    st.session_state.show_products = False
if 'quantities' not in st.session_state:
    st.session_state.quantities = {}
if 'products_data' not in st.session_state:
    st.session_state.products_data = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0
if 'search_term' not in st.session_state:
    st.session_state.search_term = ""
if 'show_review' not in st.session_state:
    st.session_state.show_review = False
if 'items_per_page' not in st.session_state:
    st.session_state.items_per_page = 10

# Google Sheets configuration
SHEET_URL = st.secrets["google"]["sheet_id"] # Replace with your actual sheet ID
WHATSAPP_NUMBER = st.secrets["whatsapp"]["number"] # Replace with actual WhatsApp number

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_google_sheet_data_real():
    """Load data from real Google Sheets - Use this when API is set up"""
    try:
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
        )
        
        gc = gspread.authorize(credentials)
        sheet = gc.open_by_key(SHEET_URL).sheet1
        data = sheet.get_all_records()
        
        # Convert to DataFrame and ensure correct column names
        df = pd.DataFrame(data)
        return df
        
    except Exception as e:
        st.error(f"خطأ في تحميل البيانات من Google Sheets: {str(e)}")
        return pd.DataFrame()

def process_data_with_categories(df):
    """Process data to identify categories based on separators"""
    if df.empty:
        return []
    
    categories = []
    current_category = []
    category_name = "المنتجات"  # Default category name
    
    for idx, row in df.iterrows():
        if row.get('is_separator', False):
            # If we have items in current category, save it
            if current_category:
                categories.append({
                    'name': category_name,
                    'items': current_category.copy()
                })
                current_category = []
            
            # Look for the next non-empty row to determine category name
            next_items = df[idx+1:idx+10]  # Look ahead a few rows
            non_empty = next_items[~next_items.get('is_separator', True)]
            if not non_empty.empty:
                first_item = non_empty.iloc[0]['البند']
                if 'بوبينه' in str(first_item):
                    category_name = "البوبينات"
                elif 'حساس' in str(first_item):
                    category_name = "الحساسات"
                elif 'شريط' in str(first_item):
                    category_name = "شرائط الإيرباج"
                else:
                    category_name = "منتجات أخرى"
        else:
            # Add non-separator rows to current category
            if not (pd.isna(row['البند']) or row['البند'] == ''):
                current_category.append(row)
    
    # Add the last category if it has items
    if current_category:
        categories.append({
            'name': category_name,
            'items': current_category
        })
    
    return categories

def filter_categories(categories, search_term):
    """Filter categories based on search term"""
    if not search_term:
        return categories
    
    search_term = search_term.lower()
    filtered_categories = []
    
    for category in categories:
        filtered_items = []
        for item in category['items']:
            if (search_term in str(item['البند']).lower() or 
                search_term in str(item['المنشأ']).lower()):
                filtered_items.append(item)
        
        if filtered_items:
            filtered_categories.append({
                'name': category['name'],
                'items': filtered_items
            })
    
    return filtered_categories

def paginate_categories(categories, page, items_per_page):
    """Paginate categories and items"""
    all_items = []
    for category in categories:
        all_items.extend([(category['name'], item) for item in category['items']])
    
    total_items = len(all_items)
    total_pages = math.ceil(total_items / items_per_page) if total_items > 0 else 1
    
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    page_items = all_items[start_idx:end_idx]
    
    # Group items back by category
    paginated_categories = {}
    for category_name, item in page_items:
        if category_name not in paginated_categories:
            paginated_categories[category_name] = []
        paginated_categories[category_name].append(item)
    
    return paginated_categories, total_pages, total_items

def update_quantity(product_name: str, change: int):
    """Update quantity for a product"""
    if product_name not in st.session_state.quantities:
        st.session_state.quantities[product_name] = 0
    
    new_quantity = st.session_state.quantities[product_name] + change
    st.session_state.quantities[product_name] = max(0, new_quantity)

def get_selected_items():
    """Get items with quantities > 0"""
    selected = {}
    for product, qty in st.session_state.quantities.items():
        if qty > 0:
            selected[product] = qty
    return selected

def calculate_total_from_categories(selected_items: Dict[str, int], categories: List) -> tuple:
    """Calculate total items and cost from categories"""
    total_items = sum(selected_items.values())
    total_cost = 0
    
    # Create a lookup dictionary for prices
    price_lookup = {}
    for category in categories:
        for item in category['items']:
            price_lookup[item['البند']] = item['السعر']
    
    for product, qty in selected_items.items():
        if product in price_lookup:
            price = price_lookup[product]
            total_cost += price * qty
    
    return total_items, total_cost

def generate_whatsapp_message_from_categories(selected_items: Dict[str, int], categories: List) -> str:
    """Generate WhatsApp message from categories"""
    message_lines = ["شركة المهندس لقطع غيار السيارات", "🧾 طلب جديد:", ""]
    
    # Create price lookup
    price_lookup = {}
    for category in categories:
        for item in category['items']:
            price_lookup[item['البند']] = item['السعر']
    
    total_cost = 0
    for product, qty in selected_items.items():
        if product in price_lookup:
            price = price_lookup[product]
            subtotal = price * qty
            total_cost += subtotal
            message_lines.append(f"- {product}: {qty} × {price} = {subtotal}")
    
    total_items = sum(selected_items.values())
    message_lines.extend([
        "",
        f"📦 عدد الأصناف: {total_items}",
        f"✅ الإجمالي: {total_cost} جنيه"
    ])
    
    message = "\n".join(message_lines)
    encoded_message = urllib.parse.quote(message)
    return f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded_message}"

def render_product_card(item, category_name):
    """Render a single product card with embedded controls"""
    product_name = item['البند']
    origin = item['المنشأ']
    price = item['السعر']
    
    current_qty = st.session_state.quantities.get(product_name, 0)
    subtotal = price * current_qty
    
    # Create unique keys for buttons
    minus_key = f"minus_{hash(product_name)}_{hash(category_name)}"
    plus_key = f"plus_{hash(product_name)}_{hash(category_name)}"
    
    # Product card HTML structure
    card_html = f'''
    <div class="product-card">
        <div class="product-header">
            <div class="product-info">
                <div class="product-name">{product_name}</div>
                <div class="product-origin">
                    <span>🏭</span>
                    <span>المنشأ: {origin}</span>
                </div>
                <div class="product-price">💰 {price} جنيه</div>
            </div>
            <div class="quantity-controls">
    '''
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Quantity controls in embedded columns
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("−", key=minus_key, disabled=current_qty <= 0, help="تقليل الكمية"):
            update_quantity(product_name, -1)
            st.rerun()
    
    with col2:
        st.markdown(f'<div class="qty-display">{current_qty}</div>', unsafe_allow_html=True)
    
    with col3:
        if st.button("+", key=plus_key, help="زيادة الكمية"):
            update_quantity(product_name, 1)
            st.rerun()
    
    # Close quantity controls and add footer if item is selected
    footer_html = '''
            </div>
        </div>
    '''
    
    if current_qty > 0:
        footer_html += f'''
        <div class="product-footer">
            <div class="subtotal">المجموع: {subtotal} جنيه</div>
            <div style="font-size: 12px; color: #666;">الكمية: {current_qty}</div>
        </div>
        '''
    
    footer_html += '</div>'
    st.markdown(footer_html, unsafe_allow_html=True)

# Main app
def main():
    # Title
    st.markdown('<h1 class="main-title">شركة المهندس لقطع غيار السيارات</h1>', unsafe_allow_html=True)
    
    # Load data
    if st.session_state.products_data is None:
        with st.spinner('جاري تحميل البيانات...'):
            st.session_state.products_data = load_google_sheet_data_real()
    
    df = st.session_state.products_data
    
    if df.empty:
        st.error("لا توجد بيانات متاحة")
        return
    
    # Process data into categories
    categories = process_data_with_categories(df)
    
    # New Order Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("طلبية جديدة", key="new_order_btn"):
            st.session_state.show_products = True
            st.session_state.show_review = False
            st.session_state.current_page = 0
            st.rerun()
    
    # Show products table
    if st.session_state.show_products:
        st.markdown("---")
        
        # Search box and items per page selector
        search_col1, search_col2 = st.columns([3, 1])
        with search_col1:
            search_term = st.text_input(
                "البحث في المنتجات",
                value=st.session_state.search_term,
                placeholder="ابحث عن قطعة غيار...",
                key="search_input"
            )
            if search_term != st.session_state.search_term:
                st.session_state.search_term = search_term
                st.session_state.current_page = 0  # Reset to first page
                st.rerun()
        
        with search_col2:
            items_per_page = st.selectbox(
                "عدد العناصر",
                options=[5, 10, 15, 20],
                index=[5, 10, 15, 20].index(st.session_state.items_per_page),
                key="items_per_page_select"
            )
            if items_per_page != st.session_state.items_per_page:
                st.session_state.items_per_page = items_per_page
                st.session_state.current_page = 0  # Reset to first page
                st.rerun()
        
        # Filter categories
        filtered_categories = filter_categories(categories, st.session_state.search_term)
        
        if not filtered_categories:
            st.markdown('<div class="empty-state">لا توجد منتجات تطابق البحث 🔍</div>', unsafe_allow_html=True)
            return
        
        # Paginate results
        paginated_categories, total_pages, total_items = paginate_categories(
            filtered_categories, 
            st.session_state.current_page, 
            st.session_state.items_per_page
        )
        
        # Display paginated categories and products
        if paginated_categories:
            current_category = None
            
            for category_name, items in paginated_categories.items():
                # Only show category header if it's different from previous
                if category_name != current_category:
                    st.markdown(f'<div class="category-header">{category_name}</div>', unsafe_allow_html=True)
                    current_category = category_name
                
                # Display products in this category
                for item in items:
                    render_product_card(item, category_name)
        
        # Pagination controls
        if total_pages > 1:
            st.markdown('<div class="pagination-container">', unsafe_allow_html=True)
            
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
            
            with col1:
                if st.button("◀◀", disabled=st.session_state.current_page <= 0, help="الصفحة الأولى"):
                    st.session_state.current_page = 0
                    st.rerun()
            
            with col2:
                if st.button("◀", disabled=st.session_state.current_page <= 0, help="الصفحة السابقة"):
                    st.session_state.current_page -= 1
                    st.rerun()
            
            with col3:
                st.markdown(f'<div class="pagination-info">صفحة {st.session_state.current_page + 1} من {total_pages} ({total_items} عنصر)</div>', unsafe_allow_html=True)
            
            with col4:
                if st.button("▶", disabled=st.session_state.current_page >= total_pages - 1, help="الصفحة التالية"):
                    st.session_state.current_page += 1
                    st.rerun()
            
            with col5:
                if st.button("▶▶", disabled=st.session_state.current_page >= total_pages - 1, help="الصفحة الأخيرة"):
                    st.session_state.current_page = total_pages - 1
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Floating summary for selected items
        selected_items = get_selected_items()
        if selected_items:
            total_items, total_cost = calculate_total_from_categories(selected_items, categories)
            
            st.markdown(f'''
            <div class="floating-summary">
                📦 {len(selected_items)} أصناف مختارة | 
                🔢 {total_items} قطعة | 
                💰 {total_cost} جنيه
            </div>
            ''', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("مراجعة الطلبية 📋", key="review_order_btn"):
                    st.session_state.show_review = True
                    st.rerun()
    
    # Review popup
    if st.session_state.show_review:
        selected_items = get_selected_items()
        if selected_items:
            total_items, total_cost = calculate_total_from_categories(selected_items, categories)
            
            st.markdown("---")
            st.markdown("## 📋 مراجعة الطلبية")
            
            # Selected items details
            st.markdown("### تفاصيل الطلبية:")
            
            # Create price lookup
            price_lookup = {}
            for category in categories:
                for item in category['items']:
                    price_lookup[item['البند']] = item['السعر']
            
            for product, qty in selected_items.items():
                if product in price_lookup:
                    price = price_lookup[product]
                    subtotal = price * qty
                    st.write(f"• **{product}**: {qty} × {price} = {subtotal} جنيه")
            
            # Summary cards
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="summary-card">
                    <h3>📦 عدد الأصناف</h3>
                    <h2>{total_items}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="summary-card">
                    <h3>💰 الإجمالي</h3>
                    <h2>{total_cost} جنيه</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Action buttons
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.button("العودة للتعديل", key="back_to_edit"):
                    st.session_state.show_review = False
                    st.rerun()
            
            with col2:
                whatsapp_url = generate_whatsapp_message_from_categories(selected_items, categories)
                st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; font-size: 16px; width: 100%;">إرسال عبر واتساب 📱</button></a>', unsafe_allow_html=True)
            
            with col3:
                if st.button("طلبية جديدة", key="new_order_from_review"):
                    st.session_state.quantities = {}
                    st.session_state.show_review = False
                    st.session_state.search_term = ""
                    st.session_state.current_page = 0
                    st.rerun()

if __name__ == "__main__":
    main()
