# EG Cash Rewards Platform

A complete, responsive rewards platform for your AI agent, built with **Flask** and **Bootstrap 5**.

## Features
- Landing page (EG Cash style)
- User authentication (signup, login, logout)
- Referral rewards and dashboard
- Task/offerwall dashboard (placeholders for AdMantum, CPALead, Wannads, etc.)
- Daily check-in rewards
- Profile/account settings
- Transactions and redemption history
- Redeem page for payouts (PayPal, PayTM, Amazon, Google Play, etc.)
- Admin dashboard for announcements and redemption management
- Leaderboard for top users
- Responsive, modern UI

## Tech Stack
- **Backend:** Flask, Flask-Login, Flask-SQLAlchemy
- **Frontend:** Bootstrap 5, Jinja2 templates
- **Database:** SQLite (default, easy to switch to PostgreSQL/MySQL)

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd pocket
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app:**
   ```bash
   python3 app.py
   ```
   The app will be available at [http://127.0.0.1:5000](http://127.0.0.1:5000)

5. **Create an admin user:**
   - Register a new account, then set `is_admin` to `True` for that user in the database (using SQLite browser or shell).

## Folder Structure
```
/ (project root)
├── app.py
├── models.py
├── extensions.py
├── requirements.txt
├── README.md
├── /templates
│   ├── base.html
│   ├── landing.html
│   ├── how_it_works.html
│   ├── payment_methods.html
│   ├── login.html
│   ├── signup.html
│   ├── profile.html
│   ├── referral_dashboard.html
│   ├── dashboard.html
│   ├── transactions.html
│   ├── redeem.html
│   ├── admin_announcement.html
│   ├── admin_redemptions.html
│   └── leaderboard.html
└── /venv
```

## Customization
- Integrate real offerwall APIs (AdMantum, CPALead, etc.)
- Add more payout methods or custom rewards
- Enhance admin dashboard with more controls
- Add dark mode, QR invites, wallet logs, etc.

## License
MIT (or your preferred license) 