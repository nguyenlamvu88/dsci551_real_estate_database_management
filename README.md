# Property Management System

## Overview

This comprehensive Property Management System is designed for efficient handling of property listings through a robust backend and an intuitive frontend. The backend, developed in Python, interacts with MongoDB to manage property data. The frontend, powered by Streamlit, offers a user-friendly web interface for streamlined property management tasks.

## Accessing the Web Application

The Property Management System web application can be accessed through the link: [Property Management System Web Application](https://bit.ly/3xHxiNZ). This allows for direct interaction with the system via a web browser.

## Backend (Python) – `backend_v12.py`

### Features Include:

- **Database Initialization**: Sets up necessary indexes to optimize query performance.
- **User Authentication**: Supports secured user registration and login.
- **Property Insertion**: Facilitates the insertion of new property listings with validation to ensure data integrity. Each listing is linked to the user who created it.
- **Property Searching**: Enables property searches based on various criteria such as city, state, type, and custom identifiers, with optional sorting by price.
- **Property Updating**: Allows updates to existing property listings by specifying the property's custom identifier and the fields to be updated. Only the creator of a property can update their listings
- **Property Deletion**: Supports the deletion of property listings from the database using the property's custom identifier. Only the creator of a property can delete their listings.
- **Export Functionality**: Enables exporting search results into CSV or JSON formats for external use or analysis.
- **Interactive Mode**: Provides an interactive mode for insert, search, update, and delete operations, guiding users through the process with prompts.

### Usage Instructions
#### Change to the directory where `backend_v12.py` is saved and run the following commands:

##### Authenticaion Example:
The username and password are set as environment variables (MYAPP_USERNAME and MYAPP_PASSWORD), users only need to log in once per session, simplifying subsequent command executions.
- **Registering a new user**: `python backend_v12.py --register --username "user" --password "password"`
- **Logging in**: `python backend_v12.py --username "user" --password "password"`

##### Command-Line Interface Example
- **Initialize Database**: `python backend_v12.py --init`
  
- **Insert a Property**: `python backend_v12.py --username "user" --password "password" --operation insert --address "14631 Deer Park St" --city "Irvine" --state "California" --zip_code 92604 --price 1688888 --bedrooms 4 --bathrooms 3 --square_footage 2089 --type "sale" --date_listed "2024-04-01" --description "Charming downtown home" --images "img1.jpg,img2.jpg"`
  
- **Search for Properties**: `python backend_v12.py --username "user" --password "password" --operation search --state "California" --city "San Francisco"`
  
- **Update a Property**: `python backend_v12.py --username "user" --password "password" --operation update --custom_id "CAL-IRVI-14631DeerParkSt" --updates "bedrooms=4" "bathrooms=2.5" "price=675000"`
  
- **Delete a Property**: `python backend_v12.py --username "user" --password "password" --operation delete --custom_id "CAL-IRVI-14631DeerParkSt"`

##### Interactive Interface Example

- **Interactive Insert**: `python backend_v12.py --username "user" --password "password" --operation interactive_insert`
- **Interactive Search**: `python backend_v12.py --username "user" --password "password" --operation interactive_search`
- **Interactive Update**: `python backend_v12.py --username "user" --password "password" --operation interactive_update`
- **Interactive Delete**: `python backend_v12.py --username "user" --password "password" --operation interactive_delete`

### Function Descriptions

#### Authentication Functions
- **`register_user`**: Registers a new user by securely hashing their password and storing it in MongoDB.
- **`authenticate_user`**: Validates user login attempts against stored hashed passwords to ensure secure access.

#### Database and Initialization Functions
- **`check_connection`**: Ensures MongoDB connectivity.
- **`initialize_indexes`**: Sets up indexes for improved query performance.

#### Property Management Functions
- **`create_custom_id`**, **`get_database`**: Manage property identification and database allocation.
- **`validate_property_data`**: Confirms property data matches schema requirements.
- **`property_already_exists`**, **`duplicate_property`**, **`insert_property`**, **`search_property`**, **`update_property`**, **`delete_property`**: Facilitate CRUD operations on property listings.

#### Export Functions
- **`export_to_csv`**, **`export_to_json`**: Allow for exporting property data to CSV or JSON formats.

#### Utility and Helper Functions
- **`prompt_for_property_data`** through **`delete_property_interactive`**: Support interactive command-line operations for property management.

## Frontend (Streamlit) – `frontend_v12.py`

### Usage Instructions

Change to the directory where `frontend_v12.py` is saved and run the frontend application by executing:

`streamlit run frontend_v12.py`

### Function Descriptions

#### Authentication Functions
- **`hash_password`**, **`insert_new_user`**: Handle user password security and registration.
- **`login_ui`**, **`registration_ui`**: Render and manage login and registration interfaces.

#### Image Handling Functions
- **`image_to_base64`**, **`convert_image_to_base64`**: Convert and process images for web display.
- **`display_image_in_base64`**: Show property images within the web application.

#### UI Components
- **`display_logo`**: Presents the system's logo and branding.
- **`add_property_ui`**, **`search_property_ui`**, **`update_property_ui`**, **`delete_property_ui`**: Offer web-based forms and interfaces for managing property listings.

#### Export to CSV or JSON
- **`Download CSV` & `Download JSON` buttons**: Allow user to download search results in JSON or CSV format.
