import streamlit as st
import mylibrary

# Set page config
st.set_page_config(page_title="Payment - Yan Yan Crochet", page_icon="💳")

# Initialize order completion state
if 'order_completed' not in st.session_state:
    st.session_state.order_completed = False

# Get cart from previous page
cart = st.session_state.get('cart', {})

# Reset order completion only when user actually has items to order
# This prevents reset immediately after placing order (when cart is intentionally empty)
if cart and st.session_state.order_completed:
    st.session_state.order_completed = False

st.title("💳 Payment")
st.markdown("*Complete your Yan Yan Crochet order* 🧶")

# Add back to checkout button (only if order not completed)
if not st.session_state.order_completed:
    col_back, col_space = st.columns([1, 4])
    with col_back:
        if st.button("← Back to Checkout"):
            st.switch_page("pages/checkout.py")

st.markdown("---")

# Check if order was completed
if st.session_state.order_completed:
    # ORDER CONFIRMATION PAGE
    st.success("✅ Your order has been placed successfully!")
    st.balloons()
    st.info("🎉 Thank you for your order! You will receive a confirmation email shortly.")
        
    # Continue shopping button
    if st.button("🛍️ Continue Shopping", type="primary", use_container_width=True):
        # Reset order state and clear cart completely
        st.session_state.order_completed = False
        st.switch_page("app.py")
    
    st.stop()  # Don't show the rest of the payment form

# NORMAL PAYMENT PAGE (if order not completed)
# Layout: Left = Contact, delivery & payment options, Right = Order Summary
col1, col2 = st.columns([2, 1])

# Right Col: Order Summary (preserving teammate's logic)
with col2:
    st.subheader("🛒 Order Summary")
    subtotal = mylibrary.render_cart(cart)

    # Discount state tracking
    st.session_state.setdefault("applied_discount_code", "")
    st.session_state.setdefault("discount_value", 0)
    
    # Valid discount codes
    valid_codes = {"FRIEND10": 0.10, "FAMILY20": 0.20}
    
    # Discount code input
    code = st.text_input("Discount code or gift card")
    previously_applied = st.session_state.applied_discount_code
    
    # Always define discount before using it
    discount = st.session_state.discount_value
    
    # Discount logic
    if code in valid_codes:
        if previously_applied:
            st.warning("Only one discount code can be applied. Your discount has been updated to the current code.")
        discount, msg = mylibrary.apply_discount(code, subtotal, valid_codes)
        st.session_state.discount_value = discount
        st.session_state.applied_discount_code = code
        st.success(msg)
    elif code:
        st.error("Invalid discount code")

    # Free shipping logic
    shipping_cost, shipping_msg, progress = mylibrary.check_free_shipping(subtotal + discount)
    st.write(shipping_msg)
    if shipping_cost == 0:
        st.success("🎉 You've unlocked free shipping!")
    else:
        st.progress(progress)

    # GST and total
    gst = (subtotal + discount)*0.08
    total = subtotal + gst + shipping_cost # Adjust subtotal to reflect discount applied
    # Final summary
    st.write(f"Subtotal: ${subtotal:.2f}")
    st.write(f"Discount: ${discount:.2f}")
    st.write(f"GST (8%): ${gst:.2f}")
    st.write(f"Shipping: ${shipping_cost:.2f}")
    st.subheader(f"Total: ${total:.2f}")

# Left Col: Contact & Payment (preserving teammate's logic)
with col1:
    # Contact Information
    st.subheader("📧 Contact Information")
    email = st.text_input("Email address")
    subscribe = st.checkbox("Subscribe to news and offers")
    
    # 🚚 Delivery Details
    st.subheader("🚚 Delivery Details")
    country = st.selectbox("Country/Region", ["Singapore", "Malaysia", "Indonesia"])
    name = st.text_input("Recipient Name")
    address = st.text_area("Address")
    postal = st.text_input("Postal Code")
    phone = st.text_input("Phone Number")
    save_info = st.checkbox("Save this information for future use")
    
    st.caption("Enter your shipping address to view available shipping methods.")
    
    # 💳 Payment Method
    st.subheader("💳 Payment Method")
    payment_method = st.radio(
        "Choose your payment option:",
        ["Credit/Debit Card", "PayNow (QR)", "Cash on Delivery"]
    )
    
    if payment_method == "Credit/Debit Card":
        saved_card = mylibrary.load_saved_card()
        card = mylibrary.render_card_payment(saved_card)

    elif payment_method == "PayNow (QR)":
        st.info("Scan the QR code below to pay via PayNow")
        # Use the new PayNow QR code
        try:
            st.image("images/paynowQR.jpg", caption="Scan to pay via PayNow", width=200)
        except:
            st.write("📱 QR Code for PayNow payment")
        st.write(f"Amount to pay: ${total:.2f}")
    
    elif payment_method == "Cash on Delivery":
        st.info("Please prepare exact change. Delivery personnel will collect payment.")
    
    # 🛍️ Place Order Button
    st.markdown("---")
    if st.button("🛍️ Place Order", type="primary", use_container_width=True):
        
        # Set order completion state
        st.session_state.order_completed = True
        
        # Clear cart data
        if 'cart' in st.session_state:
            st.session_state.cart = {}
        # Reset discount state
        if 'applied_discount_code' in st.session_state:
            st.session_state.applied_discount_code = ""
        if 'discount_value' in st.session_state:
            st.session_state.discount_value = 0    
        # Rerun to show confirmation page
        st.rerun()
