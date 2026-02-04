import streamlit as st
from openai import OpenAI
import json

# Function for display product
def display_product(products, tab_key):
    for row in range(0, len(products), 3):
        cols = st.columns(3)
        for i in range(3):
            if(row + i < len(products)):
                product_final = products[row + i]

                with cols[i]: 
                    st.image(product_final["image"])
                    st.subheader(product_final["name"])
                    st.write(f"${product_final['price']:.2f}")

                    # Create consistent product key for cart
                    product_key = product_final["name"].lower().replace(" ", "_")
                    
                    # Get quantity from cart (dictionary format)
                    quantity = st.session_state.cart.get(product_key, 0)

                    button_col1, button_col2, button_col3 = st.columns(3)
                    
                    with button_col1: # display minus button
                        minus_key = f"{tab_key}_minus_{row}_{i}"
                        if st.button("➖", key=minus_key):
                            if quantity > 1:
                                st.session_state.cart[product_key] = quantity - 1
                            elif quantity == 1:
                                del st.session_state.cart[product_key]
                            st.rerun()

                    with button_col2: # display quantity
                        st.write(f"**{quantity}**")

                    with button_col3: # display + button
                        plus_key = f"{tab_key}_plus_{row}_{i}"
                        if st.button("➕", key=plus_key):
                            st.session_state.cart[product_key] = quantity + 1
                            st.rerun()

def display_all_products_in_tabs():
    all_products = load_products()
    
    # Store all product info in session state once
    for product in all_products:
        product_key = product["name"].lower().replace(" ", "_")
        st.session_state[f"product_{product_key}"] = product

    single_products = []
    couple_products = []
    diykit_products = []
    
    for product in all_products:
        if product['category'] == 'single':
            single_products.append(product)
        elif product['category'] == 'couple':
            couple_products.append(product)
        elif product['category'] == 'diykit':
            diykit_products.append(product)
    
    tab1, tab2, tab3 = st.tabs(["Single", "Couple Set", "DIY Kit"])
    
    with tab1:
        display_product(single_products, "single")
    with tab2: 
        display_product(couple_products, "couple")
    with tab3: 
        display_product(diykit_products, "diykit")
                            

def load_products():
    products = []
    files_to_load = ["single.txt", "couple.txt", "diykit.txt"]
    
    for file in files_to_load:
        with open(f"data/{file}", "r") as txt_file:
            for line in txt_file:
                line = line.strip()
                if "," in line:
                    name, price, image = line.split(",")
                    products.append({
                        "name": name.strip(),
                        "price": round(float(price.strip()), 2), 
                        "image": f"images/{image.strip()}",
                        "category": file.replace(".txt", "")
                    })
    return products
                            
# =======================================
# PAYMENT & CART FUNCTIONS (from notebook)
# =======================================

def render_cart(cart):
    """Render cart items and return subtotal - works with simple cart format"""
    subtotal = 0
    for product_id, qty in cart.items():
        product_info = get_product_info(product_id)
        # Try to display image, but handle missing files gracefully
        st.image(product_info.get("image", ""), width=100)
        st.write(f"{product_info['name']}: {qty} × ${product_info['price']:.2f}")
        subtotal += qty * product_info["price"]
    return subtotal

def apply_discount(code, subtotal, valid_codes):
    """Apply discount code (from payment notebook)"""
    value = valid_codes[code] * subtotal
    return -value, f"Discount applied: -${value:.2f}"

def check_free_shipping(subtotal_after_discount, threshold=100):
    """Check free shipping eligibility (from payment notebook)"""
    if subtotal_after_discount >= threshold:
        return 0, "🎉 You've unlocked free shipping!", 1.0
    else:
        remaining = threshold - subtotal_after_discount
        progress = max(0, min(subtotal_after_discount / threshold, 1.0))
        return 5, f"Spend ${remaining:.2f} more to unlock free shipping", progress

def calculate_gst(amount, rate=0.08):
    """Calculate GST (from payment notebook)"""
    return amount * rate

def calculate_total(subtotal, discount, gst, shipping):
    """Calculate final total (from payment notebook)"""
    return subtotal + discount + gst + shipping

def load_saved_card(filepath="data/card_details.txt"):
    """Load saved card details (from payment notebook)"""
    card = {}
    try:
        with open(filepath, "r") as f:
            for line in f:
                if "|" in line:
                    key, value = line.strip().split("|", 1)
                    card[key] = value
    except FileNotFoundError:
        pass
    return card

def save_card_details(card, filepath="data/card_details.txt"):
    """Save card details (from payment notebook)"""
    with open(filepath, "w") as f:
        for key, value in card.items():
            f.write(f"{key}|{value}\n")

def render_card_payment(saved_card):
    """Render card payment form (from payment notebook)"""
    use_saved = bool(saved_card) and st.checkbox("Use saved card details")

    if use_saved:
        st.markdown("#### 💳 Using saved card:")
        masked = "**** **** **** " + saved_card.get("Card Number", "")[-4:]
        st.write(f"**Card Number:** {masked}")

    card_fields = [
        ("Card Number", "card_number"),
        ("Cardholder Name", "card_name"),
        ("Expiry Date (MM/YY)", "card_expiry"),
        ("CVV", "card_cvv")
    ]

    card = {}
    for field in card_fields:
        label, key = field[0], field[1]
        default = saved_card.get(label, "") if use_saved else ""
        card[key] = st.text_input(label, value=default, key=key)

    if not use_saved and st.checkbox("Save this card for future use"):
        save_card_details({f[0]: card[f[1]] for f in card_fields})

    return card

# =======================================
# CHECKOUT & CART MANAGEMENT FUNCTIONS  
# =======================================

def get_product_info(product_key):
    product_info_key = f"product_{product_key}"
    return st.session_state.get(product_info_key)

def format_cart_summary(cart_items):
    summary = []
    for product_key, quantity in cart_items.items():
        product_info = get_product_info(product_key)
        summary.append(f"{product_info['name']} x{quantity}")
    return summary

def apply_bundle_discounts(cart_items):
    total_savings = 0.0
    discount_details = []
    couple_items = []
    diy_items = []
    
    for product_key, quantity in cart_items.items():
        product_info = get_product_info(product_key)
        product_category = product_info.get('category', '')
        
        if product_category == 'couple':
            couple_items.append({'quantity': quantity, 'info': product_info})
        elif product_category == 'diykit':
            diy_items.append({'quantity': quantity, 'info': product_info})
    
    # Couple Set Discount: 10% off all couple sets
    if len(couple_items) >= 1:
        couple_subtotal = 0
        for i in couple_items:
            couple_subtotal += i['info']['price'] * i['quantity']
        couple_discount = couple_subtotal * 0.10
        total_savings += couple_discount
        discount_details.append(f"Couple Set Bundle (10% off): -${couple_discount:.2f}")
    
    # DIY Kit Discount: Buy 3 accessories, get 1 free (cheapest item)
    total_diy_quantity = sum(i['quantity'] for i in diy_items)
    if total_diy_quantity >= 3:
        cheapest_price = min(item['info']['price'] for item in diy_items)
        free_items = total_diy_quantity // 3
        diy_discount = cheapest_price * free_items
        total_savings += diy_discount
        discount_details.append(f"DIY Kit Bundle ({free_items} free item{'s' if free_items > 1 else ''}): -${diy_discount:.2f}")
    
    return total_savings, discount_details

def calculate_order_total(cart_items):
    base_subtotal = 0
    for product_key, quantity in cart_items.items():
        product_info = get_product_info(product_key)
        base_subtotal += product_info['price'] * quantity
    
    bundle_savings, discount_details = apply_bundle_discounts(cart_items)
    
    final_subtotal = base_subtotal - bundle_savings
    
    return {
        "subtotal": final_subtotal,
        "base_subtotal": base_subtotal,
        "bundle_savings": bundle_savings,
        "discount_details": discount_details
    }

# =======================================
# AI RECOMMENDATION FUNCTIONS
# =======================================

def load_openai_key():
    with open('data/openai_key.txt', 'r') as f:
        api_key = f.read().strip()
        return api_key

def get_complete_ai_analysis(cart_items):
    # Load API key and set OpenAI client
    api_key = load_openai_key()
    client = OpenAI(api_key=api_key)
    
    # Get cart summary
    cart_items_list = format_cart_summary(cart_items)
    cart_summary = ", ".join(cart_items_list)
    
    # Get available products as JSON for the AI
    available_products = load_products()
    
    prompt = f"""
    Customer has: {cart_summary}
    
    Available products (JSON): {json.dumps(available_products)}
    
    Suggest 2 complementary products as JSON:
    {{"recommendations": [{{"product_name": "Exact Name", "reason": "Brief reason"}}]}}
    """
    
    # Craft GPT Response
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.3
    )
    
    # Strip ai response from JSON
    ai_response = response.choices[0].message.content.strip()
    analysis = json.loads(ai_response)
    return {"recommendations": analysis.get("recommendations", [])}

def display_cart(cart_items):
    #Check whether to display edit mode
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False

    st.header("📋 Order Summary")
    cart_changed = False
    
    #Loop to set display info
    for product_key, quantity in list(cart_items.items()):
        product_info = get_product_info(product_key)
        price = product_info["price"]
        
        col1, col2, col3 = st.columns([2.5, 1.8, 0.7])
        
        #Product details
        with col1:
            st.write(f"**{product_info['name']}**")
            st.caption(f"${price:.2f} each")
        #Quantity
        with col2:
            #For edit mode
            if st.session_state.edit_mode:
                new_quantity = st.number_input(
                    "Qty", min_value=0, max_value=99, value=quantity,key=f"qty_{product_key}", label_visibility="collapsed"
                )
                # Update cart if quantity changed
                if new_quantity != quantity:
                    if new_quantity == 0:
                        del st.session_state.cart[product_key]
                    else:
                        st.session_state.cart[product_key] = new_quantity
                    cart_changed = True
            else:
                #If Not in edit mode, just display Qty
                st.write(f"Qty: {quantity}")
        
        with col3:
            if st.session_state.edit_mode:
                #Remove item if editing
                with st.container():
                    if st.button("🗑️", key=f"del_{product_key}", use_container_width=True):
                        del st.session_state.cart[product_key]
                        cart_changed = True
            # Else display quantity
            else:
                st.write(f"${price * quantity:.2f}")
    
    #Reload if the cart has changed
    if cart_changed:
        st.rerun()