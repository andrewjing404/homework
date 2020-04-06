import mysql.connector
import pandas

# Takes the query, submit to MySQL database, and print result.

query = """input query here"""

def query(host = "127.0.0.1", port = 3306, user = "root", password = ""):
    try:
        connection.close()
    except:
        pass
    connection = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password)
    cursor = connection.cursor()
    cursor.execute(query)
    columns = cursor.column_names
    result = cursor.fetchall()
    result = pd.DataFrame(result, columns=columns)
    pd.set_option("display.expand_frame_repr", False)
    print(result)
    connection.close()