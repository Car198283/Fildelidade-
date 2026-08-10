import sqlite3
conn = sqlite3.connect('bartcellos_loyalty.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(users)")
print("Colunas da tabela 'users':")
for row in cursor.fetchall():
    print(f"  {row[1]}: {row[2]}")
conn.close()
