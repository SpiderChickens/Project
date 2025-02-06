import mysql.connector
import bcrypt
import os

class startup():
    def __init__(self):
        
        self.clear_screen = lambda: os.system('cls')

        #password = input("Enter the database password: ")          #Disabled for debugging purposes

        self.connection = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "C0ventryCUC",
            auth_plugin = "mysql_native_password"

        )

        try: 
            self.connection.is_connected()
        except:
            print("Connection to MySQL database failed")
        else:
            print("Connected to MySQL database")

        self.cursor = self.connection.cursor(buffered=True) #buffered=True allows multiple queries to be executed at once.

        self.cursor.execute("CREATE DATABASE IF NOT EXISTS school")
        self.cursor.execute("use school")
        self.cursor.execute("""create table if not exists users
            (id INTEGER PRIMARY KEY AUTO_INCREMENT, 
            name VARCHAR(255),
            role ENUM('admin', 'teacher', 'student'),
            email VARCHAR(255),
            password VARCHAR(255) 
            )""")
        
        self.cursor.execute("""create table if not exists subjects
            (id INTEGER PRIMARY KEY AUTO_INCREMENT,
            subject VARCHAR(255) UNIQUE
            )""")
        
        self.cursor.execute("""create table if not exists teachers
            (id INTEGER PRIMARY KEY,
            teacher_id INTEGER,
            subject VARCHAR(255),
            FOREIGN KEY(teacher_id) REFERENCES users(id)
            )""")
        
        self.cursor.execute("""create table if not exists students
            (id INTEGER PRIMARY KEY,
            student_id INTEGER,
            lessons VARCHAR(255),
            FOREIGN KEY(student_id) REFERENCES users(id),
            FOREIGN KEY(lessons) REFERENCES subjects(subject)
            )""")  
         

        # Triggers to prevent duplicate IDs in teachers and students tables
        try:
            self.cursor.execute("""CREATE TRIGGER before_insert_teachers
                BEFORE INSERT ON teachers
                FOR EACH ROW
                BEGIN
                IF EXISTS (SELECT 1 FROM students WHERE id = NEW.id) THEN
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ID already exists in students table';
                END IF;
                END""")

            self.cursor.execute("""CREATE TRIGGER before_insert_students
                BEFORE INSERT ON students
                FOR EACH ROW
                BEGIN
                IF EXISTS (SELECT 1 FROM teachers WHERE id = NEW.id) THEN
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

        self.login()

class database(startup):
    
    def __init__(self):
        super().__init__()

    def close(self):
        self.connection.close()
        print("Connection closed")

    def login(self):
        email = input("Enter your email: ")
        password = input("Enter your password: ")

        # Fetch the stored hashed password and role
        query = "SELECT password, role FROM school.users WHERE email = %s"
        self.cursor.execute(query, (email,))
        result = self.cursor.fetchone()

        if result:
            stored_hashed_password, user_role = result

            # Check the password
            if bcrypt.checkpw(password.encode(), stored_hashed_password.encode()):
                print("Login successful!")

                # User role checks
                if user_role == "admin":
                    self.clear_screen()
                    admin(self.cursor, self.connection).menu()
                elif user_role == "student":
                    self.clear_screen()
                    print("Student logged in.")
                    # student(self.cursor, self.connection).menu()  # If student class exists
                elif user_role == "teacher":
                    self.clear_screen()
                    print("Teacher logged in.")
                    # teacher(self.cursor, self.connection).menu()  # If teacher class exists
                else:
                    print("Access role unknown: Contact your administrator")
            else:
                print("Invalid credentials.")
                self.login()
        else:
            print("User not found.")
            self.login()


class student(database):
    def __init__(self):
        super().__init__()

class teacher(database):
    def __init__(self):
        super().__init__()

class admin(database):
    def __init__(self, cursor, connection):
        self.cursor = cursor
        self.connection = connection

    def add_user(self):
        # Inserting data into the database
        insert_query = "INSERT INTO users (name, email, role, password) VALUES (%s, %s, %s, %s)"
        user_name = input("Enter your name: ")
        user_email = input("Enter your email: ")
        user_password = input("Enter your password: ")
        user_password = bcrypt.hashpw(user_password.encode(), bcrypt.gensalt()).decode()
        user_role = input("Enter your access role: ")
        data = (user_name, user_email, user_role, user_password)
        self.cursor.execute(insert_query, data)

        # Commit the changes
        self.connection.commit()
        print("Data inserted successfully into users table")
        if user_role == "teacher":
            data = self.cursor.execute("SELECT id FROM users WHERE email = %s", (user_email,))
            teacher_id = self.cursor.fetchone()[0]
            teacher_subject = input("Enter the subject you teach: ")
            self.cursor.execute("INSERT INTO teachers (id, subject) VALUES (%s, %s)", (teacher_id, teacher_subject))
            self.connection.commit()
            print("Teacher added successfully")

        elif user_role == "student":
            data = self.cursor.execute("SELECT id FROM users WHERE email = %s", (user_email,))
            student_id = self.cursor.fetchone()[0]
            data = self.cursor.execute("SELECT subject FROM subjects")
            subjects = self.cursor.fetchall()
            print(subjects)
            x = 0
            subjects_list = []
            for x in range(len(subjects)):
                subjects_list = subjects_list.append(subjects[x])
            choosing = True
            while choosing == True:
                x = 0
                print("Available subjects: ")
                for subject in subjects:
                    print(x, subjects_list[0])
                    x += 1
                student_subject = input("Enter the subjects you want to learn: ")
                student_subject = subjects[int(student_subject)]
                data = self.cursor.execute("insert into student (id, subject) values (%s, %s)", (student_id, student_subject))
                self.connection.commit()
                subjects.pop(int(student_subject))
                if len(subjects) == 0:
                    print("No more subjects available.")
                    choosing = False
                if input("Do you want to add more subjects? (y/n): ") == 'n':
                    choosing = False
                else:
                    print("Subject not available, please try again.")
            print("Student added successfully")
        

        self.menu()

    def update_user(self):
        # Updating data in the database
        update_query = "UPDATE users SET name = %s, email = %s, role = %s, password = %s WHERE id = %s"
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
        # Deleting data from the database
        delete_query = "DELETE FROM users WHERE id = %s"
        user_id = input("Enter the id of the user you want to delete: ")
        self.cursor.execute(delete_query, (user_id,))

        # Commit the changes
        self.connection.commit()
        print("Data deleted successfully")
        self.menu()

    def menu(self):
        print("1. Add User\n2. Fetch Users\n3. Delete Users\n4. Update Users\n5. Exit")
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
            print("Exiting...")
            self.connection.close()
            print("Connection closed")
            exit()
        else:
            print("Invalid choice, please try again.")
            self.menu()




if __name__ == "__main__":
    database()



#C0ventryCUC