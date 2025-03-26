# OPC UA Client Application

A full-stack web application for secure communication with OPC UA servers. Built with Vue.js and Django, this application provides a modern web interface for OPC UA operations with real-time data updates.

## Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Security](#security)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)
- [Contact](#contact)

## 🌟 Features

- **Server Connection**

  - Discover and connect to OPC UA servers.
  - Support for secure endpoints and encrypted communication.
  - Username/password and certificate-based authentication.

- **Data Operations**

  - Read/write operations for one or multiple nodes.
  - Automatic data type detection and conversion.
  - Batch operations support.

- **Real-time Updates**

  - WebSocket‑based live data subscription.
  - Configurable update intervals.
  - Real‑time value monitoring.

- **Node Management**
  - Node registration for optimized access.
  - Connection state management.
  - Robust error handling and recovery.

## 📸 Screenshots

<img src="docs/images/screenshot.gif" alt="Screenshots"/>

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn
- An OPC UA Server for testing

### Backend Setup

1. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Python dependencies:**

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

   3. **Run migrations:**

   ```bash
   python manage.py migrate
   ```

3. **Start the Django server:**

   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. **Install dependencies:**

   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server:**

   ```bash
   npm run dev
   ```

## 🔧 Configuration

### Security Configuration

1. **Generate Certificates** (if using a secure connection):

   ```bash
   openssl req -x509 -newkey rsa:2048 -keyout opcua_client_key.pem -out opcua_client_cert.pem -days 365 -config openssl.conf -nodes
   ```

2. **Copy Certificates:**

   Place `opcua_client_key.pem` and `opcua_client_cert.pem` in the `backend/opc_ua/certificates/` folder.

## 📡 API Endpoints

| **Endpoint**                        | **Method** | **Description**                                        |
| ----------------------------------- | ---------- | ------------------------------------------------------ |
| `/api/connection/?url=<server_url>` | GET        | Retrieve available endpoints from server               |
| `/api/connection/`                  | POST       | Connect to server with selected endpoint configuration |
| `/api/connection/`                  | DELETE     | Disconnect from the server                             |
| `/api/read-write/`                  | POST       | Read values from one or multiple nodes                 |
| `/api/read-write/`                  | PUT        | Write values to one or multiple nodes                  |
| `/api/register/`                    | GET        | Get all registered nodes                               |
| `/api/register/`                    | POST       | Register nodes for optimized access                    |
| `/api/register/`                    | DELETE     | Unregister nodes                                       |
| `/api/subscribe/`                   | GET        | Get all active subscriptions                           |
| `/api/subscribe/`                   | POST       | Create a new subscription                              |
| `/api/subscribe/`                   | DELETE     | Delete a subscription                                  |

## 🔒 Security

- Supports OPC UA security policies.
- Certificate-based authentication.
- Encrypted communication.
- CORS protection.
- Django security middleware.

## 🤝 Contributing

1. **Fork** the repository.
2. Create your feature branch:  
   `git checkout -b feature/AmazingFeature`
3. **Commit** your changes:  
   `git commit -m 'Add some AmazingFeature'`
4. **Push** to the branch:  
   `git push origin feature/AmazingFeature`
5. Open a **Pull Request**.

## ✨ Acknowledgments

- [Python OPC UA](https://python-opcua.readthedocs.io/) for the OPC UA implementation.
- [Vue.js](https://vuejs.org/) for the reactive frontend framework.
- [Django](https://www.djangoproject.com/) for a robust backend framework.
- [Quasar Framework](https://quasar.dev/) for advanced UI components.

## 📫 Contact

Özkan ERÖZCAN  
[@ozkanerozcan](https://github.com/ozkanerozcan) · ozkanerozcan@gmail.com

Project Link: [https://github.com/ozkanerozcan/opc-ua-client](https://github.com/ozkanerozcan/opc-ua-client)
