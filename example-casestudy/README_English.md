# Restaurant Python case study

Copy the entire `example-casestudy` folder beside `example-cars`, `example-orm1` and your other examples in the VS Code DB workspace. No existing project file needs to be replaced.

The database and these four tables must already exist: CUSTOMER, CUSTOMER_ORDER, MENU_ITEM, ORDER_ITEM. This project never creates or alters them. Match DB_NAME to your actual Restaurant schema, including table-name case.

## Windows PowerShell quick start

```powershell
cd example-casestudy
py -3 -m venv .venv
$casePython = ".\.venv\Scripts\python.exe"
& $casePython -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit the new `.env`. Use your MySQL credentials and existing schema name. Environment variables already set in the terminal override `.env`; the parent workspace `.env` is not loaded. If using an existing suitable environment, skip creating `.venv` and set `$casePython` to that environment's Python executable. In VS Code select the same interpreter. The commands above do not require PowerShell activation.

```powershell
& $casePython check_database.py
# Optional ONLY if all four existing tables are empty:
& $casePython seed_sample.py
& $casePython console.py --mode prepared crud-demo
& $casePython console.py --mode orm orders --id C01
& $casePython console.py --mode prepared details --id O101
& $casePython web_app.py
```

Open http://127.0.0.1:5000. Press Ctrl+C in the terminal to stop. A new terminal needs the `$casePython` assignment again. For macOS/Linux, use `python3 -m venv .venv` and replace `& $casePython` with `.venv/bin/python`.

## Console CRUD one operation at a time

```powershell
& $casePython console.py --mode prepared create --id CDEMO --name "Dewi"
& $casePython console.py --mode prepared get --id CDEMO
& $casePython console.py --mode prepared update --id CDEMO --name "Dewi Putri"
& $casePython console.py --mode prepared delete --id CDEMO
```

Repeat with `--mode orm`. For the deliberately unsafe version, set `ALLOW_UNSAFE_SQL=true` in `.env`, restart the web app, and use `--mode raw` or the UI selector. No login or production deployment is included; the Flask server binds to localhost and debug is off.

```powershell
& $casePython console.py --mode raw injection-demo
& $casePython console.py --mode prepared injection-demo
& $casePython console.py --mode orm injection-demo
& $casePython verify_live.py
```

The reference data yields two C01 orders (O101, O103), two O101 menu lines (50000 and 8000), and total 58000. Without sample data, joins can legitimately return empty lists. `seed_sample.py` refuses a partially or fully populated database and never resets/deletes existing data. Run it only when nobody else is writing to the teaching database.

## Files and reuse

- `raw_sql.py`: deliberately unsafe interpolated SQL; use only in this local lab.
- `prepared_sql.py`: hand-written SQL with `prepared=True` and `%s` binding.
- `models.py`, `orm_repository.py`: four ORM classes, association object and queries.
- `repositories.py`: selects a mode with the same method interface.
- `dto.py`: detached data returned by all implementations, with decimal/date serialization.
- `db.py`, `config.py`: connection lifetime and this folder's configuration.
- `console.py`, `web_app.py`, `templates/index.html`: console and web callers.
- `check_database.py`, `seed_sample.py`, `verify_live.py`: preflight, optional sample, live checks.

Both callers use list_customers, get_customer, create_customer, update_customer, delete_customer, search_customers, customer_orders and order_details. Routes contain no SQL and repositories contain no Flask imports or printing.

Each repository write is one transaction. `crud-demo` is several committed operations and deletes its own CTEST row at the end; it refuses an existing CTEST. Do not use separately committed methods to create an order plus lines: a future multi-table service must share one connection/session and transaction. Deleting C01 is rejected because it has orders. Ordinary FKs do not enforce that every order has at least one line. No cascade delete is configured.

An update rowcount can be zero if a direct MySQL UPDATE changes nothing, while the ORM returns one for an existing matched customer; compare the resulting data rather than treating those counts as equivalent.

Raw SQL is not inherently unsafe: interpolation of untrusted values is the problem. ORM binding is not a claim of server-side prepared execution. ORM expressions can also be undermined by interpolated SQL text. Placeholders represent values, not dynamic table or column names.

## Web walkthrough

Choose prepared, create CWEB, read it, update it, read it again, delete it. Repeat in ORM and optionally raw. Use 1-N with C01, M-N with O101. In exact-name search compare Made, `' OR '1'='1`, and O'Connor in each mode. The raw payload returns all customers; raw O'Connor gives a database error. Safe modes treat both as literal values. JSON examples: `/api/customers?mode=prepared` and `/api/orders/O101/items?mode=orm`.

POST forms carry a session token; use the displayed form instead of invoking a write endpoint as a URL. GET cannot create/update/delete. Keep the SQL injection example on SELECT; no destructive payload is needed.

## Troubleshooting

- Access denied: verify account, password, host and database grants.
- Unknown database/table: use the actual DB_NAME and the exact four uppercase table names.
- Missing modules: install requirements with the same Python used to run the files.
- Port in use: set FLASK_PORT=5001 and restart.
- Raw disabled: enable the local lab flag and restart; no manual escaping fix is applied.
- Duplicate ID: choose another temporary ID; no existing row is overwritten automatically.
- Foreign-key error: remove dependent data only if your exercise calls for it; use CWEB/CTEST for ordinary deletion.
- Name updates: inspect returned data; MySQL may report zero changed rows when the name was unchanged.

## Documentation

https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursorprepared.html
https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html
https://docs.sqlalchemy.org/en/20/orm/session_basics.html
https://flask.palletsprojects.com/en/stable/tutorial/views/
