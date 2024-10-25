import pyodbc
from datetime import datetime
import sqlite3

# Function to Connect to the database
def connect_db():
  """Connect to the SQL Server database and return the connection object."""
  try:
    connection = pyodbc.connect(
      'DRIVER={ODBC Driver 17 for SQL Server};'    # Trusted driver, compatible with various versions of SQL Server, 2017, 2019, and Azure SQL Database.
      'SERVER=OBIORA\INSTANCE_ONE_SQL;'            # SQL Server instance
      'DATABASE=FoodOrderDB;'                       # Name of the database
      'Trusted_Connection=yes;'                    # Use Windows authentication
    )
    return connection
  except pyodbc.Error as db_error:
    print(f"Error connecting to database: {db_error}")
    return None

def generate_unique_order_id(cursor):
  """Generate a unique alphanumeric OrderID."""
  prefix = 'A'  # Set a prefix for OrderID
  counter = 1  # Start counter

  while True:
    # Format OrderID
    order_id = f"{prefix}{counter:02d}"  # e.g., A01, A02
    cursor.execute("SELECT COUNT(*) FROM FoodOrderDB WHERE OrderID = ?", (order_id,))
    exists = cursor.fetchone()[0]

    if exists == 0:  # If this OrderID does not exist
      return order_id  # Return the unique OrderID
    counter += 1  # Increment the counter to generate a new OrderID

# Function: Add New Employee
def place_new_order():
  try:
    conn = connect_db()
    if conn is None:
      print("Failed to connect to the database.")
      return
    cursor = conn.cursor()
    
    # Generate a unique OrderID
    order_id = generate_unique_order_id(cursor)

    # Get employee details from user input, and remove extra spaces
    customerName = input("Enter Customer Name: ").strip()
    foodItem = input("Enter Food Item: ").strip()
    
    # Get quantity input and ensure it's a valid integer
    while True:
      try:
        qty = int(input("Enter Quantity: ").strip())
        if qty < 0:
          print("Quantity cannot be negative. Please try again.")
        else:
          break  # Exit loop if valid input is given
      except ValueError:
        print("Invalid input. Please enter a valid integer for the quantity.")

    # Get price input and ensure it's a valid float
    while True:
      try:
        price = float(input("Enter the Price: ").strip())
        if price < 0:
          print("Price cannot be negative. Please try again.")
        else:
          break  # Exit loop if valid input is given
      except ValueError:
        print("Invalid input. Please enter a valid number for the price.")

    # Get orderDate input and ensure it's valid  
    orderDate = input("Enter the Order Date (YYYY-MM-DD): ").strip()
    # Validate date
    try:
      orderDate = datetime.strptime(orderDate, "%Y-%m-%d").date()
    except ValueError:
      print("Invalid date format. Please enter the date as YYYY-MM-DD.")
      return

    # Insert the order record into the FoodOrderDB table
    cursor.execute(
      """INSERT INTO FoodOrderDB (OrderId, CustomerName, FoodItem, Quantity, Price, OrderDate) VALUES (?, ?, ?, ?, ?, ?)""", 
      (order_id, customerName, foodItem, qty, price, orderDate)
    )
    conn.commit()    # Save the changes to database
    print(f"Order Placed Successfully with OrderID: , {order_id}")
        
  except Exception as error_placing_order:
    print(f"Error: {error_placing_order}")
  finally:
    if conn:
      conn.close()

# Update an existing food order
def update_order():
  """Update a food order based on user input for OrderID."""
  
  try:                        # Try to connect to the database
    conn = connect_db()       # Create a connection to the database
    if conn is None:          # If the connection is not successful, stop here
      print("Failed to connect to the database.")
      return
    cursor = conn.cursor()    # Create a cursor object to execute SQL queries and retrieve results one row at a time
    
    # Fetch available OrderIDs only
    cursor.execute("SELECT OrderID FROM FoodOrderDB")
    order_id_to_update = [row[0] for row in cursor.fetchall()]  # Extract OrderIDs into a list
    
    if not order_id_to_update:
      print("No orders available to update.")
      return
    
    # Get and validate Order ID input
    while True:
      order_id = input("Enter OrderID to Update: ").strip().upper()
      
      if not order_id.isalnum():  # Check if it's alphanumeric (no special characters or empty input)
        print(
          f"\nInvalid OrderID Character'{order_id}." 
          f"Please enter a valid Order ID from the following available Order IDs{', '.join(order_id_to_update)}"
        )
        continue
      if order_id in order_id_to_update:
        print(f"OrderID: {order_id} found. Proceeding with update...")
        break  # Valid OrderID, proceed
      else:
        print(f"Food Order with the OrderID: {order_id} does not exist. Please choose from: {', '.join(order_id_to_update)}")

    def check_order_exists(cursor, order_id): # Check if the OrderID exists
      try:
        # Use parameterized query to avoid SQL injection
        cursor.execute("SELECT * FROM FoodOrderDB WHERE OrderID = ?", (order_id,))
        
        # Fetch one result to check existence
        result = cursor.fetchone()
        
        if result is None:
          print(f"Food Order with the OrderID: {order_id} does not exist.")
          return False  # Return False if the OrderID is not found
        else:
          print(f"OrderID: {order_id} found. Proceeding with update...")
          return True  # Return True if the OrderID exists
      except Exception as error:
        print(f"An error occurred while checking the OrderID: {error}")
        return False  # Handle database errors gracefully
    
    # Get new order details from user input, and remove extra spaces
    customerName = input("Enter new Customer Name (leave blank if you want to retain): ").strip()
    foodItem = input("Enter new Food Item (leave blank if you want to retain): ").strip()
    qty = input("Enter new Quantity (leave blank if you want to retain): ").strip()
    price = input("Enter new Price (leave blank if you want to retain): ").strip()
    orderDate = input("Enter new Order Date (YYYY-MM-DD), leave blank if you want to retain: ").strip()

    # Build the update query in a dynamic way based the on user's input
    update_order_fields = []
    update_order_values = []

    # Check and add valid inputs to the update query
    if customerName:
      update_order_fields.append("CustomerName = ?")
      update_order_values.append(customerName)

    if foodItem:
      update_order_fields.append("FoodItem = ?")
      update_order_values.append(foodItem)

    if qty:
      try:
        qty = int(qty)  # Ensure quantity is a valid integer
        update_order_fields.append("Quantity = ?")
        update_order_values.append(qty)
      except ValueError:
        print("Invalid quantity. Please enter a valid integer.")
        return

    if price:
      try:
        price = float(price)  # Ensure price is a valid float
        update_order_fields.append("Price = ?")
        update_order_values.append(price)
      except ValueError:
        print("Invalid price. Please enter a valid number.")
        return

    if orderDate:
      try:
        order_date = datetime.strptime(orderDate, "%Y-%m-%d").date()  # Validate date format
        update_order_fields.append("OrderDate = ?")
        update_order_values.append(orderDate)
      except ValueError:
        print("Invalid date format. Please enter the date as YYYY-MM-DD.")
        return
      
    if update_order_fields:
      # Add OrderID to the values list for the WHERE clause/condition
      update_order_values.append(order_id)
      # Create the UPDATE SQL query using the fields and values and saves the changes to database
      query = f"UPDATE FoodOrderDB SET {', '.join(update_order_fields)} WHERE OrderID = ?"
      
      # Confirm Order Update
      confirm = input(f"\nAre you sure you want to Update the order with OrderID: {order_id}? (yes/no): ").strip().lower()
      if confirm != 'yes':
        print("\nOrder Update Cancelled.")
        return
      
      try:
        # Execute the query and commit the changes
        cursor.execute(query, update_order_values)
        conn.commit()
        print("Order Updated successfully!")
      except Exception as error:
        print(f"An error occurred while updating the order: {error}")
    else:
      print("No Order Updates were made.")
      
  except Exception as error:      # gets any exceptions that may occur during the update process
    print(f"Error: {error}")
  finally:                        # Finally, close the database connection
    if conn:
      conn.close()

# Delete an Order by OrderID from table
def delete_order():
  """Delete a food order based on user input for OrderID."""
  try:
    # Connect to the database
    conn = connect_db()
    if conn is None:
      print("Failed to connect to the database.")
      return
    cursor = conn.cursor()
    
    # Fetch available OrderIDs only
    cursor.execute("SELECT OrderID FROM FoodOrderDB")
    available_order_ids = [row[0] for row in cursor.fetchall()]  # Extract OrderIDs into a list
    
    # Check if there are available orders
    if not available_order_ids:
      print("No orders available to delete.")
      return  # Exit if there are no orders to delete

    # Prompt user to choose an Order ID / Get and validate Order ID input
    while True:
      order_id = input("\nEnter OrderID to Delete / type 'exit' to cancel: ").strip().upper()
      
      if order_id.lower() == 'exit':  # Allow user to exit
        # The above code is a Python script that prints the message "Order deletion cancelled." to the console.
        print("\nOrder deletion cancelled.")
        return
      
      if not order_id.isalnum():  # Check if it's alphanumeric (no special characters or empty input)
        print(f"\nInvalid OrderID Character'{order_id}. Please enter a valid Order ID from the following available Order IDs")
        continue
      
      if not check_order_exists(cursor, order_id):
        print(f"\nPlease choose from the following available Order IDs: {', '.join(available_order_ids)}")
        continue  # Ask for input again
        
      # Confirm deletion
      confirm = input(f"\nAre you sure you want to delete the order with OrderID: {order_id}? (yes/no): ").strip().lower()
      if confirm != 'yes':
        print("\nOrder deletion cancelled.")
        return
        
      cursor.execute("DELETE FROM FoodOrderDB WHERE OrderID = ?", (order_id,))
      conn.commit()
      print(f"\nOrder with OrderID: {order_id} has been deleted successfully.")
      break  # Exit the loop after successful deletion
  except Exception as error:
    print(f"An error occurred: {error}")

  finally:
    # Ensure the database connection is closed
    if conn:
      conn.close()
      
def check_order_exists(cursor, order_id):
  """Check if the OrderID exists."""
  try:
    # Use parameterized query to avoid SQL injection
    cursor.execute("SELECT * FROM FoodOrderDB WHERE OrderID = ?", (order_id,))
    
    # Fetch one result to check existence
    result = cursor.fetchone()
    
    if result is None:
      print(f"\nFood Order with the OrderID: {order_id} does not exist.")
      return False  # Return False if the OrderID is not found
    else:
      print(f"\nOrderID: {order_id} found. Deleting the Order...")
      return True  # Return True if the OrderID exists
  except Exception as error:
    print(f"An error occurred while checking the OrderID: {error}")
    return False  # Handle database errors gracefully

def view_orders():
  """Fetch and display all food orders, returning available Order IDs."""
  try:
    # conn = sqlite3.connect('your_database.db')  # Connect to the database
    # conn.row_factory = sqlite3.Row  # Allows access by column name
    conn = connect_db()
    if conn is None:
      print("Failed to connect to the database.")
      return
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM FoodOrderDB")
    rows = cursor.fetchall()

    if rows:
      print(f"{'OrderID':<10} {'Customer Name':<20} {'Food Item':<15} {'Quantity':<10} {'Price':<10} {'Order Date':<15}")
      print("-" * 80)  # Print a separator line for better readability
      
      # order_ids = []  # List to hold order IDs for returning
      # Iterate through each order in the fetched rows and display each order in a table format
      for row in rows:
        order_date_fetch = row[5].strftime("%Y-%m-%d")  # Format date to YYYY-MM-DD
        print(
          f"{row[0]:<10} {row[1]:<20} {row[2]:<15} "
          f"{row[3]:<10} {row[4]:<10.2f} {order_date_fetch:<15}"
        )
      # order_ids.append(row[0])  # Add OrderID to the list
      # return order_ids  # Return the list of Order IDs
    else:
      print("No orders were found.")
      # return []  # Return an empty list if no orders are available

  except Exception as error:
    print(f"Error: {error}")
    # return []  # Return an empty list in case of error
  finally:
    if conn:
      conn.close()


# Display the main menu
def menu():
  """Display the main menu for the Food Order Management System."""
  while True:
    print("\nFood Order Management System")
    print("1. Place Food Order")
    print("2. Update Food Order")
    print("3. Delete Food Order")
    print("4. View Food Orders")
    print("5. Exit")

    choice = input("Select an option to execute: 1-5: ").strip()

    if choice == '1':
      print("You have chosen to place a food order.")
      place_new_order()   # Call the function to add a food order
    elif choice == '2':
      print("You have chosen to update a food order.")
      update_order()      # Call the function to update a food order
    elif choice == '3':
      print("You have chosen to delete a food order.")
      delete_order()      # Call the function to delete a food order
    elif choice == '4':
      print("You have chosen to view all food orders.")
      view_orders()       # Call the function to view all food orders
    elif choice == '5':
      print("Exiting program. Thank you for using the Food Order Management System.")
      break               # Exit the loop and terminate the program
    else:
      print(f"Invalid choice: ({choice}). Please select a valid option: 1-5.")  # Handle invalid input

# Start of the program execution; display the main menu to the user
if __name__ == "__main__":
  menu()

