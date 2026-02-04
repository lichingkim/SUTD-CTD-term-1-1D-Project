import streamlit as st
#import mylibrary
if("cart" not in st.session_state):
    st.session_state.cart = []

# Page configuration
st.set_page_config(page_title="Yan Yan.co")

# Title
st.title("Yan Yan.co")
st.text("Hand made with love by Elicia")
st.markdown("---")

#header
st.header("Our products")

#function for display product
def display_product(textfile, tab_key):

    product = []
    with open(textfile, "r") as txt_file:
        for line in txt_file:
            if(line == "\n"):
                break
            else:
                name, price, image = line.split(",")
                product.append({
                    "name": name.strip(),
                    "price": round(float(price.strip()), 2), 
                    "image": image.strip()
                })

    for row in range(0, len(product), 3):
        cols = st.columns(3)

        for product_exist in range(3):
            if(row + product_exist < len(product)):
                product_final = product[row + product_exist]

                with cols[product_exist]: 
                    st.image(product_final["image"])
                    st.subheader(product_final["name"])
                    st.write(f"${product_final['price']:.2f}")

                    quantity = 0 # Check if item is in cart and get quantity, this in memory
                    for item in st.session_state.cart:
                        if (item["name"] == product_final["name"]):
                            quantity = item["quantity"]
                            break

                    button_col1, button_col2, button_col3 = st.columns(3) # Create 3 columns for buttons
                    
                    with button_col1: # display minus button
                        minus_key = f"{tab_key}_minus_{row}_{product_exist}"
                        if st.button("➖", key=minus_key):
                            for item in st.session_state.cart:
                                if item["name"] == product_final["name"]:
                                    if item["quantity"] > 1:
                                        item["quantity"] -= 1
                                    else:
                                        st.session_state.cart.remove(item)
                                    break
                            st.rerun()

                    with button_col2: #display quanlity
                        st.write(f"**{quantity}**")

                    with button_col3: #display + button
                        plus_key = f"{tab_key}_plus_{row}_{product_exist}"
                        if st.button("➕", key=plus_key):
                            found = False
                            for item in st.session_state.cart:
                                if item["name"] == product_final["name"]:
                                    item["quantity"] += 1
                                    found = True
                                    break
                            if not found:
                                product_to_add = {
                                    "name": product_final["name"],
                                    "price": product_final["price"],
                                    "image": product_final["image"],
                                    "quantity": 1
                                }
                                st.session_state.cart.append(product_to_add)
                            st.rerun()

#tabs
tab1, tab2, tab3 = st.tabs(["Single", "Couple Set", "DIY Kit"])
with tab1:
    display_product("single.txt", "single")
with tab2: 
    display_product("couple.txt", "couple")
with tab3: 
    display_product("diykit.txt", "diykit")
#sidebar
with st.sidebar:
    st.title("My Cart")
    if len(st.session_state.cart) == 0:
        st.write("Your shopping cart is empty.")
    else:
        total = 0
        for item in st.session_state.cart:
            col1, col2 = st.columns([1,1])
            with col1: 
                st.write("x {}".format(item['quantity']))
            with col2:
                st.write("{} - ${:.2f}".format(item["name"], item["price"]))
            
        st.markdown("---")
        st.button("Check out", key="Checkout")