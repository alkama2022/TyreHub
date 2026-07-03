# 🚗 TyreHub

TyreHub is a production-ready Automobile Tyre Management System built with **Django**, **Django REST Framework**, and **PostgreSQL**. It provides secure and scalable REST APIs for managing tyre inventory, customers, suppliers, sales, maintenance, and business operations.

## ✨ Features

- 🔐 JWT Authentication & Authorization
- 👥 Customer Management
- 🛞 Tyre Inventory Management
- 📦 Stock Tracking
- 🏢 Supplier Management
- 💰 Sales & Order Management
- 📊 Reports & Analytics
- 🔍 Barcode/QR Code Support
- 📝 Tyre Inspection & Maintenance Records
- 📄 API Documentation
- ⚡ RESTful API Architecture

## 🛠️ Tech Stack

- Python 3.x
- Django
- Django REST Framework
- PostgreSQL
- JWT Authentication
- Git & GitHub

## 📂 Project Structure

```
TyreHub/
├── config/
├── apps/
│   ├── accounts/
│   ├── tyres/
│   ├── inventory/
│   ├── customers/
│   ├── suppliers/
│   ├── sales/
│   └── reports/
├── requirements.txt
├── manage.py
└── README.md
```

## 🚀 Getting Started

### Clone the repository

```bash
git clone https://github.com/yourusername/tyrehub.git
cd tyrehub
```

### Create a virtual environment

```bash
python -m venv venv
```

### Activate the virtual environment

**Windows**

```bash
venv\Scripts\activate
```

**Linux/macOS**

```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file and add your PostgreSQL credentials.

```env
DB_NAME=tyrehub
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Run the development server

```bash
python manage.py runserver
```

The API will be available at:

```
http://127.0.0.1:8000/
```

## 📌 Roadmap

- [ ] User Authentication
- [ ] Customer Module
- [ ] Supplier Module
- [ ] Tyre Inventory
- [ ] Sales Management
- [ ] Barcode Integration
- [ ] Reporting Dashboard
- [ ] Notifications
- [ ] Deployment

## 🤝 Contributing

Contributions are welcome. Feel free to fork the repository, create a feature branch, and submit a pull request.

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Alkama Umar Liman**

Information Technology Student | Backend Developer | Python & Django Enthusiast
