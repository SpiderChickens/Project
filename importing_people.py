import csv
import mysql.connector
import bcrypt

connection = mysql.connector.connect(
                host = "localhost",
                user = "root",
                password = "C0ventryCUC",
                auth_plugin = "mysql_native_password"
            )

if connection.is_connected():
    print("Connected Successfully")
else:
    print("Connection failed.")

cursor = connection.cursor(buffered = True)

cursor.execute("use school")


with open("school_data.csv") as fileObject:

    heading = next(fileObject)
    reader_obj = csv.reader(fileObject)

    for row in reader_obj:
        fname, sname, role, subjects, password = row
        #print(f"{fname} , {sname} , {role} , {subjects} , {password}")                 Debug print
        subject_list = subjects.split(", ")
        #print(type(fname), fname)
        print(subject_list[0])

        password = bcrypt.hashpw("beans".encode(), bcrypt.gensalt()).decode()

        name = fname + " " + sname
        cursor.execute("INSERT INTO users (name, role, password) values (%s, %s, %s)", (name, role, password))
        connection.commit()
        cursor.execute("SELECT uni_id FROM users WHERE (name, role, password) = (%s, %s, %s)", (name, role, password))
        uni_id = cursor.fetchone()
        uni_id = str(uni_id).replace("(", "").replace(")", "").replace(",", "").replace("'", "")
        email = sname + fname[0] + uni_id
        cursor.execute("UPDATE users SET email = %s WHERE (name, role, password) = (%s, %s, %s)", (email, name, role, password))
        connection.commit()

        if role == "teacher":
            cursor.execute("INSERT INTO teachers (uni_id, subject) VALUES (%s, %s)", (uni_id, str(subject_list[0])))
            connection.commit()

        elif role == "student":
            for subject in subject_list:
                cursor.execute("INSERT INTO students (uni_id, subject) VALUES (%s, %s)", (uni_id, subject))
        
            

