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
#archive_path = r"C:\Users\pdv\data\insitu\hypernets\archive"
archive_db = "archive.db"
anomaly_db = "anomaly.db"
metadata_db = "metadata.db"

# the following fields can be used to control the behavious of the script.
# If these arfe set to none, the user will be prompted for input through the command line.
# To avoid being prompted, set these to the appropriate values for what you want to remove 
# (see examples below)

db_choice = None  # which db should be queried to identify sequences that should be removed (the selected sequences wil be removed from all three db)
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

# bad_sequence_list = ["SEQ20231026T080128", "SEQ20231031T073028"]

sql_query = "site_id = 'GHNA' and datetime_SEQ >= '2025-09-01' and datetime_SEQ < '2025-10-15'"



def get_sequences(db_path, table_name, sql_query):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    sequences = []
    for row in cursor.execute(f"SELECT sequence_name,rel_product_dir FROM {table_name} WHERE {sql_query}"):
        sequences.append(row)
    conn.close()
    sequences=np.array(sequences)
    if len(sequences)==0:
        return sequences
    unique_ids=np.unique(sequences[:,0],return_index=True)[1]
    sequences=sequences[unique_ids]
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

def remove_sequence_from_db(db_path, table_name, sequence_id, metadata=False):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if metadata:
        try:
            cursor.execute(f"DELETE FROM {table_name} WHERE sequence_id=?", (sequence_id,))
        except:
            print(f"sequence_id not found in {table_name} in metadata.db")
    else:
        cursor.execute(f"DELETE FROM {table_name} WHERE sequence_name=?", (sequence_id,))
    conn.commit()
    conn.close()

def load_table_names(db_a):
    cursor_a = db_a.cursor()
    cursor_a.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_names = [table_item[0] for table_item in cursor_a.fetchall()]
    return table_names

def delete_files(file_path):
    if os.path.exists(file_path):
        try:
            shutil.rmtree(file_path)
            print(f"Deleted folder: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")
    else:
        print(f"File/Folder does not exist: {file_path}")

def main(archive_path=None, db_choice=None, bad_sequence_list=None, sql_query=None):
    if archive_path is None:
        archive_path = input("Enter the archive path (where the .db files are located): ").strip()
    if db_choice is None:
        db_choice = input("Select database (archive/anomaly): ").strip().lower()
    db_file = archive_db if db_choice == "archive" else anomaly_db
    db_path = os.path.join(archive_path, db_file)
    conn = sqlite3.connect(db_path)
    table_names = load_table_names(conn)
    conn.close()
    if bad_sequence_list is not None:
        sql_query = f"sequence_name IN {str(tuple(bad_sequence_list))}"
    elif sql_query is None:
        sql_query = input("Enter SQL WHERE clause to filter sequences (e.g., date < '2023-01-01'): ").strip()
    sequences = get_sequences(db_path, table_names[0], sql_query)
    print(f"Found {len(sequences)} sequences.")
    for idx, seq in enumerate(sequences):
        if list_info:
            print(f"[{idx}] ID: {seq[0]}, product_path: {seq[1]}, ids: {get_all_info(db_path, table_names[0], seq[0])}")
        else:
            print(f"[{idx}] ID: {seq[0]}, product_path: {seq[1]}")

    to_remove = input("Enter comma-separated indices of sequences to remove (or `*' for all): ").strip()
    if to_remove == "*":
        indices = range(len(sequences))
    else:
        indices = [int(i) for i in to_remove.split(",") if i.isdigit()]
    
    for i in indices:
        seq = sequences[i]
        delete_files(os.path.join(archive_path,seq[1]))
    for db in [metadata_db,anomaly_db,archive_db]:
        db_path = os.path.join(archive_path, db)
        conn = sqlite3.connect(db_path)
        table_names = load_table_names(conn)
        conn.close()
        for table_name in table_names:
            for i in indices:
                seq = sequences[i]
                remove_sequence_from_db(db_path, table_name, seq[0], metadata=(db==metadata_db))
                print(f"Sequence {seq[0]} removed from {table_name} in {db}.")

    print(f"Sequences have been removed from all the db and files deleted.")

if __name__ == "__main__":
    main(archive_path, db_choice, bad_sequence_list, sql_query)