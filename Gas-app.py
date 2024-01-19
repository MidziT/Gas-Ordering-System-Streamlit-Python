import streamlit as st
import pymysql
import pandas as pd
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
import numpy as np
import random
import string
import base64

# Connect to the database
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="P@55w0rd",
    db="gasorder"
)
c = conn.cursor()

# Define function to create Users table
def create_users_table():
    c.execute('''CREATE TABLE IF NOT EXISTS Users (
        id INT PRIMARY KEY AUTO_INCREMENT,
        username VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        userType ENUM('admin', 'customer') NOT NULL
    )''')

# Define function to create Results table
def create_results_table():
    c.execute('''CREATE TABLE IF NOT EXISTS Results (
        id INT PRIMARY KEY AUTO_INCREMENT,
        customerId INT NOT NULL,
        orderType VARCHAR(255) NOT NULL,
        orderDate DATE NOT NULL,
        FOREIGN KEY(customerId) REFERENCES Users(id)
    )''')

def create_tb_gas_order():
    c.execute('''CREATE TABLE tb_gas_order (
        order_code varchar(20),
        name VARCHAR(30) ,
        city VARCHAR(30), 
        phoneNumber int(10),
        amount float(10),
        price int(10),
        order_status VARCHAR(30)
    )''')

# Create the Users and Results tables if they don't exist
create_users_table()
create_results_table()
#create_tb_gas_order()

# Define function to add a new user to the Users table
def add_user(username, password, userType):
    try:
        c.execute('''INSERT INTO Users (username, password, userType) VALUES (%s, %s, %s)''', (username, password, userType,))
        conn.commit()
        st.success('Account created!')
    except Exception as e:
        conn.rollback()
        st.error(f"Error creating account: {e}")

# Define function to authenticate a user's login credentials
def authenticate(username, password):
    c.execute('''SELECT * FROM Users WHERE username = %s AND password = %s''', (username, password))
    return c.fetchone()

# Define function to add a new order to the Results table
def add_order(customerId, orderType, orderDate):
    try:
        c.execute('''INSERT INTO Results (customerId, orderType, orderDate) VALUES (%s, %s, %s)''', (customerId, orderType, orderDate,))
        conn.commit()
        st.success('Order placed successfully!')
    except Exception as e:
        conn.rollback()
        st.error(f"Error placing order: {e}")

# Define function to display the customer dashboard
def display_customer_dashboard(userId):
    st.title("Gas Agent System")
    st.title("Customers")
    st.sidebar.write(f'Welcome Customer {userId}!')
    
    # Connect to the database
    conn = pymysql.connect(host='localhost', user='root', password='P@55w0rd', db='gasorder')
    cursor = conn.cursor()

     # Create operation
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name")
        city = st.text_input("City")
        
    with col2:
        
        phone_number = st.text_input("Phone Number")
        amount = st.number_input("Amount", min_value=0)

    if amount:
        price = amount * 2
        st.number_input("Price", value=price)

    def generate_order_code():
        # Generate a random order code using uppercase letters and digits
        letters_and_digits = string.ascii_uppercase + string.digits
        order_code = ''.join(random.choices(letters_and_digits, k=10))
        return order_code
    

    if st.button("Order Gas"):

        order_code = generate_order_code()
        #st.success(f"Order code: {order_code}")
        order_status = "Pending"

        insert_query = "INSERT INTO tb_gas_order (order_code, name, city, phoneNumber, amount, price, order_status) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (order_code, name, city, phone_number, amount, price, order_status))
        conn.commit()
        
        # Reload the page to show updated data
        st.experimental_set_query_params(delete=True)
        st.experimental_rerun()

    # Update operation
    st.write("# Cancel Order")
    name = st.text_input("Enter the name of the record you want to cancel the order")

    if st.button("Request Cancel"):
        update_query = "UPDATE tb_gas_order SET order_status = 'Waiting to cancel' WHERE name = %s"
        cursor.execute(update_query, (name,))
        conn.commit()

        # Reload the page to show updated data
        st.experimental_set_query_params(update=True)
        st.experimental_rerun()
        st.success("Record deleted from the database!")   

    # Read operation
    st.write("### Clients ordering gas")
    select_query = "SELECT * FROM tb_gas_order"
    cursor.execute(select_query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['Order', 'Name', 'City', 'Phone Number', 'Amount Kg', 'Price $', 'Order_status'])

    #df = pd.DataFrame(
       # np.random.randn(50, 20),
       # columns=('col %d' % i for i in range(20)))

    # Build grid options
    gb = GridOptionsBuilder.from_dataframe(df)

    # Set the column width for specific columns
    gb.configure_column("Order", maxWidth=110)
    gb.configure_column("Name", maxWidth=90)
    gb.configure_column("City", maxWidth=100)
    gb.configure_column("Phone Number", maxWidth=100)
    gb.configure_column("Amount Kg", maxWidth=100)
    gb.configure_column("Price $", maxWidth=100)
    gb.configure_column("Order_status", maxWidth=130)


    # Add pagination
    gb.configure_pagination(paginationAutoPageSize=True)

   # Add vertical scrollbar
    gb.configure_side_bar()

    grid_options = gb.build()

     # Display the dataframe using st_aggrid
    AgGrid(df, gridOptions=grid_options)
    # Close the cursor and connection
    cursor.close()
    conn.close()



    if st.sidebar.button('Logout'):
        state.logged_in = False
        st.experimental_rerun()

# Define function to display the admin dashboard
def display_admin_dashboard():

    # Connect to the database
    conn = pymysql.connect(host='localhost', user='root', password='P@55w0rd', db='gasorder')
    cursor = conn.cursor()
    
    st.title("Gas Agent System")
    st.sidebar.write('Welcome To the Admin Dashboard!')

    # Define the maximum height for the table
    #table_height = 5

    # Execute a SELECT query
    select_query = "SELECT * FROM tb_gas_order"
    cursor.execute(select_query)

    # Fetch the data from the database
    data = cursor.fetchall()

    # Create a pandas dataframe
    df = pd.DataFrame(data, columns=['Order', 'Name', 'City', 'Phone Number', 'Amount Kg', 'Price $', 'Order_status'])

    # Build grid options
    gb = GridOptionsBuilder.from_dataframe(df)

    # Set the column width for specific columns
    gb.configure_column("Order", maxWidth=110)
    gb.configure_column("Name", maxWidth=90)
    gb.configure_column("City", maxWidth=100)
    gb.configure_column("Phone Number", maxWidth=100)
    gb.configure_column("Amount Kg", maxWidth=100)
    gb.configure_column("Price $", maxWidth=100)
    gb.configure_column("Order_status", maxWidth=130)

    # Add pagination
    gb.configure_pagination(paginationAutoPageSize=True)

    grid_options = gb.build()

    # Display the dataframe using st_aggrid
    AgGrid(df, gridOptions=grid_options)

    # Delete operation
    left_col, right_col = st.columns(2)

    with left_col:
        st.write("# Delete")
        name = st.text_input("Enter the name of the record you want to delete")
        if st.button("Delete Record"):
            delete_query = "DELETE FROM tb_gas_order WHERE name = %s"
            cursor.execute(delete_query, (name,))
            conn.commit()

            # Reload the page to show updated data
            st.experimental_set_query_params(delete=True)
            st.experimental_rerun()

            st.success("Record deleted from the database!")

    # Update operation
    with right_col:
        st.write("# Process Order")
        name = st.text_input("Enter the name of the record you want to process the order")

        if st.button("Process Order"):
            update_query = "UPDATE tb_gas_order SET order_status = 'Success' WHERE name = %s"
            cursor.execute(update_query, (name,))
            conn.commit()

            # Reload the page to show updated data
            st.experimental_set_query_params(update=True)
            st.experimental_rerun()

            st.success("Record updated in the database!")

    # Update operation
    st.write("# Cancel Order")
    name = st.text_input("Enter the name of the record you want to cancel the order")

    if st.button("Request Cancel"):

        update_query = "UPDATE tb_gas_order SET order_status = 'Cancelled' WHERE name = %s"
        cursor.execute(update_query, (name,))
        conn.commit()

        # Reload the page to show updated data
        st.experimental_set_query_params(update=True)
        st.experimental_rerun()
        st.success("Record deleted from the database!")          
    

    # Close the cursor and connection
    cursor.close()
    conn.close()


    if st.sidebar.button('Logout'):
        state.logged_in = False
        st.experimental_rerun()

# Define session state
state = st.session_state
if 'logged_in' not in state:
    state.logged_in = False

# Display login form if not logged in
if not state.logged_in:
    st.title('Login')
    username = st.text_input('Username:')
    password = st.text_input('Password:', type='password')
    if st.button('Login'):
        user = authenticate(username, password)
        if user:
            st.success('Logged in successfully!')
            state.logged_in = True
            state.user_id = user[0]
            state.user_type = user[3]
            st.experimental_rerun()
        else:
            st.warning('Invalid credentials.')
    expander = st.expander('Create an Account')
    with expander:
        new_username = st.text_input('New Username:')
        new_password = st.text_input('New Password:', type='password')
        user_type_input = st.selectbox('User Type:', ('Admin', 'Customer'))
        if st.button('Create Account'):
            userType = 'admin' if user_type_input == 'Admin' else 'customer'
            add_user(new_username, new_password, userType)

# Displaydashboard if logged in
else:
    if state.user_type == 'customer':
        display_customer_dashboard(state.user_id)
        
    elif state.user_type == 'admin':
        display_admin_dashboard()
        

# Close the database connection
conn.close()




    
    

