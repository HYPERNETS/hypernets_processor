import glob
import sqlite3
import os
import sys
import numpy as np
from hypernets_processor.version import __version__
import shutil

"""___Authorship___"""
__author__ = "Pieter De Vis"
__created__ = "29/3/2023"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "pieter.de.vis@npl.co.uk"
__status__ = "Development"

# set your archive path, and database names
archive_path = r"/archive/"
# archive_path = r"C:\Users\pdv\data\insitu\hypernets\archive"

archive_db = "archive.db"
anomaly_db = "anomaly.db"
metadata_db = "metadata.db"

# the following fields can be used to control the behavious of the script.
# If these arfe set to none, the user will be prompted for input through the command line.
# To avoid being prompted, set these to the appropriate values for what you want to remove 
# (see examples below)

bad_sequence_list = None # instead of using a SQL query, it is also possible to provide manually a list of Sequence_names
sql_query = None # Here provide using SQLite the conditions (i.e. the WHERE clause in SQL) for which you would like to remove sequences
list_info = False # If True, show list of all the products/anomalies that will be removed (this is slower). If False, only sequence_name and product_dir will be shown.

# Here are some example sql queries you can use to filter sequences (you can connecty these by AND/OR)
# --- Archive DB (products table) ---
# sql_query = "site_id = 'ATGE'"
# sql_query = "datetime_SEQ >= '2025-01-01'"
# sql_query = "datetime_start >= '2025-01-01' AND datetime_end <= '2025-11-01'"
# sql_query = "sequence_name LIKE 'SEQ2025%'"
# sql_query = "product_level = 'L2A'"
# sql_query = "solar_zenith_angle_max < 70.0"
# sql_query = "percent_zero_flags > 0.1"

# --- Anomaly DB (anomalies table) ---
# sql_query = "anomaly_id = 'x'"
# sql_query = "anomaly_id IN ('x', 'ms')"
# sql_query = "datetime >= '2025-01-01' AND datetime <= '2025-11-01'"
# sql_query = "site_id = 'ATGE'"
# sql_query = "sequence_name LIKE 'SEQ2025%'"
# sql_query = "product_level_last = 'L2A'"
# sql_query = "datetime >= '2025-01-01' AND datetime <= '2025-11-01'"

# Set your params here is you want to avoid specifying them through the command line.
db_choice = "anomaly"
# db_choice = "archive"

#bad_sequence_list = ["SEQ20251114T110045"]

sql_query = "site_id = 'L2B' and datetime_SEQ >= '2025-09-01'"

def get_products(db_path, sql_query):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    sequences = []
    for row in cursor.execute(f"SELECT sequence_name,rel_product_dir,product_name FROM products WHERE product_level='L_L2B' AND {sql_query}"):
        sequences.append(row)
    conn.close()
    sequences=np.array(sequences)
    if len(sequences)==0:
        return sequences
    unique_ids=np.unique(sequences[:,2],return_index=True)[1]
    sequences=sequences[unique_ids]
    return sequences

def get_amomalies_from_anomaly_db(db_path, sql_query):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    sequences = []
    for row in cursor.execute(f"SELECT sequence_name,rel_product_dir,anomaly_id FROM anomalies WHERE anomaly_id IN ('per','val','tod','hsn','scl','npr','man','wns','nos','hos') AND {sql_query.replace('datetime_SEQ','datetime')}"):
        sequences.append(row)
    conn.close()
    return sequences

def get_all_info(db_path, table_name, sequence_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    sequence_info = []
    if table_name=="anomalies":
        return_key = "anomaly_id"
    else:
        return_key = "product_name"
    for row in cursor.execute(f"SELECT {return_key} FROM {table_name} WHERE sequence_name=?", (sequence_id,)):
        sequence_info.append(row)
    conn.close()
    return sequence_info

def remove_from_anomaly_db(db_path, seq_name,sql_query):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM anomalies WHERE anomaly_id IN ('per','val','tod','hsn','scl','npr','man','wns','nos','hos') AND sequence_name='{seq_name}' AND {sql_query}")
    conn.commit()
    conn.close()

def remove_all_from_anomaly_db(db_path,sql_query):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM anomalies WHERE anomaly_id IN ('per','val','tod','hsn','scl','npr','man','wns','nos','hos') AND {sql_query}")
    conn.commit()
    conn.close()

def remove_all_from_metadata_db(db_path,sql_query):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM L_L2B WHERE {sql_query}")
    conn.commit()
    conn.close()

def remove_all_from_archive_db(db_path,sql_query):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM products WHERE product_level='L_L2B' AND {sql_query}")
    conn.commit()
    conn.close()

def remove_product_from_db(cursor, table_name, product_name, metadata=False):
    if metadata:
        try:
            cursor.execute(f"DELETE FROM {table_name} WHERE product_name=?", (product_name,))
        except:
            print(f"product_name not found in {table_name} in metadata.db")
    else:
        cursor.execute(f"DELETE FROM {table_name} WHERE product_name=?", (product_name,))
    

def load_table_names(db_a):
    cursor_a = db_a.cursor()
    cursor_a.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_names = [table_item[0] for table_item in cursor_a.fetchall()]
    return table_names

def delete_files(file_path):
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")
    else:
        print(f"File/Folder does not exist: {file_path}")

def main(archive_path=None, bad_sequence_list=None, sql_query=None):
    if archive_path is None:
        archive_path = input("Enter the archive path (where the .db files are located): ").strip()
    db_file = archive_db 
    db_path = os.path.join(archive_path, db_file)
    if bad_sequence_list is not None:
        sql_query = f"product_level = 'L_L2B' AND sequence_name IN {str(tuple(bad_sequence_list))}"
    elif sql_query is None:
        sql_query = input("Enter SQL WHERE clause to filter sequences (e.g., date < '2023-01-01'): ").strip()
    sequences = get_products(db_path, sql_query)
    print(f"Found {len(sequences)} products.")
    for idx, seq in enumerate(sequences):
        print(f"[{idx}] ID: {seq[0]}, product_path: {seq[1]}, product: {seq[2]}")

    to_remove = input("Enter comma-separated indices of sequences to remove (or `*' for all): ").strip()
    if to_remove == "*":
        indices = range(len(sequences))
    else:
        indices = [int(i) for i in to_remove.split(",") if i.isdigit()]
    
    for i in indices:
        seq = sequences[i]
        # remove file
        delete_files(os.path.join(archive_path,seq[1],seq[2]+".nc"))
        #remove plots
        glob_files = glob.glob(os.path.join(archive_path,seq[1],"plots/*L2B*.nc"))
        if len(glob_files)>0:
            for gf in glob_files:
                delete_files(gf)    
    
    #removem product from metadata db
    db_path = os.path.join(archive_path, metadata_db)
    
    if to_remove == "*" and "datetime" not in sql_query:
        remove_all_from_metadata_db(db_path, sql_query)
    else:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        for i in indices:
            seq = sequences[i]
            remove_product_from_db(cursor, "L_L2B", seq[2], metadata=True)
        conn.commit()
        conn.close()

    #removem product from archive db
    db_path = os.path.join(archive_path, archive_db)
    
    if to_remove == "*":
        remove_all_from_archive_db(db_path, sql_query)
    else:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        for i in indices:
            seq = sequences[i]
            remove_product_from_db(cursor, "products", seq[2], metadata=False)
        conn.commit()
        conn.close()
    print(f"L2B products have been removed from archive db and files deleted.")
    
    db_path = os.path.join(archive_path, anomaly_db)
    get_amomalies_from_anomaly_db(db_path,sql_query)

    print(f"Found {len(sequences)} anomalies.")
    for idx, seq in enumerate(sequences):
        print(f"[{idx}] ID: {seq[0]}, product_path: {seq[1]}, anomaly: {seq[2]}")
    to_remove = input("Enter comma-separated indices of sequences to remove (or `*' for all): ").strip()
    if to_remove == "*":
        indices = range(len(sequences))
    else:
        indices = [int(i) for i in to_remove.split(",") if i.isdigit()]
    
    for i in indices:
        seq = sequences[i]
        remove_from_anomaly_db(db_path, seq[0], sql_query)
                
    print(f"Sequences have been removed from anomaly db")

if __name__ == "__main__":
    main(archive_path, bad_sequence_list, sql_query)