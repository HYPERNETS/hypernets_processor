
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

files_archive=["archive_WWUK.db","archive_DEGE.db"]
files_anomaly=["anomaly_WWUK.db","anomaly_DEGE.db"]
files_metadata=["metadata_WWUK.db","metadata_DEGE.db"]

out_archive="archive.db"
out_anomaly="anomaly.db"
out_metadata="metadata.db"


def merge(outfile, file, table_name):
    db_out = sqlite3.connect(os.path.join(archive_path, outfile))
    cursor_a = db_out.cursor()
    db_b = sqlite3.connect(os.path.join(archive_path, file))
    cursor_b = db_b.cursor()

    new_table_name = table_name + "_new"

    table_names_out=load_table_names(db_out)
    if True:
        if len(table_names_out)==0:
            cursor_a.execute("ATTACH DATABASE '%s' AS table_new"%(os.path.join(archive_path, file)))
            cursor_a.execute(
                "CREATE TABLE IF NOT EXISTS " + new_table_name + " AS SELECT * FROM table_new." + table_name)

        else:
            cursor_a.execute("CREATE TABLE IF NOT EXISTS " + new_table_name + " AS SELECT * FROM " + table_name)
            index_prev=list(cursor_a.execute("SELECT id FROM " + table_name))[-1]
            print(index_prev)
            for i,row in enumerate(cursor_b.execute("SELECT * FROM " + table_name)):
                row=["none" if v is None else v for v in row]
                row[0]+=int(index_prev[0])
                row=tuple(row)
                cursor_a.execute("INSERT INTO " + new_table_name + " VALUES " + str(row))
            cursor_a.execute("DROP TABLE IF EXISTS " + table_name)
        cursor_a.execute("ALTER TABLE " + new_table_name + " RENAME TO " + table_name)
        db_out.commit()

        print("\n\nMerge Successful!\n")
    db_b.close()
    db_out.close()

def load_table_names(db_a):
    cursor_a = db_a.cursor()
    cursor_a.execute("SELECT name FROM sqlite_master WHERE type='table';")

    table_counter = 0
    table_names=[]
    for table_item in cursor_a.fetchall():
        current_table = table_item[0]
        table_counter += 1
        # print("-> " + current_table)
        table_names.append(current_table)

    return table_names

if __name__ == "__main__":
    db_a = sqlite3.connect(os.path.join(archive_path, files_archive[0]))
    table_names = load_table_names(db_a)
    db_a.close()
    for file in enumerate(files_archive):
        for table_name in table_names:
            merge(out_archive, file, table_name)

    db_a = sqlite3.connect(os.path.join(archive_path, files_anomaly[0]))
    table_names = load_table_names(db_a)
    db_a.close()
    for file in enumerate(files_anomaly):
        for table_name in table_names:
            merge(out_archive, file, table_name)

    db_a = sqlite3.connect(os.path.join(archive_path, files_metadata[0]))
    table_names = load_table_names(db_a)
    db_a.close()
    for file in enumerate(files_metadata):
        for table_name in table_names:
            merge(out_archive, file, table_name)