import streamlit as st
import base64
from bson import ObjectId
from backend_v12 import insert_property, search_property, update_property, delete_property
from PIL import Image
import bcrypt
from io import BytesIO
from pymongo import MongoClient
import pandas as pd
import json


# Constants for the states list and file types for images
STATES_LIST = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
    "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
    "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri",
    "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York",
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island",
    "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin", "Wyoming"
]
ACCEPTED_IMAGE_TYPES = ['jpg', 'png']


# MongoDB connection setup
MONGO_URI = 'mongodb+srv://nguyenlamvu88:Keepyou0ut99!!@cluster0.ymo3tge.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(MONGO_URI)

# Database and collection names
db = client['authentication']
users_collection = db['login_info']


def hash_password(password):
    """Hash a password before storing it."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def insert_new_user(username, hashed_password):
    try:
        existing_user = users_collection.find_one({"username": username})
        if existing_user:
            st.error("Username already exists. Please choose a different username.")
            return False

        # Ensure the password hash is decoded to a string before storage if not already handled
        result = users_collection.insert_one({
            "username": username,
            "hashed_password": hashed_password.decode('utf-8')  # decode bytes to string
        })
        if result.inserted_id:
            return True
        else:
            st.error("Failed to insert new user.")
            return False
    except Exception as e:
        st.error(f"Exception occurred while registering user: {e}")
        return False


def login_ui():
    st.sidebar.subheader("Login")
    username = st.sidebar.text_input("Username", key="login_username")
    password = st.sidebar.text_input("Password", type="password", key="login_password")
    if st.sidebar.button("Login"):
        # Here you would have your logic to authenticate the user.
        # This is typically a function that returns True if the login is successful.
        user_info = users_collection.find_one({"username": username})
        if user_info and bcrypt.checkpw(password.encode('utf-8'), user_info['hashed_password'].encode('utf-8')):
            # If the user is successfully authenticated, you set the session state.
            st.session_state['authenticated'] = True
            st.session_state['username'] = username  # This line sets the username in the session state
            st.sidebar.success("You are logged in.")
            st.experimental_rerun()
        else:
            st.sidebar.error("Incorrect username or password.")


def registration_ui():
    """Create a registration interface for new users."""
    st.sidebar.subheader("Register New Account")
    with st.sidebar.form("registration_form"):
        new_username = st.text_input("New Username", key="new_username_reg")
        new_password = st.text_input("New Password", type="password", key="new_password_reg")
        submit_button = st.form_submit_button("Register")
        if submit_button:
            if new_username and new_password:
                hashed_password = hash_password(new_password)
                if insert_new_user(new_username, hashed_password):
                    st.sidebar.success("User registered successfully.")
                else:
                    st.sidebar.error("Registration failed. Username might already exist.")
            else:
                st.sidebar.error("Username and password cannot be empty.")


def image_to_base64(image_path):
    """
    Convert an image file to a base64 string.
    """
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception as e:
        st.error(f"Error reading image file: {e}")
        return None


def display_logo(url: str):
    """
    Display the company logo and title in the Streamlit app using an image URL.
    """
    # Use the URL directly in the img src attribute
    logo_html = f"<img src='{url}' class='img-fluid' width='350'>"
    st.markdown(f"""
        <div style="display: flex; align-items: center;">
            {logo_html}
            <h1 style="margin: 0 0 0 50px;">Majestic Real Estate Management</h1>
        </div>
        <div class="space"></div>
        """, unsafe_allow_html=True)


def convert_image_to_base64(uploaded_image, size=(600, 400)):
    """
    Convert an uploaded image to a base64 string for storage.
    """
    try:
        # Extract file extension from filename and normalize to uppercase
        filename = uploaded_image.name
        file_extension = filename.split(".")[-1].lower()  # Ensure extension is in lowercase
        if file_extension not in ['jpg', 'png']:
            raise ValueError("Invalid file type")

        # Open the uploaded image with PIL
        image = Image.open(uploaded_image)

        # Resize the image
        resized_image = image.resize(size)

        # Save the resized image to a buffer, specifying format explicitly
        buffer = BytesIO()
        format = 'JPEG' if file_extension == 'jpg' else file_extension.upper()
        resized_image.save(buffer, format=format)  # Use explicit format
        buffer.seek(0)

        # Convert the image in the buffer to a base64 string
        b64_encoded = base64.b64encode(buffer.read()).decode()

        return f"data:image/{file_extension};base64,{b64_encoded}"
    except Exception as e:
        st.error(f"An error occurred while converting image to base64: {e}")
        return None


def display_image_in_base64(base64_string):
    st.markdown(
        f"<img src='{base64_string}' class='img-fluid'>", unsafe_allow_html=True
    )


def add_property_ui():
    """
    UI for adding a new property.
    """
    st.subheader("🏡 Add a New Property")
    with st.form(key='add_property_form'):
        col1, col2 = st.columns(2)
        with col1:
            address = st.text_input("Address")
            city = st.text_input("City")
            state = st.selectbox("State", STATES_LIST)
            zip_code = st.text_input("ZIP Code")
        with col2:
            price = st.number_input("Price ($)", min_value=0, value=150000, step=50000, format="%d")
            bedrooms = st.number_input("Bedrooms", min_value=0, value=3, step=1)
            bathrooms = st.number_input("Bathrooms", min_value=0.0, value=2.0, step=0.5)
            square_footage = st.number_input("Square Footage", min_value=0, value=1000, step=100)
        property_type = st.selectbox("Type", ["Sale", "Rent"])
        date_listed = st.date_input("Date Listed")
        description = st.text_area("Description")
        uploaded_images = st.file_uploader("Upload Property Images", accept_multiple_files=True,
                                           type=ACCEPTED_IMAGE_TYPES)
        submit_button = st.form_submit_button(label='Add Property')

        if submit_button:
            image_strings = [convert_image_to_base64(image) for image in uploaded_images] if uploaded_images else []
            property_data = {
                "address": address,
                "city": city,
                "state": state,
                "zip_code": int(zip_code) if zip_code.isdigit() else 0,
                "price": price,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "square_footage": square_footage,
                "type": property_type.lower(),
                "date_listed": str(date_listed),
                "description": description,
                "images": image_strings
            }
            # Retrieve the username from session state
            username = st.session_state.get('username', None)
            if username:
                try:
                    success = insert_property(property_data, username)
                    if success:
                        st.success("Property added successfully!")
                    else:
                        st.error("Failed to add property. Please check the input data.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
            else:
                st.error("User not logged in. Please log in to add properties.")


# Custom JSON Encoder to handle MongoDB ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)  # Convert ObjectId to string
        return json.JSONEncoder.default(self, o)


def display_image(base64_string):
    if isinstance(base64_string, str):
        # Check if the string is a URL or base64
        if base64_string.startswith('http') or base64_string.startswith('data:image'):
            st.image(base64_string, use_column_width=True)
        else:
            st.error('Invalid image URL or base64 string')
    else:
        st.error('Invalid image data')


def search_property_ui():
    st.subheader("🔍 Search for Properties")
    with st.form("search_form"):
        city = st.text_input("City", help="partial match allowed, case-insensitive")
        state = st.text_input("State", help="partial match allowed, case-insensitive")
        property_type = st.text_input("Type", help="sale or rent, case-insensitive")
        address = st.text_input("Address", help="partial match allowed, case-insensitive")
        custom_id = st.text_input("Custom ID")
        sort_by_price = st.selectbox("Sort by Price", ["None", "Ascending", "Descending"], index=0)

        submit = st.form_submit_button("Search")

    if submit:
        sort_option = 'asc' if sort_by_price == "Ascending" else 'desc' if sort_by_price == "Descending" else None
        search_results = search_property(city=city, state=state, property_type=property_type.lower(), address=address, custom_id=custom_id, sort_by_price=sort_option)
        unique_properties = {prop['custom_id']: prop for prop in search_results}
        unique_search_results = list(unique_properties.values())

        if unique_search_results:
            st.success(f"Found {len(unique_search_results)} unique properties.")
            for property in unique_search_results:
                with st.expander(f"{property.get('address', 'No Address Provided')}, {property.get('city', 'Unknown City')}, {property.get('state', 'Unknown State')} {property.get('zip_code', 'Unknown ZIP')}"):
                    st.markdown(
                        f"<span style='font-weight:bold; color: dark blue;'>{property.get('address', 'No Address Provided')}</span>",
                        unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**Property ID:** `{property.get('custom_id')}`")
                        st.markdown(f"**City:** `{property.get('city', 'N/A')}`")
                        st.markdown(f"**State:** `{property.get('state', 'N/A')}`")
                    with col2:
                        price = property.get('price', 'N/A')
                        formatted_price = f"${price:,.0f}" if isinstance(price, int) else "N/A"
                        st.markdown(f"**Price:** `{formatted_price}`", unsafe_allow_html=True)
                        st.markdown(f"**Bedrooms:** `{property.get('bedrooms', 'N/A')}`")
                        st.markdown(f"**Bathrooms:** `{property.get('bathrooms', 'N/A')}`")
                    with col3:
                        st.markdown(f"**Square Footage:** `{property.get('square_footage', 'N/A')}`")
                        st.markdown(f"**Type:** `{property.get('type', 'N/A')}`")
                        st.markdown(f"**Listed Date:** `{property.get('date_listed', 'N/A')}`")

                    st.markdown(f"**Description:** {property.get('description', 'N/A')}")
                    images = property.get('images', [])
                    if images:
                        for img in images:
                            display_image(img)

            # Global download buttons for all search results
            json_data = json.dumps(unique_search_results, indent=4, cls=JSONEncoder).encode('utf-8')
            df = pd.DataFrame(unique_search_results).drop(columns=['images'], errors='ignore')
            csv_data = df.to_csv(index=False).encode('utf-8')

            st.download_button("Download JSON", json_data, "search_results.json", "application/json", key='download-json')
            st.download_button("Download CSV", csv_data, "search_results.csv", "text/csv", key='download-csv')
        else:
            st.warning("No properties found matching the criteria.")


def insert_new_property(property_data, username):
    """
    Insert a new property into the database, including the username of the creator.
    """
    # Add the 'created_by' field to property_data
    property_data['created_by'] = username
    # Call your existing backend function to insert the property
    return insert_property(property_data)


def update_property_ui():
    st.subheader("✏️ Update Property Details")
    custom_id = st.text_input("Enter the Custom ID of the property to update")

    fetch_button = st.button("Fetch Property Details")
    if fetch_button and custom_id:
        property_info = search_property(custom_id=custom_id)
        if property_info:
            property_data = property_info[0]  # Assuming the first match is what we want
            owner_username = property_data.get('created_by')

            # Check if the logged-in user is the owner of the property
            if st.session_state.get('username') == owner_username:
                st.session_state['property_data'] = property_data
                st.success("Property details fetched. You can now update the property.")
            else:
                st.error("You are not authorized to update this property.")
        else:
            st.error("Property not found. Please check the Custom ID.")

    if 'property_data' in st.session_state:
        property_data = st.session_state['property_data']
        with st.form("update_form"):
            new_price = st.number_input(
                "Price ($)", value=float(property_data.get('price', 0)),
                min_value=0.0, step=50000.0, format="%.2f"
            )
            new_bedrooms = st.number_input("Bedrooms", value=property_data.get('bedrooms', 0), min_value=0)
            new_bathrooms = st.number_input("Bathrooms", value=property_data.get('bathrooms', 0.0), min_value=0.0, step=0.5)
            new_square_footage = st.number_input("Square Footage", value=property_data.get('square_footage', 0), min_value=0, step=100)
            new_type = st.selectbox("Type", ["Sale", "Rent"], index=0 if property_data.get('type', 'sale') == 'sale' else 1)
            new_listed_date = st.date_input("Listed Date", value=pd.to_datetime(property_data.get('date_listed')))
            new_description = st.text_area("Description", value=property_data.get('description', ''))
            submit_update = st.form_submit_button("Update Property")

            if submit_update:
                updates = {
                    "price": new_price,
                    "bedrooms": new_bedrooms,
                    "bathrooms": new_bathrooms,
                    "square_footage": new_square_footage,
                    "type": new_type.lower(),
                    "listed_date": new_listed_date.strftime("%Y-%m-%d"),
                    "description": new_description
                }
                username = st.session_state.get('username')
                if username:
                    result = update_property(custom_id, updates, username=username)
                    if result:
                        st.success("Property updated successfully!")
                        del st.session_state['property_data']  # Clear the stored data
                    else:
                        st.error("Failed to update property. Please check the input data and try again.")
                else:
                    st.error("You must be logged in to update a property.")


def delete_property_ui():
    st.subheader("🗑️ Delete a Property")
    custom_id = st.text_input("Enter the Custom ID of the property to delete", key='delete_property_custom_id')

    if custom_id:
        fetch_button = st.button("Fetch Property Details")
        if fetch_button:
            property_info = search_property(custom_id=custom_id)
            if property_info:
                property_data = property_info[0]
                st.session_state['property_data_to_delete'] = property_data
                st.success("Property details fetched. Confirm deletion below.")
            else:
                st.error("Property not found. Please check the Custom ID.")
                if 'property_data_to_delete' in st.session_state:
                    del st.session_state['property_data_to_delete']

        if 'property_data_to_delete' in st.session_state:
            property_data = st.session_state['property_data_to_delete']
            st.write(f"Property Address: {property_data.get('address')}")
            st.write(f"Property ID: {property_data.get('custom_id')}")
            st.write(f"Listed by: {property_data.get('created_by')}")

            if st.session_state.get('username') == property_data.get('created_by'):
                confirm_delete = st.checkbox("Confirm you want to delete this property", value=False, key='confirm_delete')
                delete_button = st.button("Delete Property")
                if delete_button and confirm_delete:
                    username = st.session_state.get('username')
                    result = delete_property(custom_id, username)  # Pass the username as an argument
                    if result:
                        st.success("Property deleted successfully!")
                        st.session_state['reset_delete_property_custom_id'] = True  # Set the flag to reset on next run
                        # Do not clear 'delete_property_custom_id' here directly
                    else:
                        st.error("Failed to delete property. Please check the Custom ID.")
            else:
                st.error("You do not have permission to delete this property.")
    else:
        if st.button("Fetch Property Details"):
            st.warning("Please enter a Custom ID.")


def logout_ui():
    if st.sidebar.button('Logout'):
        # Clear authentication-related session state
        if 'authenticated' in st.session_state:
            del st.session_state['authenticated']
        if 'username' in st.session_state:
            del st.session_state['username']
        st.sidebar.success("You have been logged out.")
        st.experimental_rerun()


def main():
    # Safely check if the user is authenticated, defaulting to False if the key doesn't exist
    is_authenticated = st.session_state.get("authenticated", False)

    logo_url = "https://nguyenlamvu88.github.io/dsci551_data_base_management_system/landing_page_image.png"
    display_logo(logo_url)

    if is_authenticated:
        # User is authenticated, show property management operations
        st.sidebar.title("🏠 Property Management")
        operation = st.sidebar.selectbox("Choose Operation",
                                         ["Add Property", "Search Property", "Update Property", "Delete Property"])

        # Save the current operation to session state
        st.session_state['current_operation'] = operation

        if operation == "Add Property":
            add_property_ui()
        elif operation == "Search Property":
            search_results = search_property_ui()
            st.session_state['search_results'] = search_results  # Store search results in session state
        elif operation == "Update Property":
            update_property_ui()
        elif operation == "Delete Property":
            delete_property_ui()

        logout_ui()  # Call the logout UI function

    else:
        # User is not authenticated, show login and optionally registration UI
        if 'logout' in st.session_state:
            del st.session_state['username']  # Ensure user details are cleared on logout
        login_ui()
        registration_ui()


if __name__ == "__main__":
    main()
