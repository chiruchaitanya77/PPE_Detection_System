# PPE Detection System

<img src="https://github.com/user-attachments/assets/f9a4b01a-4c6d-496e-9c7b-2c9af13591fb" alt="PPE Detection System Poster" width="1000">

## 🚀 About the Project
This **PPE Detection System** is our **final year major project** developed by a team of **B.Tech CSE students**. The project aims to enhance **workplace safety in construction environments** by automatically detecting Personal Protective Equipment (PPE) using deep learning. Leveraging **YOLOv8 by Ultralytics**, our system accurately identifies PPE, ensuring compliance and reducing workplace risks.

## ✨ Key Features
✅ **Automated PPE Detection** – Uses deep learning to identify helmets, vests, gloves, and other safety gear.

✅ **Real-Time PPE Recognition** – Uses YOLOv8 for quick and accurate identification of PPE in live environments.

✅ **Secure User Authentication** – Supports role-based access for admins and users.

✅ **User-Friendly Dashboard** – Separate interfaces for users and admins. 

✅ **Live Streaming Support** – Continuously monitors work areas for PPE compliance.

✅ **Non-Compliance Alerts** – Identify and alert for missing PPE.  

✅ **Django-Based Web Application** – Built using Python Django framework for scalability and efficiency.

---

## 🏛 Modules
### 🔹 Admin Dashboard
- Activate/Deactivate and Manage users.

### 🔹 User Dashboard
- Register and login securely.
- Access real-time detection results.
- View PPE compliance reports.

### 🔹 Live Streaming & Detection
- Integrates live video for real-time PPE monitoring.
- Detect PPE compliance in uploaded from video streams.
- Detects helmets, vests, gloves, and other PPE.

---

## 📷 Project Screenshots

### 🔹 Landing Page
<img width="500px" alt="Landing Page" src="https://github.com/user-attachments/assets/6b2f5898-029f-49cf-8c9d-781608a53ecf" />

<img width="500px" alt="Project Overview" src="https://github.com/user-attachments/assets/7fd18c22-b52d-4431-8c5b-926be63e2912" />

<img width="500px" alt="Demo Video" src="https://github.com/user-attachments/assets/abab9ab2-3b5b-423b-8cd8-2928df0aba58" />

### 🔹 User Registration Page
<img width="500px" alt="Image" src="https://github.com/user-attachments/assets/6c09d7e3-e615-4139-bf52-c397b8283985" />

### 🔹 User Login Page
<img width="500px" alt="Image" src="https://github.com/user-attachments/assets/17c4b412-c492-4634-b0b3-93290c3bc735" />

### 🔹 User Dashboard
<img width="500px" alt="Image" src="https://github.com/user-attachments/assets/bec2853b-8e41-4209-9ecc-1fa7df353401" />

### 🔹 Video Upload Page
<img width="500px" alt="Image" src="https://github.com/user-attachments/assets/ffe91841-c9a7-49f8-b071-26d00082d0bc" />

### 🔹 Detection Output Page
<img width="500px" alt="Image" src="https://github.com/user-attachments/assets/78ffb993-9dc6-40da-b275-9cf107e0cfd4" />

### 🔹 Admin Login Page
<img width="500px" alt="Image" src="https://github.com/user-attachments/assets/25d1ae17-a7df-46c7-a593-d4033ae5db9b" />

### 🔹 Admin Dashboard
<img width="500px" alt="Image" src="https://github.com/user-attachments/assets/c57f1690-75af-4362-88af-95b035b11524" />

---

## 🔧 Installation Guide
To run this project on your local machine, follow these steps:

### 1️⃣ Clone the Repository
```sh
git clone https://github.com/chiruchaitanya77/PPE_Detection_System.git
```

### 2️⃣ Navigate to the Project Directory
```sh
cd PPE_Detection_System
```

### 3️⃣ Install Required Dependencies
```sh
pip install -r requirements.txt
```

### 4️⃣ Apply Database Migrations
```sh
python manage.py makemigrations
python manage.py migrate
```

### 5️⃣ Run the Django Server
```sh
python manage.py runserver
```
Now, open your browser and go to **http://127.0.0.1:8000/** to access the system.

### 6️⃣ (Optional) Create a Django Admin User
If you want to access the **Django Administrator Panel**, run:
```sh
python manage.py createsuperuser
```
Follow the prompts to set up an admin username and password. Then, log in at **http://127.0.0.1:8000/admin/**.

---

## 📌 Final Year Major Project
This project was developed as part of our **final year B.Tech CSE major project** by a team of five dedicated students. Our goal was to integrate deep learning into workplace safety measures, ensuring **accurate and efficient PPE detection** to minimize workplace hazards.

Made with ✨ by our **B.Tech Final Year Team**.

---
