import csv
import mysql.connector
import bcrypt

fake_people_connection = mysql.connector.connect(
                host = "localhost",
                user = "root",
                password = "C0ventryCUC",
                auth_plugin = "mysql_native_password"
            )

if fake_people_connection.is_connected():
    print("Connected Successfully")
else:
    print("Connection failed.")

fake_people_cursor = fake_people_connection.cursor(buffered = True)

fake_people_cursor.execute("use school")


with open("school_data.csv") as fileObject:

    heading = next(fileObject)
    reader_obj = csv.reader(fileObject)
    loops = 0
    for row in reader_obj:
        fname, sname, role, subjects, password = row
        #print(f"{fname} , {sname} , {role} , {subjects} , {password}")                 Debug print
        subject_list = subjects.split(", ")
        #print(type(fname), fname)
        #print(subject_list[0])

        password = bcrypt.hashpw("beans".encode(), bcrypt.gensalt()).decode()

        name = fname + " " + sname
        fake_people_cursor.execute("INSERT INTO users (name, role, password) values (%s, %s, %s)", (name, role, password))
        fake_people_connection.commit()
        fake_people_cursor.execute("SELECT uni_id FROM users WHERE (name, role, password) = (%s, %s, %s)", (name, role, password))
        uni_id = fake_people_cursor.fetchone()
        uni_id = str(uni_id).replace("(", "").replace(")", "").replace(",", "").replace("'", "")
        email = sname + fname[0] + uni_id
        fake_people_cursor.execute("UPDATE users SET email = %s WHERE (name, role, password) = (%s, %s, %s)", (email, name, role, password))
        fake_people_connection.commit()

        if role == "teacher":
            fake_people_cursor.execute("INSERT INTO teachers (uni_id, subject) VALUES (%s, %s)", (uni_id, str(subject_list[0])))
            fake_people_connection.commit()

        elif role == "student":
            for subject in subject_list:
                fake_people_cursor.execute("INSERT INTO students (uni_id, subject) VALUES (%s, %s)", (uni_id, subject))
        loops += 1
        print(f"{loops} rows inserted.")

fake_people_connection.close()

        
            

