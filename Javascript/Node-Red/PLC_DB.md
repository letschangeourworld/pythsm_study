To connect a Mitsubishi MELSEC PLC to a MySQL database using Node-RED, we need to go through the following steps:

1.	Set up Node-RED environment: Ensure you have Node-RED installed and running.

2.	Install necessary Node-RED nodes:
	• node-red-contrib-modbustcp (for communicating with the PLC)
	• node-red-node-mysql (for MySQL database interaction)

3.	Create MySQL table: We need to create a table in the MySQL database to store the PLC data.

4.	Design the Node-RED flow:
	• Connect to the PLC and read data.
	• Format the data and insert it into the MySQL database.
	• Include a debug node to verify data collection.


Here’s an example Node-RED flow that accomplishes this:

1.Install required Node-RED nodes: Run the following commands in your Node-RED directory:

npm install node-red-contrib-modbustcp
npm install node-red-node-mysql

2.MySQL table creation:

CREATE DATABASE plc_data;
USE plc_data;
CREATE TABLE readings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    plc_value INT
);

3.	Node-RED Flow:

[
    {
        "id": "a1d1b77c.b5c208",
        "type": "tab",
        "label": "PLC to MySQL",
        "disabled": false,
        "info": ""
    },
    {
        "id": "72f3e845.e4c8c8",
        "type": "modbustcp-read",
        "z": "a1d1b77c.b5c208",
        "name": "",
        "topic": "",
        "dataType": "HoldingRegister",
        "adr": "0",
        "quantity": "1",
        "server": "6a2e6a57.4a5cc4",
        "interval": "5",
        "unit_id": "1",
        "reconnecttimeout": "10",
        "timeout": "5",
        "retries": "10",
        "x": 140,
        "y": 80,
        "wires": [
            [
                "8aef4c3d.14695"
            ]
        ]
    },
    {
        "id": "8aef4c3d.14695",
        "type": "function",
        "z": "a1d1b77c.b5c208",
        "name": "Format Data",
        "func": "msg.topic = \"INSERT INTO readings (plc_value) VALUES (?)\";\nmsg.payload = [msg.payload[0]];\nreturn msg;",
        "outputs": 1,
        "noerr": 0,
        "initialize": "",
        "finalize": "",
        "libs": [],
        "x": 340,
        "y": 80,
        "wires": [
            [
                "c3b5d7d7.f47f28",
                "d52f0b6b.4d2a58"
            ]
        ]
    },
    {
        "id": "c3b5d7d7.f47f28",
        "type": "mysql",
        "z": "a1d1b77c.b5c208",
        "mydb": "92d7c9a1.3d0e08",
        "name": "",
        "x": 540,
        "y": 80,
        "wires": [
            [
                "a758dabe.593eb8"
            ]
        ]
    },
    {
        "id": "d52f0b6b.4d2a58",
        "type": "debug",
        "z": "a1d1b77c.b5c208",
        "name": "PLC Data",
        "active": true,
        "tosidebar": true,
        "console": false,
        "tostatus": false,
        "complete": "payload",
        "targetType": "msg",
        "statusVal": "",
        "statusType": "auto",
        "x": 540,
        "y": 140,
        "wires": []
    },
    {
        "id": "6a2e6a57.4a5cc4",
        "type": "modbustcp-server",
        "z": "",
        "name": "PLC",
        "host": "192.168.0.10",
        "port": "502",
        "unit_id": "1",
        "reconnecttimeout": "10"
    },
    {
        "id": "92d7c9a1.3d0e08",
        "type": "MySQLdatabase",
        "z": "",
        "name": "MySQL",
        "host": "localhost",
        "port": "3306",
        "db": "plc_data",
        "tz": "",
        "charset": "UTF8"
    }
]

Explanation:

1.modbustcp-read node:
  • Reads data from the PLC at specified intervals (every 5 seconds in this example).
  • The server configuration node (modbustcp-server) specifies the PLC IP address and port.

2.Function node (Format Data):
  • Prepares the SQL query for inserting data into the MySQL database.
  • Formats the payload to match the query parameters.

3.MySQL node:
  • Executes the SQL query to insert the data into the MySQL database.
  • The mydb configuration node specifies the MySQL database connection details.

4.Debug node:
  • Displays the data read from the PLC in the debug pane of Node-RED, allowing you to verify that data is being collected correctly.

This flow continuously reads data from the PLC and stores it into a MySQL database. The debug node helps ensure that the data is being collected correctly from the PLC.



To connect a Mitsubishi Electric PLC (MELSEC) to a MySQL database using Node-RED, and to store data into the MySQL database while including debugging steps, follow the flow and steps below:

Prerequisites:
	1.	Node-RED installed on your system.
	2.	MySQL server set up and running.
	3.	Node-RED nodes installed for MySQL (node-red-node-mysql) and MELSEC PLC (node-red-contrib-mcprotocol).

Step-by-Step Node-RED Flow

1. Install necessary Node-RED nodes:

npm install node-red-node-mysql
npm install node-red-contrib-mcprotocol

2.	Create the MySQL table:
You need to create a table in your MySQL database to store the PLC data. Below is an example SQL command to create a table:

CREATE DATABASE IF NOT EXISTS plc_data;
USE plc_data;

CREATE TABLE IF NOT EXISTS melsec_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    plc_value VARCHAR(255)
);

3.	Node-RED Flow:
Here is a Node-RED flow that reads data from the MELSEC PLC, stores it in a MySQL database, and includes debug nodes to check the data:

[
    {
        "id": "d5e9a68a.f72ac8",
        "type": "tab",
        "label": "MELSEC to MySQL",
        "disabled": false,
        "info": ""
    },
    {
        "id": "9b1838a8.0d7988",
        "type": "mcprotocol in",
        "z": "d5e9a68a.f72ac8",
        "name": "",
        "connection": "4c7b2a9b.7c6ab4",
        "address": "D0",
        "datatype": "WORD",
        "topic": "",
        "x": 130,
        "y": 80,
        "wires": [
            [
                "5c0e4c3b.7919b4",
                "b09b2ab2.6ddce8"
            ]
        ]
    },
    {
        "id": "5c0e4c3b.7919b4",
        "type": "debug",
        "z": "d5e9a68a.f72ac8",
        "name": "PLC Data",
        "active": true,
        "tosidebar": true,
        "console": false,
        "tostatus": false,
        "complete": "payload",
        "targetType": "msg",
        "x": 340,
        "y": 80,
        "wires": []
    },
    {
        "id": "b09b2ab2.6ddce8",
        "type": "function",
        "z": "d5e9a68a.f72ac8",
        "name": "Format Data",
        "func": "msg.topic = \"INSERT INTO melsec_data (plc_value) VALUES ('\" + msg.payload + \"')\";\nreturn msg;",
        "outputs": 1,
        "noerr": 0,
        "initialize": "",
        "finalize": "",
        "libs": [],
        "x": 330,
        "y": 140,
        "wires": [
            [
                "f6f49b59.b9e9b8",
                "cf828926.65dc3"
            ]
        ]
    },
    {
        "id": "f6f49b59.b9e9b8",
        "type": "debug",
        "z": "d5e9a68a.f72ac8",
        "name": "SQL Query",
        "active": true,
        "tosidebar": true,
        "console": false,
        "tostatus": false,
        "complete": "payload",
        "targetType": "msg",
        "x": 540,
        "y": 140,
        "wires": []
    },
    {
        "id": "cf828926.65dc3",
        "type": "mysql",
        "z": "d5e9a68a.f72ac8",
        "mydb": "29e9d6ae.0bb20a",
        "name": "",
        "x": 520,
        "y": 200,
        "wires": [
            [
                "91568e5e.437bf"
            ]
        ]
    },
    {
        "id": "91568e5e.437bf",
        "type": "debug",
        "z": "d5e9a68a.f72ac8",
        "name": "MySQL Response",
        "active": true,
        "tosidebar": true,
        "console": false,
        "tostatus": false,
        "complete": "payload",
        "targetType": "msg",
        "x": 720,
        "y": 200,
        "wires": []
    },
    {
        "id": "4c7b2a9b.7c6ab4",
        "type": "mcprotocol-connection",
        "name": "MELSEC PLC",
        "host": "192.168.0.1",
        "port": "1025",
        "protocol": "TCP"
    },
    {
        "id": "29e9d6ae.0bb20a",
        "type": "MySQLdatabase",
        "name": "MySQL Database",
        "host": "127.0.0.1",
        "port": "3306",
        "db": "plc_data",
        "tz": "",
        "charset": "UTF8"
    }
]

Explanation of the Flow:

	•	MC Protocol Node (mcprotocol in):
	•	This node connects to the MELSEC PLC and reads data from address D0.
	•	Configuration for connection (host, port, protocol) should match your PLC settings.
	•	Debug Node (debug - PLC Data):
	•	Used to display the incoming data from the PLC for debugging purposes.
	•	Function Node (function - Format Data):
	•	Formats the incoming PLC data into an SQL INSERT statement.
	•	Debug Node (debug - SQL Query):
	•	Displays the formatted SQL query to verify its correctness before insertion into the database.
	•	MySQL Node (mysql):
	•	Executes the SQL query to insert data into the MySQL table.
	•	Configured with your MySQL connection details.
	•	Debug Node (debug - MySQL Response):
	•	Displays the response from the MySQL database to verify if the data was inserted successfully.

Setting Up the Flow:

	1.	Configure the PLC connection: Update the IP address and port in the mcprotocol-connection configuration.
	2.	Configure the MySQL connection: Update the host, port, and database name in the MySQLdatabase configuration.
	3.	Deploy the flow: Once all nodes are configured, deploy the flow to start collecting and storing data.

This setup will help you collect data from a MELSEC PLC and store it in a MySQL database while allowing you to debug the data at various stages of the flow.

