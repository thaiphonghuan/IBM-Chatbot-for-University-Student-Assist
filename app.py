from flask import Flask, render_template, request, redirect, url_for
import ibm_db
import pandas as pd
import os

app = Flask(__name__)

# IBM DB2 connection setup
dsn_hostname = os.getenv('DB_HOST', 'copy your DB_HOST here')
dsn_uid = os.getenv('DB_UID', 'copy your DB_UID here')
dsn_pwd = os.getenv('DB_PWD', 'copy your DB_PWD here')
dsn_port = os.getenv('DB_PORT', 'copy your DB_PORT here')
dsn_database = "bludb"
dsn_driver = "{IBM DB2 ODBC DRIVER}"
dsn_protocol = "TCPIP"
dsn_security = "SSL"

dsn = (
    "DRIVER={0};"
    "DATABASE={1};"
    "HOSTNAME={2};"
    "PORT={3};"
    "PROTOCOL={4};"
    "UID={5};"
    "PWD={6};"
    "SECURITY={7};").format(dsn_driver, dsn_database, dsn_hostname, dsn_port, dsn_protocol, dsn_uid, dsn_pwd, dsn_security)

# Fetch students from DB2
def fetch_students():
    try:
        conn = ibm_db.connect(dsn, "", "")
        query = "SELECT * FROM DSSV" #Change your Table name 
        stmt = ibm_db.exec_immediate(conn, query)
        rows = []
        result = ibm_db.fetch_assoc(stmt)
        while result:
            rows.append(result)
            result = ibm_db.fetch_assoc(stmt)

        df = pd.DataFrame(rows)
        
        # Sort the DataFrame by "Mã Số"
        df = df.sort_values(by=["Mã Số"], ascending=True)  # Sắp xếp theo "Mã Số"
        
        return df
    except Exception as e:
        print("Error fetching students from DB2: ", str(e))
        return None
    finally:
        if 'conn' in locals():
            ibm_db.close(conn)


# Add a student to DB2
def add_student(name, birth_date, student_id, major):
    try:
        conn = ibm_db.connect(dsn, "", "")
        query = """
        INSERT INTO DSSV ("Tên Sinh Viên", "Ngày Sinh", "Mã Số", "Chuyên Ngành")
        VALUES (?, ?, ?, ?)
        """
        stmt = ibm_db.prepare(conn, query)
        ibm_db.bind_param(stmt, 1, name)
        ibm_db.bind_param(stmt, 2, birth_date)
        ibm_db.bind_param(stmt, 3, student_id)
        ibm_db.bind_param(stmt, 4, major)
        ibm_db.execute(stmt)
    except Exception as e:
        print("Error adding student to DB2: ", str(e))
    finally:
        if 'conn' in locals():
            ibm_db.close(conn)


# Delete a student from DB2
def delete_student(student_id):
    try:
        conn = ibm_db.connect(dsn, "", "")
        query = "DELETE FROM DSSV WHERE \"Mã Số\" = ?" #Change your Table name
        stmt = ibm_db.prepare(conn, query)
        ibm_db.bind_param(stmt, 1, student_id)
        ibm_db.execute(stmt)
    except Exception as e:
        print("Error deleting student from DB2: ", str(e))
    finally:
        if 'conn' in locals():
            ibm_db.close(conn)


# Main route to display student data and handle add/delete requests
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'add' in request.form:
            name = request.form['name']
            birth_date = request.form['birth_date']
            student_id = request.form['student_id']
            major = request.form['major']
            # Add student to DB2
            add_student(name, birth_date, student_id, major)
        elif 'delete' in request.form:
            student_id = request.form['student_id']
            # Delete student from DB2
            delete_student(student_id)
        # After updating DB2, redirect to refresh the page with updated student list
        return redirect(url_for('index'))

    # Fetch updated student list from DB2 and display
    students = fetch_students()
    return render_template('index.html', students=students)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
