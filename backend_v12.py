import re

import bcrypt
from pymongo import MongoClient, ASCENDING, DESCENDING
import logging
import hashlib
import argparse
import sys
import json
from bson import ObjectId
import csv
import datetime
import os
from PIL import Image
from io import BytesIO
import base64


"""
Property Management System

This script provides a comprehensive solution for managing property listings, utilizing MongoDB for storage and management. 
It supports a variety of operations such as inserting, searching, updating, and deleting property information, facilitated through both command-line arguments and interactive prompts.

Features include:
- Database Initialization: Prepares the database by creating necessary indexes to optimize query performance.
- User Authentication: Supports user registration and login to secure access to property management functionalities.
- Property Insertion: Allows for the insertion of new property listings into the database, with input validation to ensure data integrity.
- Property Searching: Supports searching for properties based on criteria such as city, state, type, and custom identifiers, with optional sorting by price.
- Property Updating: Enables updating existing property listings by specifying the property's custom identifier and the fields to be updated.
- Property Deletion: Allows for the deletion of property listings from the database using the property's custom identifier.
- Export Functionality: Provides the ability to export search results into CSV or JSON formats for external use or analysis.
- Interactive Mode: Offers an interactive mode for insert, search, update, and delete operations, guiding users through the process with prompts.

Usage:
- The script is designed to be used from the command line, with specific flags and arguments to control its operations. Users must register and log in to access the property management functionalities securely. 
- Additionally, the script supports interactive modes for inserting, searching, updating, and deleting properties, which provide a user-friendly interface for carrying out these operations.

Dependencies:
- pymongo: For MongoDB interactions.
- logging: For logging information and errors.
- hashlib: For generating hashes for custom IDs.
- argparse: For parsing command-line arguments.
- sys, json, csv, datetime, os: For various utility functions including environment variable management.


Example of Registering and Logging In:

- Registering a new user: 
  - python backend_v12.py --register --username "user" --password "password"
  
- Logging in: 
  - python backend_v12.py --username "user" --password "password"


Examples of Command-Line Interface:

- Initializes database indexes:
  - python backend_v12.py --username "user" --password "password" --init

- Inserting a Property: provide details in accordance with the property schema
  - python backend_v12.py --username "user" --password "password" --operation insert --address "14631 Deer Park St" --city "Irvine" --state "California" --zip_code 92604 --price 1688888 --bedrooms 4 --bathrooms 3 --square_footage 2089 --type "sale" --date_listed "2024-04-01" --description "Charming downtown home" --images "img1.jpg,img2.jpg" 

- Searching for Properties: use any combination of city, state, type, and address
  - python backend_v12.py --username "user" --password "password" --operation search --city "Irvine" --type "sale"
  - python backend_v12.py --username "user" --password "password" --operation search --custom_id "CAL-IRVI-14631"
  - python backend_v12.py --username "user" --password "password" --operation search --state "California" --city "San Francisco"

- Updating a Property: need to provide its custom ID and the updates in a field=value format, separate by space
  - python backend_v12.py --username "user" --password "password" --operation update --custom_id "CAL-IRVI-14631" --updates "bedrooms=4" "bathrooms=2.5" "price=675000" 

- Deleting a Property: provide its custom ID
  - python backend_v12.py --username "user" --password "password" --operation delete --custom_id "CAL-IRVI-14631"


Examples of Interactive Modes:

- Initializes database indexes:
  - python backend_v12.py --username "user" --password "password" --init

- Inserting a Property: Follow the prompts for each property detail
  - python backend_v12.py --username "user" --password "password" --operation interactive_insert

- Searching for Properties: Follow the prompts for search criteria
  - python backend_v12.py --username "user" --password "password" --operation interactive_search

- Updating a Property: Follow the prompts to specify the property and updates
  - python backend_v12.py --username "user" --password "password" --operation interactive_update

- Deleting a Property: Follow the prompt to enter the Custom ID of the property to delete
  - python backend_v12.py --username "user" --password "password" --operation interactive_delete


Security Note:
- The script includes a MongoDB URI with hardcoded credentials for demonstration purposes. In a production environment, it is crucial to manage sensitive information such as database URIs and credentials securely, using environment variables or configuration files.
"""


# ANSI escape codes for text colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
PURPLE = "\033[95m"
RESET = "\033[0m"  # Reset to default color

dt_now = datetime.datetime.now()
# The format to include time (e.g., "15-Mar-24 14:30") for exporting search results to json and csv files
formatted_dt = dt_now.strftime("%d-%b-%y %H:%M")

# Initialize logging
logging.basicConfig(level=logging.INFO)

# MongoDB connection
MONGO_URI = 'mongodb+srv://nguyenlamvu88:Keepyou0ut99!!@cluster0.ymo3tge.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(MONGO_URI)

# Database names
DATABASE_NAMES = ['properties_db1', 'properties_db2', 'properties_db3', 'properties_db4']

# Property schema for validation
property_schema = {
    "address": str,
    "city": str,
    "state": str,
    "zip_code": int,
    "price": (int, float),
    "bedrooms": int,
    "bathrooms": float,
    "square_footage": int,
    "type": str,
    "date_listed": str,
    "description": str,
    "images": list
}


def check_connection():
    """
    Checks the MongoDB connection by attempting to retrieve server information.
    Logs the result and exits the application if the connection is unsuccessful.

    Raises:
        SystemExit: If the MongoDB connection cannot be established, the application will exit.
    """
    try:
        client.server_info()
        logging.info(BLUE + "\nSuccessfully connected to MongoDB." + RESET)
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        sys.exit("Exiting due to unsuccessful MongoDB connection.")


def register_user(username, password):
    """
    Registers a new user with a username and password if the username does not already exist.
    The password is hashed before storage for security.

    Args:
        username (str): The username for the new user.
        password (str): The user's password which will be hashed before storage.

    Returns:
        bool: True if registration was successful, False if the username already exists.
    """
    user_collection = client['authentication']['login_info']
    if user_collection.find_one({"username": username}):
        print("\nUsername already exists.")
        return False
    try:
        # Generate password hash
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        # Convert byte string to string before storing
        password_hash_str = password_hash.decode('utf-8')
        # Insert the user into the database
        user_collection.insert_one({'username': username, 'hashed_password': password_hash_str})
        print("\nUser registered successfully.")
        return True
    except Exception as e:
        print(f"Error during registration: {e}")
        return False


def authenticate_user(username, password):
    """
    Authenticates a user by checking the provided username and password against stored values.

    Args:
        username (str): The username to authenticate.
        password (str): The password to authenticate.

    Returns:
        bool: True if authentication is successful, False otherwise.
    """
    user_collection = client['authentication']['login_info']
    user = user_collection.find_one({'username': username})
    if user:
        # Retrieve the stored hash and ensure it's in bytes for comparison
        stored_hash = user['hashed_password'].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            print(BLUE + "\nLogin successful.\n" + RESET)
            return True
    print("\nLogin failed. Please check your username and password.")
    return False


def initialize_indexes():
    """
    Creates indexes on commonly queried fields across all configured databases to enhance query performance.
    Indexes are created for 'city', 'state', 'type', 'address', and 'custom_id' fields.
    """
    index_fields = ['city', 'state', 'type', 'address', 'custom_id']
    for db_name in DATABASE_NAMES:
        db = client[db_name]
        properties_collection = db['properties']
        for field in index_fields:
            properties_collection.create_index([(field, 1)])
            logging.info(f"Index on '{field}' created in {db_name}.")


def create_custom_id(state, city, address):
    """
    Generates a custom ID using the state, city, and address information.
    This ID is used as a unique identifier for properties within the database.

    Args:
        state (str): The state where the property is located.
        city (str): The city where the property is located.
        address (str): The property's address.

    Returns:
        str: A custom ID generated based on the state, city, and address.
    """
    state_abbr = state[:3].upper().strip()
    city_abbr = ''.join(city.split())[:4].upper()

    # Use regular expression to extract the first numeric part and the first four words of the street name
    address_parts = re.search(r'(\d+)\s+([\w]+\s+[\w]+\s+[\w]+\s+[\w]+|\w+\s+\w+\s+\w+|\w+\s+\w+|\w+)', address)
    if address_parts:
        address_num = address_parts.group(1)  # First group: numbers
        street_name_part = address_parts.group(2)  # Second group: first four words of the street name
        # Replace spaces
        street_name_part = street_name_part.replace(" ", "")
    else:
        address_num = '0000'  # Default if no number is found
        street_name_part = 'NoStreet'  # Default if no street name is found

    custom_id = f"{state_abbr}-{city_abbr}-{address_num}{street_name_part}"
    return custom_id


def get_database(custom_id):
    """
    Validates the given property data against the defined schema, ensuring all required fields are present and correctly formatted.

    Args:
        property_data (dict): The property data to validate.

    Raises:
        ValueError: If any field is missing or incorrectly formatted.
    """
    hash_obj = hashlib.sha256(custom_id.encode())
    hash_value = int(hash_obj.hexdigest(), 16)
    db_index = hash_value % len(DATABASE_NAMES)
    return client[DATABASE_NAMES[db_index]]


def generate_hash_for_duplication(custom_id, exclude_db):
    """
    Generates a hash to decide the target database for property data duplication, excluding the specified database.

    Args:
        custom_id (str): The custom ID of the property.
        exclude_db (str): The name of the database to exclude from selection.

    Returns:
        str: The name of the target database for duplication.
    """
    hash_obj = hashlib.sha256(custom_id.encode())
    hash_value = int(hash_obj.hexdigest(), 16)

    # Use a different modulus operation or logic to select the target database for duplication
    target_db_index = hash_value % (len(DATABASE_NAMES) - 1)  # Exclude the original database

    # Adjust the index if the calculated index is equal to or greater than the index of the excluded database
    if DATABASE_NAMES.index(exclude_db) <= target_db_index:
        target_db_index += 1

    return DATABASE_NAMES[target_db_index]


def validate_property_data(property_data):
    """
    Validates the given property data against the defined schema, ensuring all required fields are present and correctly formatted.

    Args:
        property_data (dict): The property data to validate.

    Raises:
        ValueError: If any field is missing or incorrectly formatted.
    """
    optional_fields = ['images']  # Define which fields are optional

    errors = []  # List to accumulate error messages

    for key, expected_type in property_schema.items():
        # Check for missing fields
        if key not in property_data:
            if key not in optional_fields:  # Consider optional fields
                errors.append(f"Missing required field: '{key}'")
            continue

        # Ensure the field is of the correct type
        # Wrap expected_type in a tuple if it's not already one
        if not isinstance(expected_type, tuple):
            expected_type = (expected_type,)

        if not isinstance(property_data[key], expected_type):
            # Generate a friendly message for the expected types
            expected_types_formatted = ", ".join([t.__name__ for t in expected_type])
            errors.append(
                YELLOW + f"Field '{key}' is missing or has incorrect type. Expected {expected_types_formatted}, got {type(property_data[key]).__name__}\n" + RESET)

    # If there are any errors, raise an exception with all error messages
    if errors:
        error_message = "\n- " + "\n- ".join(errors)
        raise ValueError(error_message)


def property_already_exists(custom_id):
    """
    Checks if a property with the given custom_id already exists in any of the configured databases.

    Args:
        custom_id (str): The custom ID to check.

    Returns:
        bool: True if the property exists, False otherwise.
    """
    for db_name in DATABASE_NAMES:
        db = client[db_name]
        if db['properties'].find_one({"custom_id": custom_id}):
            return True
    return False


def extract_image_metadata(image_data):
    """
    Extracts and returns image metadata either from a base64 encoded string or a file path.
    This function supports both data encoded in base64 format and direct filesystem paths to images.

    Args:
        image_data (str): A string containing either a base64 encoded image or a path to an image file.

    Returns:
        dict: A dictionary containing metadata about the image such as filename, format, size, and mode.
              If an error occurs, returns a dictionary with an 'Error' key and a message.

    Raises:
        Exception: Descriptive exception if image processing fails, captured and returned in the dictionary.
    """
    try:
        if image_data.startswith('data:image'):
            # Decode the base64 image data
            base64_data = image_data.split(",")[1]
            img = Image.open(BytesIO(base64.b64decode(base64_data)))
            image_info = {
                "Filename": "Not available (Base64 data)",
                "Format": img.format,
                "Size (pixels)": img.size,
                "Mode": img.mode
            }
        else:
            # Open the image file from path
            img = Image.open(image_data)
            image_info = {
                "Filename": os.path.basename(image_data),
                "Format": img.format,
                "Size (pixels)": img.size,
                "Mode": img.mode,
                "File Size (bytes)": os.path.getsize(image_data)
            }
        img.close()
        return image_info
    except Exception as e:
        return {"Error": f"Failed to process image data: {e}"}


def duplicate_property(property_data, target_db_name):
    """
    Attempts to duplicate given property data into a specified database. Logs the result of the operation.

    Args:
        property_data (dict): A dictionary containing the data of the property to be duplicated.
        target_db_name (str): The name of the target database where the property data will be duplicated.

    Returns:
        bool: True if the duplication was successful, False otherwise, based on the insertion result.

    Raises:
        Exception: Captures any exceptions raised during the duplication process and logs them as errors.
    """
    try:
        db = client[target_db_name]
        properties_collection = db['properties']
        result = properties_collection.insert_one(property_data)
        logging.info(GREEN + f"\nProperty duplicated in {target_db_name} with same custom_id\n" + RESET)
        return True
    except Exception as e:
        logging.error(f"Failed to duplicate property in {target_db_name}: {e}")
        return False


def insert_property(property_data, username):
    """
    Inserts a property into the database after validation. If the property does not already exist,
    it is inserted into the appropriate database based on a hash of its custom ID and then duplicated
    in another database.

    Args:
        property_data (dict): Dictionary containing all the necessary data for a property.
        username (str): The username of the user creating the property. Used to associate the property with the user.

    Returns:
        bool: True if the property was successfully inserted and duplicated, False otherwise.

    Raises:
        ValueError: If the validation fails or the property already exists, indicating that
                    insertion cannot proceed.
        Exception: General exceptions that could occur during database operations are logged and re-raised.
    """
    try:
        validate_property_data(property_data)

        custom_id = create_custom_id(property_data['state'], property_data['city'], property_data['address'])
        if property_already_exists(custom_id):
            raise ValueError(RED + f"Property with custom_id {custom_id} already exists.\n" + RESET)

        property_data['custom_id'] = custom_id

        # Associate the property with the username
        property_data['created_by'] = username

        # Original insertion
        original_db = get_database(custom_id)
        properties_collection = original_db['properties']
        result = properties_collection.insert_one(property_data)
        logging.info(GREEN + f"\nProperty inserted in {original_db.name} with custom_id: {custom_id} and _id: {result.inserted_id}" + RESET)

        # Determine the target database for duplication
        target_db_name = generate_hash_for_duplication(custom_id, original_db.name)
        # Perform the duplication
        duplicate_property(property_data, target_db_name)

        return True
    except ValueError as ve:
        logging.error(RED + f"\nValidation error: {ve}" + RESET)
        return False
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return False


def search_property(city=None, state=None, property_type=None, address=None, custom_id=None, sort_by_price=None):
    """
    Searches properties based on provided criteria. Supports filtering by city, state, property type, and address.
    Properties can optionally be sorted by price in ascending or descending order.

    Args:
        city (str, optional): Filter properties by city.
        state (str, optional): Filter properties by state.
        property_type (str, optional): Filter properties by type (e.g., 'sale', 'rent').
        address (str, optional): Filter properties by address.
        custom_id (str, optional): Filter properties by a specific custom ID.
        sort_by_price (str, optional): Sort the results by price, either 'asc' for ascending or 'desc' for descending.

    Returns:
        list: A list of dictionaries, each representing a property that matches the search criteria.

    Notes:
        This function queries multiple databases and aggregates results into a single list, adjusting for unique IDs.
    """

    all_properties = {}
    query = {}

    # Building the query based on function parameters
    if custom_id:
        query["custom_id"] = custom_id
    else:
        if city:
            query["city"] = {"$regex": city, "$options": "i"}
        if state:
            query["state"] = {"$regex": state, "$options": "i"}
        if property_type:
            query["type"] = {"$regex": property_type, "$options": "i"}
        if address:
            query["address"] = {"$regex": address, "$options": "i"}

    # Query each database and collect results
    for db_name in DATABASE_NAMES:
        db = client[db_name]
        properties_collection = db['properties']
        results = list(properties_collection.find(query))
        for property in results:
            # Use custom_id as a unique key for each property
            cid = property["custom_id"]
            if cid in all_properties:
                # If this property is already listed, append the new database name to 'source_db'
                all_properties[cid]["source_db"].append(db_name)
            else:
                # Otherwise, add the property to the dictionary
                property["source_db"] = [db_name]
                all_properties[cid] = property

    # Convert the dictionary back to a list for sorting and further processing
    properties_list = list(all_properties.values())

    # Applying global sorting based on the 'sort_by_price' parameter
    if sort_by_price:
        properties_list.sort(key=lambda x: x['price'], reverse=(sort_by_price == 'desc'))

    return properties_list


def export_to_csv(properties, filename=None):
    if filename is None:
        filename = f'search_results_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            if properties:
                writer = csv.DictWriter(file, fieldnames=properties[0].keys())
                writer.writeheader()
                for prop in properties:
                    writer.writerow(prop)
                print(GREEN + f"Results exported to CSV file: {filename}\n" + RESET)
            else:
                print(RED + "No properties to export.\n" + RESET)
    except Exception as e:
        logging.error(f"Error exporting to CSV: {e}")


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)


def export_to_json(properties, filename=None):
    if filename is None:
        filename = f'search_results_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.json'
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            if properties:
                json.dump(properties, file, ensure_ascii=False, indent=4, cls=CustomEncoder)
                print(GREEN + f"Results exported to JSON file: {filename}\n" + RESET)
            else:
                print(RED + "No properties to export.\n" + RESET)
    except Exception as e:
        logging.error(f"Error exporting to JSON: {e}")


def update_property(custom_id, updates, username):
    """
    Updates a property specified by its custom ID with the given updates. This operation is attempted
    across all databases where the property might be replicated.

    Args:
        custom_id (str): The unique identifier for the property, used to locate it in the database.
        updates (dict): A dictionary containing the fields to be updated and their new values.
                        Fields expected to be type-converted are explicitly handled.
        username (str): Username of the user requesting the update. This is used to verify permissions.

    Returns:
        bool: True if the update operation was successful in at least one database, False otherwise.

    Raises:
        ValueError: If the type conversion for any of the update fields fails.
        Exception: Logs any exceptions raised during the database operations, including permission issues
                   and non-existence of the property under the specified ID.

    Notes:
        The function checks whether the logged-in user has the right to modify the property and updates the property
        if they are the creator. It logs detailed information about the outcome of each update attempt across
        multiple databases.
    """
    # Specify the expected type for each field that needs type conversion
    field_types = {
        'price': int,
        'bedrooms': int,
        'bathrooms': float,
    }

    # Convert field values based on their expected type
    for field, value in updates.items():
        if field in field_types:
            try:
                # Attempt to convert the value to the specified type
                updates[field] = field_types[field](value)
            except ValueError as e:
                logging.error(YELLOW + f"Error converting field '{field}' with value '{value}': {e}" + RESET)
                return False

        update_successful = False
    update_attempts = 0

    # Retrieve the property to check if the user is the creator
    original_db = get_database(custom_id)
    property_data = original_db['properties'].find_one({"custom_id": custom_id})

    if not property_data or property_data.get('created_by') != username:
        logging.error(RED + "You do not have permission to update this property.\n" + RESET)
        return False

    # Iterate over each database to update the property
    for db_name in DATABASE_NAMES:
        db = client[db_name]
        properties_collection = db['properties']
        result = properties_collection.update_one({"custom_id": custom_id}, {"$set": updates})

        if result.matched_count > 0:
            logging.info(GREEN + f"Property with custom_id {custom_id} updated in {db_name}." + RESET)
            update_successful = True
        else:
            logging.warning(YELLOW + f"Property with custom_id {custom_id} not found in {db_name}.\n" + RESET)

        update_attempts += 1

    return True  # Return True if update is successful


def delete_property(custom_id, username):
    """
    Deletes a property from all databases based on its custom ID, if the user has the necessary permissions.

    Args:
        custom_id (str): The unique identifier for the property to be deleted.
        username (str): The username of the user requesting the deletion.

    Returns:
        bool: True if the property was successfully deleted from all databases, False if the deletion was
              unsuccessful or the user did not have permission to delete the property.

    Notes:
        The operation checks whether the user is the creator of the property. If not, the deletion is not allowed.
        The function logs each attempt to delete the property across databases and confirms the deletion success.
    """
    original_db = get_database(custom_id)
    property_data = original_db['properties'].find_one({"custom_id": custom_id})

    if not property_data or property_data.get('created_by') != username:
        logging.error(RED + "You do not have permission to delete this property.\n" + RESET)
        return False

    deletion_successful = False
    deletion_attempts = 0

    # Iterate over each database to delete the property
    for db_name in DATABASE_NAMES:
        db = client[db_name]
        properties_collection = db['properties']
        result = properties_collection.delete_one({"custom_id": custom_id})

        if result.deleted_count > 0:
            logging.info(GREEN + f"Property with custom_id {custom_id} deleted from {db_name}.\n" + RESET)
            deletion_successful = True

        deletion_attempts += 1

    # Check if the deletion attempts were made across all databases
    if deletion_successful and deletion_attempts == len(DATABASE_NAMES):
        return True
    else:
        return False


def prompt_for_property_data():
    """
    Prompts the user for property details, collects the responses, and returns a property data dictionary.
    """
    print(BLUE + "Please enter the property details." + RESET)

    # List of fields to prompt for, with friendly display names and any special handling required
    fields = [
        ("address", "Address"),
        ("city", "City"),
        ("state", "State"),
        ("zip_code", "Zip Code", int),  # Special handling to convert to int
        ("price", "Price", float),  # Special handling to convert to float
        ("bedrooms", "Number of Bedrooms", int),
        ("bathrooms", "Number of Bathrooms", float),
        ("square_footage", "Square Footage", int),
        ("type", "Property Type (e.g., sale, rent)"),
        ("date_listed", "Date Listed (YYYY-MM-DD)"),
        ("description", "Property Description"),
        # 'images' is optional and user can input multiple images separated by commas
        ("images", "Images (optional, separate multiple paths with commas)", lambda x: x.split(',') if x else []),
    ]

    property_data = {}

    for field, prompt, *special_handling in fields:
        response = input(f"{prompt}: ").strip()
        # Apply any special handling for data conversion if necessary
        if special_handling:
            try:
                converter = special_handling[0]
                property_data[field] = converter(response)
            except ValueError:
                print(RED + f"\nError: Invalid input for '{prompt}'. Please ensure the input is correct and try again." + RESET)
                return None
        else:
            property_data[field] = response

    return property_data


def insert_property_interactive(username):
    """
    Handles the 'insert' operation in an interactive manner.
    """
    property_data = prompt_for_property_data()
    if property_data:
        success = insert_property(property_data, username)  # Pass the username here
        if success:
            print(GREEN + "\nProperty inserted successfully.\n" + RESET)
        else:
            print(RED + "\nFailed to insert property.\n" + RESET)
    else:
        print(YELLOW + "Property insertion cancelled due to invalid input." + RESET)


def search_property_interactive(username=None):
    """
    Handles the 'search' operation in an interactive manner.
    """
    print(f"Logged in as: {username}")
    print(
        BLUE + "Please enter search criteria (you can search by one or multiple criteria such as city, state, or address; hit enter to skip):" + RESET)
    city = input("City: ").strip()
    state = input("State: ").strip()
    property_type = input("Property Type (e.g., sale, rent): ").strip()
    address = input("Address: ").strip()
    custom_id = input("Custom ID: ").strip()
    sort_by_price = input("Sort by price (asc/desc, leave blank for no sorting): ").strip().lower()

    search_results = search_property(city=city, state=state, property_type=property_type, address=address,
                                     custom_id=custom_id, sort_by_price=sort_by_price)

    if search_results:
        print(GREEN + f"\nFound {len(search_results)} properties:\n" + RESET)
        for property in search_results:
            print_property(property)

        # Ask user if they want to export the results
        export_choice = input("Do you want to export the results? (yes/no): ").strip().lower()
        if export_choice == 'yes':
            # Ask for the format
            format_choice = input("Which format to export? (csv/json): ").strip().lower()
            if format_choice == 'csv':
                export_to_csv(search_results)
            elif format_choice == 'json':
                export_to_json(search_results)
            else:
                print(RED + "Invalid format selected. Export cancelled." + RESET)
    else:
        print(RED + "\nNo properties found matching the criteria.\n" + RESET)


def print_property(property_info):
    print(BLUE + "------" + RESET)
    print(PURPLE + "Custom ID: " + RESET + f"{property_info.get('custom_id', 'N/A')}")
    print(PURPLE + "Address: " + RESET + f"{property_info.get('address', 'N/A')}")
    print(PURPLE + "City: " + RESET + f"{property_info.get('city', 'N/A')}")
    print(PURPLE + "State: " + RESET + f"{property_info.get('state', 'N/A')}")
    print(PURPLE + "Zip Code: " + RESET + f"{property_info.get('zip_code', 'N/A')}")
    print(PURPLE + "Price: " + RESET + f"${property_info.get('price', 'N/A')}")
    print(PURPLE + "Bedrooms: " + RESET + f"{property_info.get('bedrooms', 'N/A')}")
    print(PURPLE + "Bathrooms: " + RESET + f"{property_info.get('bathrooms', 'N/A')}")
    print(PURPLE + "Square Footage: " + RESET + f"{property_info.get('square_footage', 'N/A')}")
    print(PURPLE + "Type: " + RESET + f"{property_info.get('type', 'N/A')}")
    print(PURPLE + "Date Listed: " + RESET + f"{property_info.get('date_listed', 'N/A')}")
    print(PURPLE + "Description: " + RESET + f"{property_info.get('description', 'N/A')}")

    if 'images' in property_info and property_info['images']:
        print(PURPLE + "Images:" + RESET)
        for index, image_data in enumerate(property_info['images']):
            metadata = extract_image_metadata(image_data)
            print(f"  Image {index + 1}:")
            for key, value in metadata.items():
                print(f"    - {key}: "f"{value}")
    else:
        print("No images available")

    dbs = property_info.get('source_db', [])
    if isinstance(dbs, list) and dbs:
        dbs_display = ', '.join(dbs)
    elif isinstance(dbs, str):
        dbs_display = dbs  # If 'source_db' is a single string, handle it gracefully
    else:
        dbs_display = "No specific database information available"

    print(PURPLE + "Found in database(s): " + RESET + f"{dbs_display}")
    print(PURPLE + "Created By: " + RESET + f"{property_info.get('created_by', 'N/A')}")
    print(BLUE + "------\n" + RESET)


def update_property_interactive(username):
    """
    Handles the 'update' operation in an interactive manner.
    """
    def find_property_by_custom_id(custom_id):
        # Assuming all databases have the same structure and property is duplicated across them
        for db_name in DATABASE_NAMES:
            db = client[db_name]
            properties_collection = db['properties']
            property_data = properties_collection.find_one({"custom_id": custom_id})
            if property_data:
                return property_data
        return None

    def collect_property_updates():
        updates = {}
        print(BLUE + "Enter the updates for the property (hit enter to skip):" + RESET)
        new_price = input("New Price (leave blank if no change): ").strip()
        if new_price:
            updates['price'] = float(new_price)

        new_bedrooms = input("New Number of Bedrooms (leave blank if no change): ").strip()
        if new_bedrooms:
            updates['bedrooms'] = int(new_bedrooms)

        new_bathrooms = input("New Number of Bathrooms (leave blank if no change): ").strip()
        if new_bathrooms:
            updates['bathrooms'] = float(new_bathrooms)

        new_square_foot = input("New Square Footage (leave blank if no change): ").strip()
        if new_square_foot:
            updates['square_footage'] = float(new_square_foot)

        new_type = input("New Type (leave blank if no change): ").strip()
        if new_type:
            updates['type'] = new_type

        new_date = input("New Listing Date - YYYY-MM-DD (leave blank if no change): ").strip()
        if new_date:
            updates['date_listed'] = new_date

        new_description = input("New Description (leave blank if no change): ").strip()
        if new_description:
            updates['description'] = new_description

        return updates

    custom_id = input(BLUE + "Please enter the Custom ID of the property to update: " + RESET).strip()
    if not custom_id:
        print(YELLOW + "Custom ID is required to update a property.\n" + RESET)
        return

    property_data = find_property_by_custom_id(custom_id)
    if property_data and property_data.get('created_by') == username:
        updates = collect_property_updates()
        if updates:
            success = update_property(custom_id, updates, username)
            if success:
                print(GREEN + "Property updated successfully.\n" + RESET)
            else:
                print(RED + "Failed to update property.\n" + RESET)
        else:
            print(YELLOW + "No updates were made.\n" + RESET)
    else:
        print(RED + "You do not have permission to update this property or it does not exist.\n" + RESET)


def delete_property_interactive(username):
    """
    Handles the 'delete' operation in an interactive manner.
    """
    def find_property_by_custom_id(custom_id):
        # Assuming all databases have the same structure and property is duplicated across them
        for db_name in DATABASE_NAMES:
            db = client[db_name]
            properties_collection = db['properties']
            property_data = properties_collection.find_one({"custom_id": custom_id})
            if property_data:
                return property_data
        return None

    custom_id = input(BLUE + "Please enter the Custom ID of the property to delete: " + RESET).strip()
    if not custom_id:
        print(YELLOW + "Custom ID is required to delete a property.\n" + RESET)
        return

    property_data = find_property_by_custom_id(custom_id)
    if property_data and property_data.get('created_by') == username:
        # Confirm before deletion
        confirm = input(RED + "Are you sure you want to delete this property? (yes/no): " + RESET).strip().lower()
        if confirm == 'yes':
            success = delete_property(custom_id, username)
            if success:
                print(GREEN + "Property deleted successfully.\n" + RESET)
            else:
                print(RED + "Failed to delete property. It may no longer exist.\n" + RESET)
        else:
            print(YELLOW + "Deletion cancelled.\n" + RESET)
    else:
        print(RED + "You do not have permission to delete this property or it does not exist.\n" + RESET)


def main():
    parser = argparse.ArgumentParser(description="Property Management System")
    parser.add_argument('--username', help="Username for login or registration", default=os.getenv('MYAPP_USERNAME'))
    parser.add_argument('--password', help="Password for login or registration", default=os.getenv('MYAPP_PASSWORD'))
    parser.add_argument('--register', action='store_true', help="Register a new user")
    parser.add_argument('--operation', choices=['insert', 'search', 'update', 'delete', 'interactive_insert', 'interactive_search', 'interactive_update', 'interactive_delete'], help="Operation to perform")
    parser.add_argument('--city', help="City where the property is located", required=False)
    parser.add_argument('--state', help="State where the property is located", required=False)
    parser.add_argument('--type', help="Type of the property (e.g., 'sale', 'rent')", required=False)
    parser.add_argument('--address', help="Address of the property", required=False)
    parser.add_argument('--custom_id', help="Custom ID of the property", required=False)
    parser.add_argument('--updates', nargs='*', help="Updates to apply in the format: field1=value1 field2=value2", required=False)
    parser.add_argument('--zip_code', type=int, help="Zip code of the property", required=False)
    parser.add_argument('--price', type=float, help="Price of the property", required=False)
    parser.add_argument('--bedrooms', type=int, help="Number of bedrooms", required=False)
    parser.add_argument('--bathrooms', type=float, help="Number of bathrooms", required=False)
    parser.add_argument('--square_footage', type=int, help="Square footage of the property", required=False)
    parser.add_argument('--date_listed', help="Date when the property was listed", required=False)
    parser.add_argument('--description', help="Description of the property", required=False)
    parser.add_argument('--images', nargs='*', help="List of property images", required=False)
    parser.add_argument('--init', action='store_true', help="Initialize database indexes", required=False)
    parser.add_argument('--sort_by_price', choices=['asc', 'desc'], help="Sort search results by price in ascending or descending order", required=False)

    args = parser.parse_args()

    # Initialize username early
    username = args.username  # Ensure username is assigned even if registration or login fails

    # Authenticate or register user
    if args.register:
        if register_user(username, args.password):
            print(BLUE + "Registration successful. Please log in.\n" + RESET)
        else:
            return
    elif not authenticate_user(username, args.password):
        print(RED + "Login failed. Access denied.\n" + RESET)
        return

    # After successful login or registration, handle operations
    if args.init:
        initialize_indexes()
        print(GREEN + "Database indexes initialized successfully.\n" + RESET)

    # Handle different operations based on command line arguments
    if args.operation:
        if 'interactive' in args.operation:
            handle_interactive(args, username)
        else:
            handle_non_interactive(args, username)


def handle_interactive(args, username):
    if args.operation == 'interactive_insert':
        insert_property_interactive(username)
    elif args.operation == 'interactive_search':
        search_property_interactive(username)  # Assuming you'll implement username checks here as well
    elif args.operation == 'interactive_update':
        update_property_interactive(username)
    elif args.operation == 'interactive_delete':
        delete_property_interactive(username)


def handle_non_interactive(args, username):
    if args.operation == 'insert':
        property_data = collect_property_data(args)
        insert_property(property_data, username)  # Pass the username here
    elif args.operation == 'search':
        search_results = search_property(city=args.city, state=args.state, property_type=args.type,
                                         address=args.address, custom_id=args.custom_id, sort_by_price=args.sort_by_price)
        print_search_results(search_results)
    elif args.operation == 'update':
        if args.custom_id and args.updates:
            updates = parse_updates(args.updates)
            update_property(args.custom_id, updates, username)  # Pass the username here
    elif args.operation == 'delete':
        if args.custom_id:
            delete_property(args.custom_id, username)  # Pass the username here


def collect_property_data(args):
    return {
        "address": args.address,
        "city": args.city,
        "state": args.state,
        "zip_code": args.zip_code,
        "price": args.price,
        "bedrooms": args.bedrooms,
        "bathrooms": args.bathrooms,
        "square_footage": args.square_footage,
        "type": args.type,
        "date_listed": args.date_listed,
        "description": args.description,
        "images": args.images
    }


def print_search_results(search_results):
    if search_results:
        print(GREEN + f"Found {len(search_results)} properties:\n" + RESET)
        for property in search_results:
            print_property(property)
    else:
        print(YELLOW + "No properties found.\n" + RESET)


def parse_updates(updates):
    return {u.split('=')[0]: u.split('=')[1] for u in updates}


if __name__ == "__main__":
    main()
