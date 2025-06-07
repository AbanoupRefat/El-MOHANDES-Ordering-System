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
    
    .product-table {
        direction: rtl;
    }
    
    .summary-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        text-align: center;
        direction: rtl;
    }
    
    .quantity-controls {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        direction: ltr;
    }
    
    .quantity-btn {
        background-color: #0066cc;
        color: white;
        border: none;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        font-size: 16px;
        cursor: pointer;
    }
    
    .quantity-display {
        min-width: 40px;
        text-align: center;
        font-weight: bold;
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
SHEET_URL = st.secrets["google"]["sheet_url"] # Replace with your actual sheet URL
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
        sheet = gc.open_by_url(SHEET_URL).sheet1
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
            'قلب طلمبه سيات ايبيزا', 'قلب طلمبه ليون', 'قلب طلمبه الفا روميو جولييتا'
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

def paginate_dataframe(df: pd.DataFrame, page: int, items_per_page: int = 10):
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
    """Generate WhatsApp message"""
    if products_df.empty:
        return ""
    
    message_lines = ["شركة المهندس لقطع غيار السيارات", "🧾 طلب جديد:", ""]
    
    total_cost = 0
    for product, qty in selected_items.items():
        product_row = products_df[products_df['البند'] == product]
        if not product_row.empty:
            price = product_row.iloc[0]['السعر']
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
    
    # Show products table
    if st.session_state.show_products:
        st.markdown("---")
        
        # Search box
        search_col1, search_col2 = st.columns([2, 1])
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
        items_per_page = 10
        total_pages = math.ceil(len(filtered_df) / items_per_page)
        
        # Page navigation
        if total_pages > 1:
            nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
            with nav_col2:
                page_col1, page_col2, page_col3 = st.columns([1, 1, 1])
                
                with page_col1:
                    if st.button("السابق", disabled=st.session_state.current_page == 0):
                        st.session_state.current_page -= 1
                        st.rerun()
                
                with page_col2:
                    st.write(f"صفحة {st.session_state.current_page + 1} من {total_pages}")
                
                with page_col3:
                    if st.button("التالي", disabled=st.session_state.current_page >= total_pages - 1):
                        st.session_state.current_page += 1
                        st.rerun()
        
        # Get current page data
        current_page_df = paginate_dataframe(filtered_df, st.session_state.current_page, items_per_page)
        
        # Products table
        st.markdown("### المنتجات المتاحة")
        
        for idx, row in current_page_df.iterrows():
            product_name = row['البند']
            origin = row['المنشأ']
            price = row['السعر']
            
            current_qty = st.session_state.quantities.get(product_name, 0)
            subtotal = price * current_qty
            
            # Product row
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 2, 1])
                
                with col1:
                    st.write(f"**{product_name}**")
                    st.write(f"المنشأ: {origin}")
                
                with col2:
                    st.write(f"**{price}** جنيه")
                
                with col3:
                    # Quantity controls
                    minus_key = f"minus_{product_name}_{idx}"
                    plus_key = f"plus_{product_name}_{idx}"
                    
                    if st.button("-", key=minus_key, disabled=current_qty <= 0):
                        update_quantity(product_name, -1)
                        st.rerun()
                
                with col4:
                    st.write(f"الكمية: **{current_qty}**")
                    if st.button("+", key=plus_key):
                        update_quantity(product_name, 1)
                        st.rerun()
                
                with col5:
                    if current_qty > 0:
                        st.write(f"**{subtotal}** جنيه")
                    else:
                        st.write("0 جنيه")
                
                st.markdown("---")
        
        # Review Order Button
        selected_items = get_selected_items()
        if selected_items:
            st.markdown("### ملخص الطلبية")
            total_items, total_cost = calculate_total(selected_items, products_df)
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"📦 عدد الأصناف المختارة: **{total_items}**")
            with col2:
                st.info(f"💰 الإجمالي: **{total_cost}** جنيه")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("مراجعة الطلبية", key="review_order_btn"):
                    st.session_state.show_review = True
                    st.rerun()
    
    # Review popup
    if st.session_state.show_review:
        selected_items = get_selected_items()
        if selected_items:
            total_items, total_cost = calculate_total(selected_items, products_df)
            
            st.markdown("---")
            st.markdown("## مراجعة الطلبية")
            
            # Selected items details
            st.markdown("### تفاصيل الطلبية:")
            for product, qty in selected_items.items():
                product_row = products_df[products_df['البند'] == product]
                if not product_row.empty:
                    price = product_row.iloc[0]['السعر']
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
                whatsapp_url = generate_whatsapp_message(selected_items, products_df)
                st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; font-size: 16px; width: 100%;">إرسال عبر واتساب</button></a>', unsafe_allow_html=True)
            
            with col3:
                if st.button("طلبية جديدة", key="new_order_from_review"):
                    st.session_state.quantities = {}
                    st.session_state.show_review = False
                    st.session_state.current_page = 0
                    st.session_state.search_term = ""
                    st.rerun()

if __name__ == "__main__":
    main()