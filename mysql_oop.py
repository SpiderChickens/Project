import mysql.connector
"""
This module provides an object-oriented interface to interact with a MySQL database for a school management system.
It includes classes for startup, database operations, and user roles (admin, teacher, student).
Classes:
    startup: Initializes the database connection, creates necessary tables, and inserts initial data.
    database: Inherits from startup and provides methods for user login and closing the database connection.
    student: Inherits from database and provides methods specific to student operations.
    teacher: Inherits from database and provides methods specific to teacher operations.
    admin: Inherits from database and provides methods for admin operations such as adding, updating, fetching, and deleting users.
Functions:
    __init__: Initializes the class instance and sets up the database connection.
    close: Closes the database connection.
    login: Handles user login and role-based access.
    add_user: Adds a new user to the database.
    update_user: Updates an existing user's information in the database.
    fetch_users: Fetches user information from the database.
    delete_user: Deletes a user from the database.
    menu: Displays the admin menu and handles user choices.
"""
import bcrypt
import os

class startup():
    def __init__(self):
        
        #clear_screen = lambda: os.system('cls')
        password = input("Enter the database password: ")          #Disabled for debugging purposes

        try:
            clear_screen()
            self.connection = mysql.connector.connect(
                host = "localhost",
                user = "root",
                password = password,
                auth_plugin = "mysql_native_password"

            )

        except:
            print("Connection to MySQL database failed. Maybe you entered the password incorrectly.")
            first_attempt = False
            self.__init__()
        else:
            self.connection.is_connected()


        self.cursor = self.connection.cursor(buffered=True) #buffered=True allows multiple queries to be executed at once and prevent cursor errors.

        #nuking the database for debugging purposes
        #if input("Do you want to nuke the database? (y/n): ") == 'y':
        #    self.cursor.execute("DROP DATABASE IF EXISTS school")
        #    self.connection.commit()
        #    print("Database nuked successfully")
        #else:
        #    pass

        self.cursor.execute("CREATE DATABASE IF NOT EXISTS school")
        self.cursor.execute("use school")
        self.cursor.execute("""create table if not exists users
            (uni_id INTEGER PRIMARY KEY AUTO_INCREMENT, 
            name VARCHAR(255),
            role ENUM('admin', 'teacher', 'student'),
            email VARCHAR(255),
            password VARCHAR(255) 
            )""")
        
        self.cursor.execute("""create table if not exists subjects
            (id INTEGER PRIMARY KEY AUTO_INCREMENT,
            subject VARCHAR(255) UNIQUE
            )""")
        
        # Inserting subjects into the subjects table
        self.cursor.execute("SELECT subject FROM subjects")
        subjects = self.cursor.fetchall()
        if not subjects:
            subjects = ["Mathematics", "Physics", "Chemistry", "Biology", "Computer Science", "History", "Geography"]
            for subject in subjects:
                self.cursor.execute("INSERT INTO subjects (subject) VALUES (%s)", (subject,))
                self.connection.commit()
            #print("Subjects inserted successfully")                             #Debugging print
        else:
            pass
            #print(subjects)                                                     #Debugging print
        
        self.cursor.execute("""create table if not exists teachers
            (id INTEGER PRIMARY KEY AUTO_INCREMENT,
            uni_id INTEGER,
            subject VARCHAR(255),
            FOREIGN KEY(uni_id) REFERENCES users(uni_id),
            FOREIGN KEY(subject) REFERENCES subjects(subject)
            )""")
        
        self.cursor.execute("""create table if not exists students
            (id INTEGER PRIMARY KEY AUTO_INCREMENT,
            uni_id INTEGER,
            subject VARCHAR(255),
            FOREIGN KEY(uni_id) REFERENCES users(uni_id),
            FOREIGN KEY(subject) REFERENCES subjects(subject)
            )""")  
         

        # Triggers to prevent duplicate IDs in teachers and students tables
        try:
            self.cursor.execute("""CREATE TRIGGER before_insert_teachers
                BEFORE INSERT ON teachers
                FOR EACH ROW
                BEGIN
                IF EXISTS (SELECT 1 FROM students WHERE uni_id = NEW.uni_id) THEN
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ID already exists in students table';
                END IF;
                END""")

            self.cursor.execute("""CREATE TRIGGER before_insert_students
                BEFORE INSERT ON students
                FOR EACH ROW
                BEGIN
                IF EXISTS (SELECT 1 FROM teachers WHERE uni_id = NEW.uni_id) THEN
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ID already exists in teachers table';
                END IF;
                END""")
        except:
            pass
        #classes TABLE , removed from students table for debugging purposes

        
        admin1_name = "admin"
        admin1_email = "josh"
        admin1_role = "admin"
        admin1_password = "beans"
        admin1_password = bcrypt.hashpw(admin1_password.encode(), bcrypt.gensalt()).decode()
        self.cursor.execute("SELECT * FROM users WHERE email = %s", (admin1_email,))
        if not self.cursor.fetchone():
            self.cursor.execute("INSERT INTO users (name, email, role, password) VALUES (%s, %s, %s, %s)", (admin1_name, admin1_email, admin1_role, admin1_password))
            self.connection.commit()
            #print("Admin account created successfully")                    Debugging print
        else:
            #print("Admin account already exists")                          Debugging print
            pass
        
        clear_screen()

        self.start_menu()

class database(startup):

    def password_change(self, email, higher_access):
        email_local = email
        #print(email_local)                                                                    #Debug print
        higher_access = higher_access
        #self.cursor.execute("SELECT role FROM users WHERE email = %s", (email_local))
        #role = self.cursor.fetchone()

        if higher_access == False:
            current_password = input("Please enter your current password:")
            clear_screen()
        else:
            current_password = ""
        new_password_1 = input("Please enter your new password:")
        clear_screen()
        new_password_2 = input("Please input your new password again:")

        self.cursor.execute("SELECT password FROM users WHERE email = %s", (email_local))
        stored_hashed_password = str(self.cursor.fetchone()).replace("(", "").replace(")", "").replace(",", "").replace("'", "")
        #print(stored_hashed_password)                                                         #Debug print

        if bcrypt.checkpw(current_password.encode(), stored_hashed_password.encode()) or higher_access == True:
            if new_password_1 == new_password_2:
                new_password_1 = bcrypt.hashpw(new_password_1.encode(), bcrypt.gensalt()).decode()
                self.cursor.execute("UPDATE users SET password = %s WHERE email = %s", (new_password_1, email_local[0]))
                self.connection.commit()
                print("Password updated")
                self.menu()
            else:
                print("Passwords do not match, please try again")
                self.menu()
        else:
            print("Invalid credentials, please try again")
            self.menu()
    
    def __init__(self):
        super().__init__()
    def close(self):
        self.connection.close()
        print("Connection closed")
        exit()

    def start_menu(self):
        choice = input(f"1. Login\n2. Close\n")
        if choice == "1":
            clear_screen()
            self.login()
        elif choice == "2":
            self.close()
        else:
            clear_screen()
            print("Invalid choice, please try again")
            self.start_menu()

    def login(self):
        email = input("Enter your email: ")
        password = input("Enter your password: ")

        # Fetch the stored hashed password and role
        query = "SELECT password, role FROM users WHERE email = %s"
        self.cursor.execute(query, (email,))
        result = self.cursor.fetchone()

        if result:
            stored_hashed_password, user_role = result

            # Check the password
            #print(type(stored_hashed_password))                                               #Debug print
            if bcrypt.checkpw(password.encode(), stored_hashed_password.encode()):
                print("Login successful!")

                # User role checks
                if user_role == "admin":
                    clear_screen()
                    admin(self.cursor, self.connection).menu()
                elif user_role == "student":
                    clear_screen()
                    print("Student logged in.")
                    student(self.cursor, self.connection, email).menu()
                elif user_role == "teacher":
                    clear_screen()
                    print("Teacher logged in.")
                    teacher(self.cursor, self.connection, email).menu()
                else:
                    print("Access role unknown: Contact your administrator")
            else:
                print("Invalid credentials.")
                self.start_menu()
        else:
            print("User not found.")
            self.start_menu()


class student(database):
    def __init__(self, cursor, connection, email):
        self.cursor = cursor
        self.connection = connection
        self.email = [email]
        self.cursor.execute("SELECT * FROM USERS WHERE email = %s", self.email)
        Student_Info = self.cursor.fetchall()
        #print(type(Student_Info))                                                                  Debug print
        #print(Student_Info)                                                                        Debug print
        id, name, role, email, hashedpassword = Student_Info[0]
        print(f"Your Student ID is: {id}\nYour name is: {name}\nYour email is: {email}")
        #for id, name, role, email, password in Student_Info[0]:                                    Alternate method
        #    print(f"Your Student ID is: {id}\nYour name is: {name}\nYour email is: {email}")
        id_list = [id]
        self.cursor.execute("SELECT Subject FROM students WHERE uni_id = %s", (id_list))
        Subject_Info = self.cursor.fetchall()
        cleaned_subjects = [str(subject).replace("(", "").replace(")", "").replace(",", "").replace("'", "") for subject in Subject_Info]
        print("You are studying:")
        for subject in cleaned_subjects:
            print(subject)
        self.menu()
        
    def menu(self):
        choice = input(f"1. Change password\n2. Logout\n")
        if choice == "1":
            higher_access = False
            self.password_change(self.email, higher_access)
        elif choice == "2":
            clear_screen()
            self.start_menu()
        else:
            print("Invalid choice")
            self.menu()
        

            


class teacher(database):
    def __init__(self, cursor, connection, email):
        self.cursor = cursor
        self.connection = connection
        self.email = [email]

    def list_students(self):
        #print(self.email)                                                                     #Debug print
        self.cursor.execute("SELECT uni_id FROM users WHERE email = %s", (self.email))
        teacher_id = self.cursor.fetchone()
        #print(teacher_id)                                                                      #Debug print
        self.cursor.execute("SELECT subject FROM teachers WHERE uni_id = %s", (teacher_id))
        subject = self.cursor.fetchone()
        #print(subject)                                                                         #Debug print    
        self.cursor.execute("SELECT uni_id FROM students WHERE subject = %s", (subject))
        students_id = self.cursor.fetchall()
        #print(students_id)                                                                     #Debug print
        self.cursor.execute("SELECT name FROM users WHERE uni_id = %s", (students_id[0]))
        students = self.cursor.fetchall()
        #print(students)                                                                        #Debug print
        print("You're teaching the following students:")
        for student in students:
            print(student)
        
    def menu(self):
        choice = input(f"1. List students\n2. Change Password\n3. Change student password\n4. Logout")
        if choice == "1":
            clear_screen()
            self.list_students()
        elif choice == "2":
            higher_access = False
            self.password_change(self.email, higher_access)
        elif choice == "3":
            student_email = [input("Enter the students email:")]
            higher_access = True
            self.password_change(student_email, higher_access)
        elif choice == "4":
            clear_screen()
            self.start_menu()
        else:
            clear_screen()
            print("Invalid input, pease try again")
            self.menu()




class admin(database):
    def __init__(self, cursor, connection):
        self.cursor = cursor
        self.connection = connection

    def add_user(self):
        # Inserting data into the database
        insert_query = "INSERT INTO users (name, role, password) VALUES (%s, %s, %s)"
        user_name = input("Enter your name and surname: ")
        #user_email = input("Enter your email: ")
        user_password = input("Enter your password: ")
        user_password = bcrypt.hashpw(user_password.encode(), bcrypt.gensalt()).decode()
        user_role = input("Enter your access role: ")
        data = (user_name, user_role, user_password)
        self.cursor.execute(insert_query, data)

        # Commit the changes
        self.connection.commit()
        print("Data inserted successfully into users table")
        if user_role == "teacher":
            data = self.cursor.execute("SELECT uni_id FROM users WHERE name = %s", (user_name,))
            uni_id = self.cursor.fetchone()[0]
            teacher_subject = input("Enter the subject you teach: ")
            self.cursor.execute("INSERT INTO teachers (uni_id, subject) VALUES (%s, %s)", (uni_id, teacher_subject))
            self.connection.commit()
            print("Teacher added successfully")

        elif user_role == "student":
            data = self.cursor.execute("SELECT uni_id FROM users WHERE name = %s", (user_name,))
            uni_id = self.cursor.fetchone()[0]
            data = self.cursor.execute("SELECT subject FROM subjects")
            subjects = self.cursor.fetchall()
            #print(subjects)                                                #Debugging print
            x = 0
            subjects_list = []
            #print(len(subjects))                                            #Debugging print
            for x in range(len(subjects)):
                subjects_list.append(subjects[x])
                #print(subjects_list)                                        #Debugging print
            choosing = True
            while choosing == True:
                x = 0
                print("Available subjects: ")
                for x in range(len(subjects_list)):
                    print(x+1,":",subjects_list[x])
                    x += 1
                student_subject_num = int(input("Enter the subjects you want to learn: "))-1
                student_subject = str(subjects_list[student_subject_num])
                student_subject = student_subject.replace("(", "").replace(")", "").replace(",", "").replace("'", "")
                #print(student_subject)                                      #Debugging print
                data = self.cursor.execute("insert into students (uni_id, subject) values (%s, %s)", (uni_id, student_subject))
                self.connection.commit()
                subjects_list.pop(student_subject_num)
                if len(subjects_list) == 0:
                    print("No more subjects available.")
                    choosing = False
                if input("Do you want to add more subjects? (y/n): ") == 'n':
                    choosing = False
                else:
                    print("Subject not available, please try again.")
            print("Student added successfully")
        
        user_name_tup = [user_name]
        #print(user_name_tup)
        self.cursor.execute("SELECT uni_id FROM users WHERE name = %s", (user_name_tup))
        user_id = self.cursor.fetchone()[0]
        #print(user_id)                                                                     #Debug print
        forename = str(user_name.split()[0])
        #print(forename)                                                                    #Debug print
        surname = str(user_name.split()[1])
        #print(surname)                                                                     #Debug print
        user_email = surname + forename[0] + str(user_id)
        #print(user_email)                                                                  #Debug print
        self.cursor.execute("UPDATE users SET email = %s WHERE name = %s", (user_email, user_name))
        self.connection.commit()
        clear_screen()
        print("Your email is:" ,user_email)
        

        self.menu()

    def update_user(self):
        # Updating data in the database
        update_query = "UPDATE users SET name = %s, email = %s, role = %s, password = %s WHERE uni_id = %s"
        user_id = input("Enter the id of the user you want to update: ")
        user_name = input("Enter your name: ")
        user_email = input("Enter your email: ")
        user_role = input("Enter your access role: ")
        user_password = input("Enter your password: ")
        user_password = bcrypt.hashpw(user_password.encode(), bcrypt.gensalt()).decode()
        data = (user_name, user_email, user_role, user_id, user_password)
        self.cursor.execute(update_query, data)

        # Commit the changes
        self.connection.commit()
        print("Data updated successfully")
        self.menu()

    def fetch_users(self):
        # Fetching data from the database
        user_selection = input("Enter the user's name to fetch: ")
        self.cursor.execute("SELECT * FROM users WHERE name = %s", (user_selection,))

        # Fetch all the rows
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)

    def delete_user(self):
        user_id = input("Enter the id of the user you want to delete: ")
        # Deleting data from the database
        delete_query = "DELETE FROM users WHERE uni_id = %s"
        self.cursor.execute(delete_query, (user_id,))
        delete_teacher_query = "DELETE FROM teachers WHERE uni_id = %s"
        self.cursor.execute(delete_teacher_query, (user_id,))
        delete_student_query = "DELETE FROM students WHERE uni_id = %s"
        self.cursor.execute(delete_student_query, (user_id,))
        self.cursor.execute(delete_query, (user_id,))
        # Commit the changes
        self.connection.commit()
        print("Data deleted successfully")
        self.menu()

    def menu(self):
        print("1. Add User\n2. Fetch Users\n3. Delete Users\n4. Update Users\n5. Logout")
        choice = input("Enter your choice: ")
        if choice == '1':
            self.add_user()
        elif choice == '2':
            self.fetch_users()
        elif choice == '3':
            self.delete_user()
        elif choice == '4':
            self.update_user()
        elif choice == '5':
            clear_screen()
            print("Logged out successfully.")
            self.start_menu()
        else:
            print("Invalid choice, please try again.")
            self.menu()




if __name__ == "__main__":
    clear_screen = lambda: os.system("cls")
    database()



#C0ventryCUC