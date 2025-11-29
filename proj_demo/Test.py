from sqlalchemy import create_engine, text

# Ganti USER, PASS, HOST, PORT, DBNAME sesuai konfigurasi
engine = create_engine("mysql+pymysql://root:Br4v02009@localhost:3306/prj_demo", echo=False, future=True)

with engine.connect() as conn:
    # Contoh memanggil Stored Procedure
    conn.execute(text("CALL sp_transfer(:from_id, :to_id, :amt)"),
                 {"from_id": 1, "to_id": 2, "amt": 50.00})
    conn.commit()  # commit jika procedure tidak commit otomatis

    # Contoh memanggil Function
    res = conn.execute(text("SELECT fn_get_balance(:id) AS balance"), {"id": 1})
    row = res.fetchone()
    print("Balance:", row.balance)

    # Contoh mengakses View
    res = conn.execute(text("SELECT * FROM v_accounts_overview"))
    for r in res.fetchall():
        print(r)

    # Contoh ekskusi Trigger: otomatis terkeskusi Ketika terjadi DML
    conn.execute(text("UPDATE accounts SET balance = balance + 10 WHERE id = :id"), {"id": 1})
    conn.commit()

    # Memastikan tabel audit ketika trigger bekerja
    res = conn.execute(text("SELECT * FROM account_audit ORDER BY created_at DESC LIMIT 5"))
    for r in res.fetchall():
        print(r)
