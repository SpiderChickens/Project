import mysql.connector
import hashlib

# Connect to the MySQL Database, alligned to pep8 standards
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="C0ventryCUC",
    auth_plugin='mysql_native_password'
)

if connection.is_connected():
    print("Connected to MySQL Database")
else:
    print("Connection failed")

cursor = connection.cursor()

def add_user():
    # Inserting data into the database
    insert_query = "INSERT INTO employees.users (name, email, level) VALUES (%s, %s, %s)"
    user_name = input("Enter your name: ")
    user_email = input("Enter your email: ")
    user_password = input("Enter your password: ")
    access_level = input("Enter your access level: ")
    data = (user_name, user_email, access_level, user_password)
    cursor.execute(insert_query, data)

    # Commit the changes
    connection.commit()
    print("Data inserted successfully")
    main()

def update_user():
    # Updating data in the database
    update_query = "UPDATE employees.users SET name = %s, email = %s, level = %s WHERE id = %s"
    user_name = input("Enter your name: ")
    user_email = input("Enter your email: ")
    user_level = input("Enter your access level: ")
    user_id = input("Enter the id of the user you want to update: ")
    data = (user_name, user_email, user_level, user_id)
    cursor.execute(update_query, data)

    # Commit the changes
    connection.commit()
    print("Data updated successfully")
    main()    

def fetch_users():
    # Fetching data from the database
    user_selection = input("Enter the user's name to fetch: ")
    cursor.execute("SELECT * FROM employees.users WHERE name = %s", (user_selection,))

    # Fetch all the rows
    rows = cursor.fetchall()
    for row in rows:
        print(row)

def delete_user():
    # Deleting data from the database
    delete_query = "DELETE FROM employees.users WHERE id = %s"
    user_id = tuple(input("Enter the id of the user you want to delete: "))
    cursor.execute(delete_query, user_id)

    # Commit the changes
    connection.commit()
    print("Data deleted successfully")
    main()

def menu():
    print("1. Add User\n2. Fetch Users\n3. Delete Users\n4. Update Users\n5. Exit")
    choice = input("Enter your choice: ")
    if choice == '1':
        add_user()
    elif choice == '2':
        fetch_users()
    elif choice == '3':
        delete_user()
    elif choice == '4':
        update_user()
    else:
        cursor.close()
        connection.close()
        print("Connection closed, Goodbye")

        exit()

def login():
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT * FROM employees.users WHERE name = %s AND password = %s", (username, password))
    rows = cursor.fetchall()
    if rows:
        print("Login successful")
        menu()
    else:
        print("Login failed")
        login()

def signup():
    username = input("Input your username: ")
    password = input("Input your password: ")
    password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("INSERT INTO employees.users (name, password) VALUES (%s, %s)", (username, password))
    connection.commit()
    print("Signup successful")
    login()

def start_page():
    print("1. Login\n2. Signup")
    choice = input("Enter your choice: ")
    if choice == '1':
        login()
    else:
        signup()

def main():
    cursor.execute("CREATE DATABASE IF NOT EXISTS employees")
    cursor.execute("USE employees")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS users 
                   (id INT AUTO_INCREMENT PRIMARY KEY, 
                    name VARCHAR(255), 
                    email VARCHAR(255),
                    password VARCHAR(255), 
                    level VARCHAR(255))
                    """)
    start_page()

main()