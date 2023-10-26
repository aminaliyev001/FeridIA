import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

def db_start(conn,cursor):
    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    email_parent TEXT NOT NULL,
    gender TEXT NOT NULL,
    mark INTEGER NOT NULL
    )
    """)

    cursor.execute (""" 
    CREATE TABLE IF NOT EXISTS templates (
    id INTEGER PRIMARY KEY,
    text TEXT NOT NULL,
    mark INTEGER NOT NULL
    )
    """)
    # cursor.execute("""
    # INSERT INTO templates (text,mark) VALUES (?,?)
    # """, ("some text1",1))
    # cursor.execute("""
    #     INSERT INTO templates (text,mark) VALUES (?,?)
    #     """, ("some text2", 2))
    # cursor.execute("""
    #     INSERT INTO templates (text,mark) VALUES (?,?)
    #     """, ("some text3", 3))
    # cursor.execute("""
    #     INSERT INTO templates (text,mark) VALUES (?,?)
    #     """, ("some text4", 4))
    # cursor.execute("""
    #     INSERT INTO templates (text,mark) VALUES (?,?)
    #     """, ("some text5", 5))
    # cursor.execute("""
    #     INSERT INTO templates (text,mark) VALUES (?,?)
    #     """, ("some text6", 6))
    # cursor.execute("""
    #     INSERT INTO templates (text,mark) VALUES (?,?)
    #     """, ("some text7", 7))
    # conn.commit()
    
def update_db():
    global students
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students")
    for student in students:
        cursor.execute("""
                INSERT INTO students (name, surname, email_parent, gender, mark)
                VALUES (?, ?, ?, ?, ?)
            """, (student["name"], student["surname"], student["email_parent"], student["gender"], student["mark"]))
    conn.commit()

    cursor.execute("DELETE FROM templates")
    for temp in templates:
        cursor.execute("""
                INSERT INTO templates (text, mark)
                VALUES (?, ?)
            """, (temp["text"], temp["mark"]))
    conn.commit()

    conn.close()
def load_db(conn,cursor):
    students = []
    try:
        cursor.execute("SELECT * FROM students")
        rows = cursor.fetchall()
        for row in rows:
            student = {
                "id": row[0],
                "name": row[1],
                "surname": row[2],
                "email_parent": row[3],
                "gender": row[4],
                "mark": row[5]
            }
            students.append(student)
    except sqlite3.Error as e:
        print("SQLite error:", e)
    except Exception as e:
        print("Error:", e)
    return students
def load_template(conn,cursor):
    templates = []
    try:
        cursor.execute("SELECT * FROM templates LIMIT 7 ")
        rows = cursor.fetchall()
        for row in rows:
            temp = {
                "id" : row[0],
                "text": row[1],
                "mark": row[2],
            }
            templates.append(temp)
    except sqlite3.Error as e:
        print("SQLite error:", e)
    except Exception as e:
        print("Error:", e)
    return templates

db_start(conn,cursor)
global students, templates
students = load_db(conn,cursor)
templates = load_template(conn,cursor)

def login():
    username = username_entry.get()
    password = password_entry.get()

    if username == "" and password == "":
        root.destroy()
        main_page()
    else:
        error_label.config(text="Invalid username or password")


def main_page():
    global students, treeview

    root = tk.Tk()
    root.title("Main Page")

    commenter_label = tk.Label(root, text="COMMENTER", font=("Arial", 16, "bold"))
    commenter_label.pack(pady=10)

    treeview = ttk.Treeview(root, columns=("name", "surname", "gender", "marks", "email"), show="headings")
    treeview.heading("name", text="Name")
    treeview.heading("surname", text="Surname")
    treeview.heading("gender", text="Gender")
    treeview.heading("marks", text="Marks (0-7)")
    treeview.heading("email", text="Parent Email")

    for student in students:
        treeview.insert("", "end", values=(
            student["name"],
            student["surname"],
            student["gender"],
            student["mark"],
            student["email_parent"]
        ))

    treeview.pack(pady=10)

    add_button = tk.Button(root, text="Add", command=add_student_page)
    delete_button = tk.Button(root, text="Delete", command=delete_student)
    edit_button = tk.Button(root, text="Edit", command=edit_selected)
    send_mail_button = tk.Button(root, text="Generate Comment", command=generate_comment)
    edit_template_button = tk.Button(root, text="Edit Template", command=edit_template)

    add_button.pack(side="left", padx=5)
    delete_button.pack(side="left", padx=5)
    edit_button.pack(side="left", padx=5)
    send_mail_button.pack(side="left", padx=5)
    edit_template_button.pack(side="left", padx=5)

    root.mainloop()


def edit_selected():
    selected_item = treeview.focus()
    if selected_item:
        selected_email = treeview.item(selected_item)["values"][4]
        edit_student_page(selected_email)
        update_db()

def edit_student_page(selected_email):
    def update_student():
        name = name_entry.get()
        surname = surname_entry.get()
        gender = gender_var.get()
        marks = marks_var.get()
        email = email_entry.get()

        for student in students:
            if student["email_parent"] == selected_email:
                student["name"] = name
                student["surname"] = surname
                student["gender"] = gender
                student["mark"] = marks
                student["email_parent"] = email
                break

        treeview.delete(*treeview.get_children())
        for student in students:
            treeview.insert("", "end", values=(
                student["name"],
                student["surname"],
                student["gender"],
                student["mark"],
                student["email_parent"]
            ))
        print(students)
        edit_window.destroy()

    edit_window = tk.Toplevel()
    edit_window.title("Edit Student")

    selected_student = next((student for student in students if student["email_parent"] == selected_email), None)

    name_label = tk.Label(edit_window, text="Name:")
    name_entry = tk.Entry(edit_window)
    name_entry.insert(0, selected_student["name"])

    surname_label = tk.Label(edit_window, text="Surname:")
    surname_entry = tk.Entry(edit_window)
    surname_entry.insert(0, selected_student["surname"])

    gender_label = tk.Label(edit_window, text="Gender:")
    gender_var = tk.StringVar()
    gender_male_radio = tk.Radiobutton(edit_window, text="Male", variable=gender_var, value="Male")
    gender_female_radio = tk.Radiobutton(edit_window, text="Female", variable=gender_var, value="Female")
    gender_var.set(selected_student["gender"])

    marks_label = tk.Label(edit_window, text="Marks (0-7):")
    marks_var = tk.StringVar()
    marks_dropdown = ttk.Combobox(edit_window, textvariable=marks_var, values=list(range(8)))
    marks_dropdown.set(selected_student["mark"])

    email_label = tk.Label(edit_window, text="Parent Email:")
    email_entry = tk.Entry(edit_window)
    email_entry.insert(0, selected_student["email_parent"])
    email_entry.config(state='disabled')

    update_button = tk.Button(edit_window, text="Update", command=update_student)

    name_label.grid(row=0, column=0, padx=5, pady=5)
    name_entry.grid(row=0, column=1, padx=5, pady=5)
    surname_label.grid(row=1, column=0, padx=5, pady=5)
    surname_entry.grid(row=1, column=1, padx=5, pady=5)
    gender_label.grid(row=2, column=0, padx=5, pady=5)
    gender_male_radio.grid(row=2, column=1, padx=5, pady=5)
    gender_female_radio.grid(row=2, column=2, padx=5, pady=5)
    marks_label.grid(row=3, column=0, padx=5, pady=5)
    marks_dropdown.grid(row=3, column=1, padx=5, pady=5)
    email_label.grid(row=4, column=0, padx=5, pady=5)
    email_entry.grid(row=4, column=1, padx=5, pady=5)
    update_button.grid(row=5, column=1, padx=5, pady=10)

    edit_window.mainloop()


def add_student_page():
    global students, treeview

    def save_student():
        name = name_entry.get()
        surname = surname_entry.get()
        gender = gender_var.get()
        marks = marks_var.get()
        email = email_entry.get()

        new_student = {
            "name": name,
            "surname": surname,
            "email_parent": email,
            "gender": gender,
            "mark": marks
        }

        students.append(new_student)
        update_db()
        treeview.insert("", "end", values=(name, surname, gender, marks, email))
        add_window.destroy()

    add_window = tk.Toplevel()
    add_window.title("Add Student")

    name_label = tk.Label(add_window, text="Name:")
    name_entry = tk.Entry(add_window)
    surname_label = tk.Label(add_window, text="Surname:")
    surname_entry = tk.Entry(add_window)

    gender_label = tk.Label(add_window, text="Gender:")
    gender_var = tk.StringVar()
    gender_male_radio = tk.Radiobutton(add_window, text="Male", variable=gender_var, value="Male")
    gender_female_radio = tk.Radiobutton(add_window, text="Female", variable=gender_var, value="Female")

    marks_label = tk.Label(add_window, text="Marks (0-7):")
    marks_var = tk.StringVar()
    marks_dropdown = ttk.Combobox(add_window, textvariable=marks_var, values=list(range(8)))

    email_label = tk.Label(add_window, text="Parent Email:")
    email_entry = tk.Entry(add_window)

    save_button = tk.Button(add_window, text="Save", command=save_student)

    name_label.grid(row=0, column=0, padx=5, pady=5)
    name_entry.grid(row=0, column=1, padx=5, pady=5)
    surname_label.grid(row=1, column=0, padx=5, pady=5)
    surname_entry.grid(row=1, column=1, padx=5, pady=5)
    gender_label.grid(row=2, column=0, padx=5, pady=5)
    gender_male_radio.grid(row=2, column=1, padx=5, pady=5)
    gender_female_radio.grid(row=2, column=2, padx=5, pady=5)
    marks_label.grid(row=3, column=0, padx=5, pady=5)
    marks_dropdown.grid(row=3, column=1, padx=5, pady=5)
    email_label.grid(row=4, column=0, padx=5, pady=5)
    email_entry.grid(row=4, column=1, padx=5, pady=5)
    save_button.grid(row=5, column=1, padx=5, pady=10)

    add_window.mainloop()


def delete_student():
    global students, treeview
    selected_item = treeview.focus()
    if selected_item:
        selected_email = treeview.item(selected_item)["values"][4]
        confirmation = messagebox.askyesno("Confirmation", "Are you sure you want to delete this student?")
        if confirmation:
            for student in students:
                if student["email_parent"] == selected_email:
                    students.remove(student)
                    break
            treeview.delete(selected_item)
            print(students)

    update_db()
root = tk.Tk()
root.title("Login")

username_label = tk.Label(root, text="Username:")
username_entry = tk.Entry(root)
password_label = tk.Label(root, text="Password:")
password_entry = tk.Entry(root, show="*")

login_button = tk.Button(root, text="Login", command=login)

error_label = tk.Label(root, fg="red")

username_label.grid(row=0, column=0)
username_entry.grid(row=0, column=1)
password_label.grid(row=1, column=0)
password_entry.grid(row=1, column=1)
login_button.grid(row=2, column=1)
error_label.grid(row=3, column=1)

import tkinter as tk

def edit_template():
    template_window = tk.Toplevel()
    template_window.title("Edit Template")
    template_window.geometry("245x385")
    template_entries = {}  
    count = 1
    for grade in templates:
        grade_label = tk.Label(template_window, text=str(grade["mark"]))
        grade_label.grid(row=count, column=0, padx=5, pady=5)

        grade_entry = tk.Entry(template_window)
        grade_entry.insert(0, grade["text"])
        grade_entry.grid(row=count, column=1, padx=5, pady=5)

        template_entries[grade["mark"]] = grade_entry
        count += 1
    def save_template():
        for grade_mark, entry in template_entries.items():
            for grade in templates:
                if grade["mark"] == grade_mark:
                    grade["text"] = entry.get()
        update_db()
        template_window.destroy()

    save_button = tk.Button(template_window, text="Save", command=save_template)
    save_button.grid(row=count, column=1, padx=5, pady=10)

    template_window.mainloop()
def replace_placeholders(message, student_name, gender):
    if gender == "male" or "Male":
        gender_pronoun = "he"
    elif gender == "female" or "Female":
        gender_pronoun = "she"

    message = message.replace("#name", student_name)
    message = message.replace("#he/she", gender_pronoun)
    return message

def sendEmail(to_email, subject, message,grade_):
    smtp_server = "smtp-mail.outlook.com" 
    smtp_port = 587 
    smtp_username = "feridiabcomputerscience@outlook.com" 
    smtp_password = "hrcftqhsdcdlvzvt"  
    try:
        for student in students:
            if student["email_parent"] == to_email:
                student["mark"] = grade_
                print("dsa")
        update_db()
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        server.sendmail(smtp_username, to_email, msg.as_string())
        server.quit()
        messagebox.showinfo("Success","Sent the email")
    except Exception as e:
        pass
def submit_button_click(grade):
    to_email = selected_email
    subject = "Grade Update"
    message = final_message_entry.get(1.0, tk.END)  
    sendEmail(to_email, subject, message,grade)
    
def generate_comment():
    global final_message_entry,selected_email,selected_grade
    selected_item = treeview.focus()
    def changeGrade(grade_):
        global selected_grade
        selected_grade = grade_
    if selected_item:
        selected_email = treeview.item(selected_item)["values"][4]
        selected_name = treeview.item(selected_item)["values"][0]
        selected_gender = treeview.item(selected_item)["values"][2]
        mail_window = tk.Toplevel()
        mail_window.title("Comment")
        def update_final_message(grade_text):
            final_message_entry.delete(1.0, tk.END)
            final_message_entry.insert(tk.END, grade_text)
        cursor.execute("SELECT mark, text FROM templates WHERE mark BETWEEN 1 AND 7")
        grade_data = cursor.fetchall()  
        for grade_info in grade_data:
            grade_mark, grade_text = grade_info
            grade_button = tk.Button(mail_window, text=str(grade_mark), command=lambda g=grade_text: (update_final_message(replace_placeholders(g,selected_name,selected_gender)),changeGrade(grade_mark)))
            grade_button.grid(row=grade_mark - 1, column=0, padx=5, pady=5)
        final_message = tk.Label(mail_window, text="Final message: ")
        final_message.grid(row=7, column=0, padx=5, pady=5)

        final_message_entry = tk.Text(mail_window, height=10, width=50, bg="white", fg="black")
        final_message_entry.grid(row=8, column=0, padx=5, pady=5)

        submit_button = tk.Button(mail_window, text="Submit",command=lambda:submit_button_click(selected_grade))
        submit_button.grid(row=9, column=0, padx=5, pady=10)

        mail_window.mainloop()

root.mainloop()