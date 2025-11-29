Install modules:
pip install pika sqlalchemy pymysql cryptography


1. RabbitMQ is built on Erlang, so this must be installed first.
Go to the official Erlang for Windows page:
👉 https://www.erlang.org/downloads
Download the latest Erlang/OTP Windows installer (for example “OTP 27.x Windows 64-bit”).
Run the installer → keep defaults → wait for it to finish.
After install, confirm it’s available:
> erl

2. Install RabbitMQ Server
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

3. Enable the management dashboard (optional but very useful)
The management plugin gives you a friendly web UI to inspect queues.
Open Command Prompt (not PowerShell) as Administrator.
Enable the plugin:
	>bbitmq-plugins enable rabbitmq_management


Restart the service:
	>et stop RabbitMQ
	>et start RabbitMQ

4. Open the UI in your browser:
👉 http://localhost:15672

Login with the default credentials:
Username: guest
Password: guest
(By default, the guest user may connect only from localhost.)


RUN:
python consumer.py (separated command)
python producer.py (separated command)
python query_user.py (separated command)