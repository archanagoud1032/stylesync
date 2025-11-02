# stylesync
🅰️ StyleSync – Fashion Styling & E-Commerce Integration Platform
🌸 Overview

StyleSync is a web-based fashion styling platform that connects stylists and users in an interactive, community-driven environment.
Stylists can create and upload complete looks with tagged product links, while users can browse, interact, and shop directly through these tagged items.
Each interaction rewards stylists with points, creating a system that blends creativity, commerce, and collaboration.

✨ Key Features

👗 Stylist Dashboard – Stylists can create looks, tag fashion items, and manage their uploaded styles.

🛍️ User Interface – Users can browse looks, view tagged items, and shop via integrated product links.

🪙 Reward System – Stylists earn points whenever users engage with their tagged products.

🔐 Secure Login/Signup – Separate authentication for stylists and users.

🖼️ Interactive Tagging – Tag products on look images using clickable overlays.

📈 Points Tracking – Stylists can view and manage their earned points.

🧠 Tech Stack
Layer	Technology
Frontend	HTML, CSS, JavaScript
Backend	Flask (Python)
Database	MySQL
Real-Time Features	Flask-SocketIO, WebSockets
Hosting (optional)	Netlify (Frontend), Flask (Backend)
⚙️ Installation & Setup
1. Clone the repository

2. Create a virtual environment
python -m venv venv

3. Activate it

Windows:

venv\Scripts\activate


Mac/Linux:

source venv/bin/activate

4. Install dependencies
pip install -r requirements.txt

5. Configure database

Open your Flask config or connection section and update:

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_password",
    database="stylesync"
)

Then import your .sql schema into MySQL.

6. Run the application
python app.py


App runs at → http://127.0.0.1:5000

📸 Screenshots (Optional)

Add screenshots of your login page, stylist dashboard, tagged look, etc.

🧩 Folder Structure
stylesync/
│
├── app.py
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── view_look.html
├── requirements.txt
└── README.md

🚀 Future Enhancements

Integrate AI-based outfit recommendations.

Enable brand partnerships directly within the platform.

Add payment gateway and redeem system for stylist rewards.

Improve UI with modern design frameworks
