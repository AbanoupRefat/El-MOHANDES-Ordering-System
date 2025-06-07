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

# Enhanced CSS for better UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif;
    }
    
    .main > div {
        direction: rtl;
        text-align: right;
        padding: 0 2rem;
    }
    
    /* Header Styling */
    .main-title {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 2rem;
        direction: rtl;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Button Styling */
    .stButton > button {
        direction: rtl;
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        font-size: 16px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
    }
    
    /* Product Card Styling */
    .product-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
        direction: rtl;
    }
    
    .product-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
        border-color: #667eea;
    }
    
    .product-name {
        font-size: 1.2rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 0.5rem;
    }
    
    .product-origin {
        color: #718096;
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
    }
    
    .product-price {
        font-size: 1.1rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 1rem;
    }
    
    /* Quantity Controls */
    .quantity-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        direction: ltr;
        background: #f7fafc;
        padding: 0.75rem;
        border-radius: 12px;
        margin: 0.5rem 0;
    }
    
    .quantity-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        width: 40px;
        height: 40px;
        font-size: 18px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .quantity-btn:hover {
        transform: scale(1.1);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    .quantity-btn:disabled {
        background: #cbd5e0;
        cursor: not-allowed;
        transform: none;
        box-shadow: none;
    }
    
    .quantity-display {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        min-width: 60px;
        text-align: center;
        font-weight: 600;
        font-size: 1.1rem;
        color: #2d3748;
    }
    
    .quantity-label {
        color: #4a5568;
        font-weight: 500;
        margin-left: 10px;
    }
    
    /* Subtotal Display */
    .subtotal {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        text-align: center;
        margin-top: 0.5rem;
    }
    
    /* Search Box */
    .stTextInput > div > div > input {
        direction: rtl;
        text-align: right;
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Summary Cards */
    .summary-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        margin: 1rem 0;
        text-align: center;
        direction: rtl;
        box-shadow: 0 8px 25px rgba(240, 147, 251, 0.4);
    }
    
    .summary-card h3 {
        margin: 0 0 0.5rem 0;
        font-weight: 400;
        opacity: 0.9;
    }
    
    .summary-card h2 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    /* Navigation */
    .nav-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 1rem;
        margin: 2rem 0;
        direction: ltr;
    }
    
    .page-info {
        background: #f7fafc;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 500;
        color: #4a5568;
    }
    
    /* Review Section */
    .review-section {
    background: #f8f9fa;
    border-radius: 16px;
    padding: 2rem;
    margin: 2rem 0;
    border: 1px solid #e9ecef;
}
.review-item strong {
    color: #1a202c; /* Darker color for strong elements */
}

.review-item small {
    color: #718096; /* Gray color for origin text */
}

/* Make sure review section headers are visible */
.review-section h3 {
    color: #2d3748;
    margin-bottom: 1rem;
}

/* Ensure price information is clearly visible */
.review-item div:last-child {
    color: #2d3748;
    font-weight: 500;
}    
    .review-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    background: white;
    border-radius: 8px;
    margin: 0.5rem 0;
    border-left: 4px solid #667eea;
    color: #2d3748; /* Add explicit text color */
}
    
    /* WhatsApp Button */
    .whatsapp-btn {
        background: #25D366 !important;
        color: white !important;
        text-decoration: none;
        display: inline-block;
        padding: 1rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(37, 211, 102, 0.4);
    }
    
    .whatsapp-btn:hover {
        background: #22c55e !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(37, 211, 102, 0.6);
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main > div {
            padding: 0 1rem;
        }
        
        .main-title {
            font-size: 2rem;
        }
        
        .product-card {
            padding: 1rem;
        }
        
        .quantity-container {
            flex-direction: column;
            gap: 10px;
        }
    }
    
    /* Alert Styling */
    .stAlert {
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
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

# Google Sheets configuration
SHEET_URL = st.secrets["google"]["sheet_id"] # Replace with your actual sheet ID
WHATSAPP_NUMBER = st.secrets["whatsapp"]["number"] # Replace with actual WhatsApp number

def load_google_sheet_data_real():
    """Load data from real Google Sheets - Use this when API is set up"""
    try:
        # Uncomment and configure when ready to use real Google Sheets
        
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

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_google_sheet_data():
    """Load data from Google Sheets"""
    try:
        # Real data based on your sheet structure
        # Replace this with actual Google Sheets API call when ready
        sample_data = {
            'البند': [
                'قلب طلمبه بونقرمال (سن ناعم)',
                'قلب طلمبه بونقرمال (سن مشرشر)',
                '(القصير) RB قلبطلمبه بنزين',
                'قلب طلمبه بنزين MD (الطويل)',
                'قلب طلمبه تيوسان (2 مخرج القصير)',
                'قلب طلمبه سبورتاج (2 مخرج الطويل)',
                'قلب طلمبه نيسان N17',
                'قلب طلمبه باريس 1 كرولا 2008 1 فيجو',
                'قلب باريس و كرولا 2014',
                'قلب طلمبه كرولا 2001 (قيشه رفيعه)',
                'قلب طلمبه شيفرولية كروز 1 اوبل استرا',
                'قلب طلمبه مازدا 3',
                'قلب طلمبه سوزوكي سويفت',
                'قلب طلمبه ميتسوبيشي اتراج',
                'قلب طلمبه رينو كليو',
                'قلب طلمبه لانسر',
                'قلب طلمبه هيونداي اكسنت',
                'قلب طلمبه فولكس فاجن جيتا',
                'قلب طلمبه نيسان تيدا',
                'قلب طلمبه بيجو 301',
                'قلب طلمبه دايو نوبيرا',
                'قلب طلمبه مازدا 6',
                'قلب طلمبه كيا سيراتو',
                'قلب طلمبه هيونداي النترا',
                'قلب طلمبه تويوتا كامري'
            ],
            'المنشأ': [
                'كوريا', 'كوريا', 'كوريا', 'كوريا', 'كوريا',
                'كوريا', 'كوريا', 'كوريا', 'كوريا', 'كوريا',
                'كوريا', 'كوريا', 'كوريا', 'كوريا', 'كوريا',
                'كوريا', 'كوريا', 'كوريا', 'كوريا', 'كوريا',
                'كوريا', 'كوريا', 'كوريا', 'كوريا', 'كوريا'
            ],
            'السعر': [
                415, 425, 573, 585, 762,
                774, 567, 567, 691, 561,
                756, 800, 589, 817, 650,
                720, 580, 690, 620, 710,
                590, 780, 640, 670, 750
            ]
        }
        
        # Add more pump parts to simulate your full inventory
        additional_pumps = [
            'قلب طلمبه فورد فيستا', 'قلب طلمبه شيفرولية افيو', 'قلب طلمبه نيسان صني',
            'قلب طلمبه هيونداي فيرنا', 'قلب طلمبه كيا ريو', 'قلب طلمبه مازدا 2',
            'قلب طلمبه ميتسوبيشي كولت', 'قلب طلمبه سوزوكي التو', 'قلب طلمبه دايهاتسو تيريوس',
            'قلب طلمبه هوندا سيفيك', 'قلب طلمبه اكورد', 'قلب طلمبه نيسان قشقاي',
            'قلب طلمبه جيلي امجراند', 'قلب طلمبه بي واي دي F3', 'قلب طلمبه شيري تيجو',
            'قلب طلمبه فولكس جولف', 'قلب طلمبه بولو', 'قلب طلمبه اوبل كورسا',
            'قلب طلمبه فيات سيينا', 'قلب طلمبه رينو لوجان', 'قلب طلمبه سيمبول',
            'قلب طلمبه بيجو 206', 'قلب طلمبه 308', 'قلب طلمبه سيتروين C4',
            'قلب طلمبه C3', 'قلب طلمبه لادا جرانتا', 'قلب طلمبه فيستا',
            'قلب طلمبه كالينا', 'قلب طلمبه سكودا اوكتافيا', 'قلب طلمبه فابيا',
            'قلb طلمبه سيات ايبيزا', 'قلب طلمبه ليون', 'قلب طلمبه الفا روميو جولييتا'
        ]
        
        # Add more items to reach 100+
        for i, pump in enumerate(additional_pumps):
            sample_data['البند'].append(pump)
            sample_data['المنشأ'].append('كوريا')
            sample_data['السعر'].append(500 + (i * 25))  # Varying prices
            
        # Add some other car parts categories
        other_parts = [
            'فلتر زيت محرك', 'فلتر هواء', 'فلتر وقود', 'فلتر مكيف',
            'شمعات اشعال', 'كويل اشعال', 'حساس اكسجين', 'حساس كرنك',
            'سير مولد', 'سير مكيف', 'مضخة مياه', 'ترموستات',
            'فرامل امامية', 'فرامل خلفية', 'ديسك فرامل', 'طقم كلتش',
            'بطارية سيارة', 'كوتش امامي', 'كوتش خلفي', 'بلف صبابات'
        ]
        
        origins = ['كوريا', 'اليابان', 'ألمانيا', 'تركيا', 'الصين']
        
        for i, part in enumerate(other_parts):
            sample_data['البند'].append(part)
            sample_data['المنشأ'].append(origins[i % len(origins)])
            sample_data['السعر'].append(200 + (i * 30))
        
        return pd.DataFrame(sample_data)
    
    except Exception as e:
        st.error(f"خطأ في تحميل البيانات: {str(e)}")
        return pd.DataFrame()

def filter_products(df: pd.DataFrame, search_term: str) -> pd.DataFrame:
    """Filter products based on search term"""
    if not search_term:
        return df
    
    search_term = search_term.lower()
    mask = (
        df['البند'].str.lower().str.contains(search_term, na=False) |
        df['المنشأ'].str.lower().str.contains(search_term, na=False)
    )
    return df[mask]

def paginate_dataframe(df: pd.DataFrame, page: int, items_per_page: int = 8):
    """Paginate dataframe"""
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    return df.iloc[start_idx:end_idx]

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

def calculate_total(selected_items: Dict[str, int], products_df: pd.DataFrame) -> tuple:
    """Calculate total items and cost"""
    if products_df.empty:
        return 0, 0
    
    total_items = sum(selected_items.values())
    total_cost = 0
    
    for product, qty in selected_items.items():
        product_row = products_df[products_df['البند'] == product]
        if not product_row.empty:
            price = product_row.iloc[0]['السعر']
            total_cost += price * qty
    
    return total_items, total_cost

def generate_whatsapp_message(selected_items: Dict[str, int], products_df: pd.DataFrame) -> str:
    """Generate clean WhatsApp message without emojis"""
    if products_df.empty:
        return ""
    
    message_lines = [
        "*شركة المهندس لقطع غيار السيارات*",
        "",
        "*طلب جديد:*",
        "=" * 30,
        ""
    ]
    
    total_cost = 0
    item_number = 1
    
    for product, qty in selected_items.items():
        product_row = products_df[products_df['البند'] == product]
        if not product_row.empty:
            price = product_row.iloc[0]['السعر']
            origin = product_row.iloc[0]['المنشأ']
            subtotal = price * qty
            total_cost += subtotal
            
            message_lines.append(f"*{item_number}.* {product}")
            message_lines.append(f"   المنشأ: {origin}")
            message_lines.append(f"   الكمية: {qty}")
            message_lines.append(f"   السعر: {price} جنيه")
            message_lines.append(f"   المجموع: *{subtotal} جنيه*")
            message_lines.append("")
            item_number += 1
    
    total_items = sum(selected_items.values())
    message_lines.extend([
        "=" * 30,
        f"*عدد الأصناف:* {total_items}",
        f"*إجمالي المبلغ:* {total_cost} جنيه",
        "",
        "شكرا لاختيارك شركة المهندس",
        "للتواصل والاستفسار: نفس هذا الرقم"
    ])
    
    message = "\n".join(message_lines)
    encoded_message = urllib.parse.quote(message)
    return f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded_message}"

def render_product_card(row, idx):
    """Render a single product card"""
    product_name = row['البند']
    origin = row['المنشأ']
    price = row['السعر']
    current_qty = st.session_state.quantities.get(product_name, 0)
    subtotal = price * current_qty
    
    card_html = f"""
    <div class="product-card">
        <div class="product-name">{product_name}</div>
        <div class="product-origin">المنشأ: {origin}</div>
        <div class="product-price">{price} جنيه</div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Quantity controls in a container
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            minus_key = f"minus_{product_name}_{idx}"
            if st.button("−", key=minus_key, disabled=current_qty <= 0):
                update_quantity(product_name, -1)
                st.rerun()
        
        with col2:
            quantity_html = f"""
            <div class="quantity-container">
                <span class="quantity-label">الكمية:</span>
                <div class="quantity-display">{current_qty}</div>
            </div>
            """
            st.markdown(quantity_html, unsafe_allow_html=True)
        
        with col3:
            plus_key = f"plus_{product_name}_{idx}"
            if st.button("＋", key=plus_key):
                update_quantity(product_name, 1)
                st.rerun()
    
    # Show subtotal if quantity > 0
    if current_qty > 0:
        subtotal_html = f"""
        <div class="subtotal">
            المجموع: {subtotal} جنيه
        </div>
        """
        st.markdown(subtotal_html, unsafe_allow_html=True)

# Main app
def main():
    # Title
    st.markdown('<h1 class="main-title">شركة المهندس لقطع غيار السيارات</h1>', unsafe_allow_html=True)
    
    # Load data
    if st.session_state.products_data is None:
        with st.spinner('جاري تحميل البيانات...'):
            st.session_state.products_data = load_google_sheet_data_real()
    
    products_df = st.session_state.products_data
    
    if products_df.empty:
        st.error("لا توجد بيانات متاحة")
        return
    
    # New Order Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("طلبية جديدة", key="new_order_btn"):
            st.session_state.show_products = True
            st.session_state.show_review = False
            st.rerun()
    
    # Show products
    if st.session_state.show_products:
        st.markdown("---")
        
        # Search box
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
                st.session_state.current_page = 0
                st.rerun()
        
        # Filter products
        filtered_df = filter_products(products_df, st.session_state.search_term)
        
        if filtered_df.empty:
            st.warning("لا توجد منتجات تطابق البحث")
            return
        
        # Pagination
        items_per_page = 8
        total_pages = math.ceil(len(filtered_df) / items_per_page)
        
        # Page navigation
        if total_pages > 1:
            nav_html = f"""
            <div class="nav-container">
                <div class="page-info">صفحة {st.session_state.current_page + 1} من {total_pages}</div>
            </div>
            """
            st.markdown(nav_html, unsafe_allow_html=True)
            
            nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])
            
            with nav_col1:
                if st.button("◀ السابق", disabled=st.session_state.current_page == 0):
                    st.session_state.current_page -= 1
                    st.rerun()
            
            with nav_col3:
                if st.button("التالي ▶", disabled=st.session_state.current_page >= total_pages - 1):
                    st.session_state.current_page += 1
                    st.rerun()
        
        # Get current page data
        current_page_df = paginate_dataframe(filtered_df, st.session_state.current_page, items_per_page)
        
        # Products grid
        st.markdown("### المنتجات المتاحة")
        
        # Display products in a grid
        for idx, row in current_page_df.iterrows():
            render_product_card(row, idx)
        
        # Order summary
        selected_items = get_selected_items()
        if selected_items:
            st.markdown("---")
            total_items, total_cost = calculate_total(selected_items, products_df)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="summary-card">
                    <h3>عدد الأصناف المختارة</h3>
                    <h2>{total_items}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="summary-card">
                    <h3>الإجمالي</h3>
                    <h2>{total_cost} جنيه</h2>
                </div>
                """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("مراجعة الطلبية", key="review_order_btn"):
                    st.session_state.show_review = True
                    st.rerun()
    
    # Review section
    if st.session_state.show_review:
        selected_items = get_selected_items()
        if selected_items:
            total_items, total_cost = calculate_total(selected_items, products_df)
            
            st.markdown("---")
            st.markdown("## مراجعة الطلبية")
            
            # Review section with styled cards
            st.markdown('<div class="review-section">', unsafe_allow_html=True)
            
            st.markdown("### تفاصيل الطلبية:")
            
            for product, qty in selected_items.items():
                product_row = products_df[products_df['البند'] == product]
                if not product_row.empty:
                    price = product_row.iloc[0]['السعر']
                    origin = product_row.iloc[0]['المنشأ']
                    subtotal = price * qty
                    
                    review_item_html = f"""
                    <div class="review-item">
                        <div>
                            <strong>{product}</strong><br>
                            <small>المنشأ: {origin}</small>
                        </div>
                        <div style="text-align: left;">
                            <div><strong>{qty}</strong> × <strong>{price}</strong> = <strong>{subtotal} جنيه</strong></div>
                        </div>
                    </div>
                    """
                    st.markdown(review_item_html, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Summary cards
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="summary-card">
                    <h3>عدد الأصناف</h3>
                    <h2>{total_items}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="summary-card">
                    <h3>الإجمالي</h3>
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
                whatsapp_url = generate_whatsapp_message(selected_items, products_df)
                st.markdown(f'<a href="{whatsapp_url}" target="_blank" class="whatsapp-btn">إرسال عبر واتساب</a>', unsafe_allow_html=True)
            
            with col3:
                if st.button("طلبية جديدة", key="new_order_from_review"):
                    st.session_state.quantities = {}
                    st.session_state.show_review = False
                    st.session_state.current_page = 0
                    st.session_state.search_term = ""
                    st.rerun()

if __name__ == "__main__":
    main()
