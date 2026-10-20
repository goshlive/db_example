# Quick start: Student web demo

1. **Create a Python environment from the project root.** Install Python 3.10+ and MySQL Server, and start MySQL. Open a terminal in the project folder containing this README and `example-orm2`.

   Windows (PowerShell or Command Prompt):
   ```powershell
   python -m venv .venv
   ```
   macOS / Linux:
   ```bash
   python3 -m venv .venv
   ```
   On Linux, install your distribution's `python3-venv` package if prompted.

2. **Activate the environment and install dependencies.** Use the command for your terminal:

   | Terminal | Activation command |
   | --- | --- |
   | Windows PowerShell | `.\.venv\Scripts\Activate.ps1` |
   | Windows Command Prompt | `.venv\Scripts\activate.bat` |
   | macOS / Linux (bash/zsh) | `source .venv/bin/activate` |

   If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`, then retry. From the project root, run:
   ```bash
   python -m pip install -r example-orm2/student/requirements.txt
   ```

3. **Configure MySQL and run the example.** In MySQL Workbench or the MySQL command-line client, run:
   ```sql
   CREATE DATABASE IF NOT EXISTS univerity;
   ```
   `univerity` is the spelling used by the app. In your terminal, with the Python environment active, generate a random local secret:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   Copy the printed 64-character value. Create or edit `example-orm2/student/.env` with your local MySQL credentials and paste that value after `SECRET_KEY=` (replace the placeholder below; keep any existing settings you need):
   ```dotenv
   DB_USER=root
   DB_PASS=your_mysql_password
   DB_HOST=127.0.0.1
   DB_PORT=3306
   DB_NAME=univerity
   SECRET_KEY=paste_your_generated_value_here
   ```
   Generate the secret once for your local setup and keep this `.env` file private; do not commit it to GitHub.

   Use a MySQL account with permission to create tables and read/write this database. The app creates missing tables at startup; it does not create the database or insert sample data. **Adding students also requires the course-provided MySQL function `get_next_id()` in this database**, returning a unique student ID of at most five characters. Its SQL definition is not included in this repository; obtain it from your instructor before trying Add Student. The home page can open with an empty student table without this function.

   With the environment active, run this command from the project root:
   ```bash
   python example-orm2/student/app.py
   ```

4. **Open the demo in your browser.** Keep the terminal running and visit **http://127.0.0.1:5000/** on the same laptop. You should see the student list (initially empty on a new database). Press `Ctrl+C` in the terminal to stop the server; run `deactivate` to leave the environment. For later sessions, activate the environment again before starting the app.

---

# Code Example (Python) to demonstrate the use of the Data Access Layer

#### Configuration and execution of the CQRS code. To try code from other examples/modules, please check the respective README.TXT files.

----
#### CQRS (Command Query Responsibility Segregation) is a design pattern that separates data writing (commands) and data reading (queries) into separate models or databases.
----

1. Install modules:
pip install pika sqlalchemy pymysql cryptography


2. RabbitMQ is built on Erlang, so this must be installed first.
Go to the official Erlang for Windows page:
👉 https://www.erlang.org/downloads
Download the latest Erlang/OTP Windows installer (for example “OTP 27.x Windows 64-bit”).
Run the installer → keep defaults → wait for it to finish.
After install, confirm it’s available:
> erl

3. Install RabbitMQ Server
Download the latest Windows installer from:
👉 https://www.rabbitmq.com/install-windows.html
Direct link to the 64-bit installer (.exe):
https://github.com/rabbitmq/rabbitmq-server/releases
(scroll to the latest release and download the .exe for Windows x64)
Run the installer → keep defaults.
It will install RabbitMQ as a Windows Service.
After installation, verify the service is running:
Open Services (services.msc), find RabbitMQ, set Startup Type = Automatic, and ensure Status = Running.
Or run in PowerShell:
> net start RabbitMQ

4. Enable the management dashboard (optional but very useful)
The management plugin gives you a friendly web UI to inspect queues.
Open Command Prompt (not PowerShell) as Administrator.
Enable the plugin:
	>bbitmq-plugins enable rabbitmq_management


Restart the service:
	>et stop RabbitMQ
	>et start RabbitMQ

5. Open the UI in your browser:
👉 http://localhost:15672

Login with the default credentials:
Username: guest
Password: guest
(By default, the guest user may connect only from localhost.)


RUN:
python consumer.py (separated command)
python producer.py (separated command)
python query_user.py (separated command)
