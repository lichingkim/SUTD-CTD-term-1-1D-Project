import streamlit as st
import mylibrary

# Initialize cart
if "cart" not in st.session_state:
    st.session_state.cart = {}

# Page Display
st.set_page_config(page_title="Yan Yan.co")
st.title("Yan Yan.co")
st.text("Hand made with love by Elicia")
st.markdown("---")
st.header("Our products")

# Load all products display in tabs
mylibrary.display_all_products_in_tabs()

# Sidebar
with st.sidebar:
    st.title("My Cart")
    if len(st.session_state.cart) == 0:
        st.write("Your shopping cart is empty.")
    else:
        for product_key, quantity in st.session_state.cart.items():
            product_info = st.session_state.get(f"product_{product_key}")
            col1, col2 = st.columns([1,1])
            with col1: 
                st.write("x {}".format(quantity))
            with col2:
                st.write("{} - ${:.2f}".format(product_info["name"], product_info["price"]))
            
        st.markdown("---")
        
        # Updated checkout button with navigation
        if st.button("Check out", key="Checkout"):
            st.switch_page("pages/checkout.py")