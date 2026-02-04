import streamlit as st
import mylibrary

st.set_page_config(page_title="Checkout - Yan Yan Crochet", page_icon="🛒")
st.title("🛒 Checkout")
st.markdown("*Complete your amigurumi order* 🧶")

# Initialize session in case never buy item
if 'cart' not in st.session_state:
    st.session_state.cart = {}

# For empty carts
if not st.session_state.cart:
    st.warning("Your cart is empty!")
    if st.button("← Back to Shop"):
        st.switch_page("app.py")
    st.stop()

#Layout
main_col1, main_col2 = st.columns([1.8, 1.2])

#Main Cart Column
with main_col1:
    
    #Display cart items
    mylibrary.display_cart(st.session_state.cart)
    
    st.divider()
    col1, col2 = st.columns([1, 1])
    
    #Edit Button
    with col1:
        #Becomes "Done" when in edit mode
        if st.button("Edit" if not st.session_state.edit_mode else "Done", key="edit_toggle"):
            st.session_state.edit_mode = not st.session_state.edit_mode
            st.rerun()

    #Display Subtotal
    with col2:
        order_summary = mylibrary.calculate_order_total(st.session_state.cart)
        
        if order_summary['bundle_savings'] > 0:
            st.write(f"**Base Total:** ${order_summary['base_subtotal']:.2f}")
            for discount in order_summary['discount_details']:
                st.write(f"🎁 {discount}")
            st.write(f"**Final Subtotal:** ${order_summary['subtotal']:.2f}")
        else:
            st.write(f"**Subtotal:** ${order_summary['subtotal']:.2f}")

    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← Continue Shopping"):
            st.switch_page("app.py")

    with col2:
        if st.button("Proceed to Payment", type="primary"):
            st.switch_page("pages/payment.py")

# AI Recommendations
with main_col2:
    st.header("💡 Yan Yan AI Recommendation")

    #Loading Text
    with st.spinner("🤖 Finding perfect additions..."):
        # Prompt and call OpenAI API
        analysis = mylibrary.get_complete_ai_analysis(st.session_state.cart)
    
    recommendations = analysis.get("recommendations", [])
    
    # Display recommendations
    for recommendation_index in range(len(recommendations)):
        recommendation = recommendations[recommendation_index]
        col1, col2 = st.columns([3.5, 1])
        
        #Recommendation details
        with col1:
            st.write(f"**{recommendation.get('product_name', '')}**")
            st.caption(recommendation.get('reason', 'Great addition!'))
        
        # Add to cart    
        with col2:
            product_name = recommendation.get('product_name', '')
            if st.button("➕ Add", key=f"rec_{recommendation_index}"):
                
                #Format Product Key
                product_key = product_name.lower().replace(" ", "_").replace(".", "")
                if product_key in st.session_state.cart:
                    st.session_state.cart[product_key] += 1
                else:
                    st.session_state.cart[product_key] = 1
                st.toast(f"✅ Added {product_name} to cart!", icon="🛒")
                st.rerun()
    