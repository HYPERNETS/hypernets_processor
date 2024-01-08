from hypernets_processor.version import __version__
import sys, sqlite3
import os
import struct

"""___Authorship___"""
__author__ = "Pieter De Vis"
__created__ = "29/3/2023"
__version__ = __version__
__maintainer__ = "Pieter De Vis"
__email__ = "pieter.de.vis@npl.co.uk"
__status__ = "Development"

archive_path = r"/home/data/insitu/hypernets/archive"

files_archive = [
    "archive_ATGE.db",
    "archive_BASP.db",
    "archive_WWUK.db",
]
files_anomaly = [
    "anomaly_ATGE.db",
    "anomaly_BASP.db",
    "anomaly_WWUK.db",
]
files_metadata = [
    "metadata_ATGE.db",
    "metadata_BASP.db",
    "metadata_WWUK.db",
]

def remove_files(archive_path, file, table_name):
    db_b = sqlite3.connect(os.path.join(archive_path, file))
    cursor_b = db_b.cursor()
    for i, row in enumerate(cursor_b.execute("SELECT * FROM " + table_name)):
        row = ["none" if (is_invalid(v)) else v for v in row]
        row = tuple(row)
        date=row[1][39:52]
        try:
            os.remove(row[7])
        except:
            print(row[7], "file does not exist")

        dir_name=os.path.join(os.path.dirname(row[7]),"plots")
        test = os.listdir(dir_name)

        for item in test:
            if date in item:
                try:
                    os.remove(os.path.join(dir_name, item))
                except:
                    print(os.path.join(dir_name, item), "file does not exist")

        try:
            os.remove(row[7])
        except:
            print(row[7], "file does not exist")

def is_invalid(v):
    if v is None:
        return True
    elif isinstance(v, bytes):
        return True
    return False


def load_table_names(db_a):
    cursor_a = db_a.cursor()
    cursor_a.execute("SELECT name FROM sqlite_master WHERE type='table';")

    table_counter = 0
    table_names = []
    for table_item in cursor_a.fetchall():
        current_table = table_item[0]
        table_counter += 1
        # print("-> " + current_table)
        table_names.append(current_table)

    return table_names


if __name__ == "__main__":
    print(os.path.join(archive_path, files_archive[0]))
    db_a = sqlite3.connect(os.path.join(archive_path, files_archive[0]))
    table_names = load_table_names(db_a)
    db_a.close()
    print(table_names)
    for file in files_archive:
        print(file)
        for table_name in table_names:
            remove_files(archive_path, file, table_name)
