
from hypernets_processor.version import __version__
import sys, sqlite3
import os

"""___Authorship___"""
__author__ = "Pieter De Vis"
__created__ = "29/3/2023"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "pieter.de.vis@npl.co.uk"
__status__ = "Development"

archive_path=r"C:\Users\pdv\OneDrive - National Physical Laboratory\Desktop\GONA_data\archive"

files_archive=["archive_GONA.db","archive_WWUK.db"]
files_anomaly=["anomaly_GONA.db","anomaly_WWUK.db"]
files_metadata=["metadata_GONA.db","metadata_WWUK.db"]

def merge(db_a, db_b, table_name):
    cursor_a = db_a.cursor()
    cursor_b = db_b.cursor()

    new_table_name = table_name + "_new"

    try:
        cursor_a.execute("CREATE TABLE IF NOT EXISTS " + new_table_name + " AS SELECT * FROM " + table_name)
        for row in cursor_b.execute("SELECT * FROM " + table_name):
            print(row)
            cursor_a.execute("INSERT INTO " + new_table_name + " VALUES" + str(row) + ";")

        cursor_a.execute("DROP TABLE IF EXISTS " + table_name);
        cursor_a.execute("ALTER TABLE " + new_table_name + " RENAME TO " + table_name);
        db_a.commit()

        print("\n\nMerge Successful!\n")

    except sqlite3.OperationalError:
        print("ERROR!: Merge Failed")
        cursor_a.execute("DROP TABLE IF EXISTS " + new_table_name);

def loadTables(db_a):
    cursor_a = db_a.cursor()
    cursor_a.execute("SELECT name FROM sqlite_master WHERE type='table';")

    table_counter = 0
    print("SQL Tables available: \n===================================================\n")
    table_names=[]
    for table_item in cursor_a.fetchall():
        current_table = table_item[0]
        table_counter += 1
        print("-> " + current_table)
        table_names.append(current_table)
    print("\n===================================================\n")

    return table_names

if __name__ == "__main__":
    db_a = sqlite3.connect(os.path.join(archive_path, files_archive[0]))
    table_names = loadTables(db_a)
    for file in files_archive[1::]:
        db_b = sqlite3.connect(os.path.join(archive_path, file))
        for table_name in table_names:
            merge(db_a, db_b, table_name)
        db_b.close()
    db_a.close()

    db_a = sqlite3.connect(os.path.join(archive_path,files_anomaly[0]))
    table_names = loadTables(db_a)
    for file in files_anomaly[1::]:
        db_b = sqlite3.connect(os.path.join(archive_path,file))
        for table_name in table_names:
            merge(db_a,db_b,table_name)
        db_b.close()
    db_a.close()

    db_a = sqlite3.connect(os.path.join(archive_path,files_metadata[0]))
    table_names = loadTables(db_a)
    for file in files_metadata[1::]:
        db_b = sqlite3.connect(os.path.join(archive_path,file))
        for table_name in table_names:
            merge(db_a,db_b,table_name)
        db_b.close()
    db_a.close()
