# Load the clean table into MySQL

import getpass
import mysql.connector
import pandas as pd

CSV_FILE = "data/processed/settlements_clean.csv"
BATCH = 2000   


def connect():
    password = getpass.getpass("MySQL password: ")
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=password,
        database="ngn_dre",
    )


def main():
    # 1. Read the clean file. Blanks become None, which MySQL stores as NULL
    df = pd.read_csv(CSV_FILE)
    df = df.astype(object).where(pd.notna(df), None)
    print("Rows to load:", len(df))

    conn = connect()
    cur = conn.cursor()

    # 2. Empty the table first, so running this twice never doubles the rows
    cur.execute("TRUNCATE TABLE settlements")

    # 3. Build the insert command from the CSV column names
    cols = list(df.columns)
    sql = (f"INSERT INTO settlements ({', '.join(cols)}) "
           f"VALUES ({', '.join(['%s'] * len(cols))})")

    # 4. Send the rows in batches
    rows = df.values.tolist()
    for i in range(0, len(rows), BATCH):
        cur.executemany(sql, rows[i:i + BATCH])
        print("Loaded", min(i + BATCH, len(rows)), "of", len(rows))
    conn.commit()

    # 5. Check
    cur.execute("SELECT COUNT(*) FROM settlements")
    print("Rows in settlements now:", cur.fetchone()[0])
    conn.close()


if __name__ == "__main__":
    main()