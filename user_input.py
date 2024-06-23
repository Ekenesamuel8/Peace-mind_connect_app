import mysql.connector
import uuid

class User_input:
    """self.cursor:a instance that will contain the
       communicator of the database.
       self.mydb: the credential of the database"""
    
    def __init__(self):
        self.cursor = None
        self.mydb = None


    def connect(self):
        """Establishes the connection to the MySQL database."""

        self.mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1258",
            database="ekenetest"
        )

        self.cursor = self.mydb.cursor()

        
    def create_table_struc(self):
        """Creates the table structure if it does not already exist."""  

        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS members(
                            id INT PRIMARY KEY AUTO_INCREMENT,
                            unique_id VARCHAR(100),                              
                            name VARCHAR(255),
                            age INT,
                            gender VARCHAR(100)
                            );
                            """)


    def collect_input(self):
        """Collects user input and generates a unique ID."""

        name = input("what is the name: ")
        age = int(input("waht is your age: "))
        gender = input("are you a male or female: ")
        unique_id = str(uuid.uuid4())

        return name, age, gender, unique_id
    

    def insert_to_table(self, name, age, gender, unique_id):
        """Inserts collected data into the database table."""

        sql_format = "INSERT INTO members (unique_id, name, age, gender) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(sql_format, (unique_id, name, age, gender))
        self.mydb.commit()


if __name__ == "__main__":

    call = User_input()
    call.connect()
    call.create_table_struc()
    user_details = call.collect_input()
    call.insert_to_table(*user_details)

    if call.mydb.is_connected():
        call.cursor.close()
        call.mydb.close()
        print("MySQL connection is closed")

