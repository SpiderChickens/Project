import csv
import faker
import random
import secrets

# Subject list provided
subjects = ["Mathematics", "Physics", "Chemistry", "Biology", "Computer Science", "History", "Geography", "English", "French", "Engineering"]

# Number of teachers (one per subject)
num_teachers = len(subjects)
# Number of students per class (for each subject)
students_per_class = 30
# Total number of students to create in the pool (we'll reuse students in different classes)
num_student_pool = 150  #  Slightly more than unique needed to allow for variations in subject choices

fake = faker.Faker()

def generate_password():
    """Generates a slightly more secure password."""
    return secrets.token_urlsafe(16) # 16 bytes of random data, URL-safe encoded

def generate_teachers(subject_list):
    """Generates teacher data."""
    teachers_data = []
    for subject in subject_list:
        teacher_first_name = fake.first_name()
        teacher_last_name = fake.last_name()
        teachers_data.append({
            "First Name": teacher_first_name,
            "Last Name": teacher_last_name,
            "Role": "teacher",
            "Subject(s)": subject,
            "Password": generate_password()
        })
    return teachers_data

def generate_student_pool(num_students):
    """Generates a pool of student data."""
    student_pool_data = []
    for _ in range(num_students):
        student_first_name = fake.first_name()
        student_last_name = fake.last_name()
        student_pool_data.append({
            "First Name": student_first_name,
            "Last Name": student_last_name,
            "Role": "student", # Role will be set when assigning to class if needed, but default to student in pool
            "Subject(s)": [], # Subjects taken will be assigned later
            "Password": generate_password()
        })
    return student_pool_data

def assign_student_subjects(student_pool, subject_list):
    """Assigns 1 to 3 subjects to each student in the pool."""
    for student in student_pool:
        num_subjects_to_take = random.randint(1, 3) # Students can take 1 to 3 subjects
        subjects_taken = random.sample(subject_list, num_subjects_to_take) # Randomly pick subjects
        student["Subject(s)"] = ", ".join(subjects_taken) # Store subjects as comma-separated string

def generate_class_enrollment(student_pool, subject, students_per_class):
    """Generates enrollment for a single class (subject)."""
    enrolled_students = random.sample(student_pool, students_per_class) # Randomly select students from the pool
    class_data = []
    for student in enrolled_students:
        student_data_for_class = student.copy() # Create a copy so we don't modify the pool directly in this function
        student_data_for_class["Role"] = "student" # Ensure role is student for class context (already student in pool)
        # Subject(s) are already assigned to students, no need to add subject here for class context
        class_data.append(student_data_for_class)
    return class_data

def create_csv_file(filename="school_data.csv"):
    """Generates all data and writes it to a CSV file."""
    teachers_data = generate_teachers(subjects)
    student_pool = generate_student_pool(num_student_pool)
    assign_student_subjects(student_pool, subjects) # Assign subjects to students in the pool

    all_data = []
    all_data.extend(teachers_data) # Add teachers first

    for subject in subjects:
        class_enrollment_data = generate_class_enrollment(student_pool, subject, students_per_class)
        all_data.extend(class_enrollment_data) # Add students enrolled in each class

    # Remove the temporary "Role" assignment from student pool for clean output if needed (optional as Role is student in pool already)
    # for student in student_pool:
    #     if "Role" in student:
    #         del student["Role"] # Keep if you want to show only student role in class, remove to show role from pool def

    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ["First Name", "Last Name", "Role", "Subject(s)", "Password"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(all_data)

    print(f"CSV file '{filename}' created successfully.")

if __name__ == "__main__":
    create_csv_file()