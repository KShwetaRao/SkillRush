from flask import Flask, render_template, request, redirect, url_for, flash
from extensions import db, login_manager
from flask_login import login_user, logout_user, login_required, current_user
import os
from models import User, Transaction, DailyCheckin, Announcement, Referral
from datetime import date
from sqlalchemy import func

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rewards.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Register blueprints (to be created)
# from auth import auth as auth_blueprint
# app.register_blueprint(auth_blueprint)
# from dashboard import dashboard as dashboard_blueprint
# app.register_blueprint(dashboard_blueprint)

REWARDS = {
    'paypal_1': {'name': 'PayPal', 'amount': '$1', 'points': 1000},
    'paypal_5': {'name': 'PayPal', 'amount': '$5', 'points': 4500},
    'paytm_100': {'name': 'PayTM', 'amount': '₹100', 'points': 1000},
    'amazon_2_5': {'name': 'Amazon', 'amount': '$2.5', 'points': 3000},
    'googleplay_10': {'name': 'Google Play', 'amount': '$10', 'points': 9000},
}

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')

@app.route('/payment-methods')
def payment_methods():
    return render_template('payment_methods.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form['fullname']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        # Check for existing user
        if User.query.filter((User.email == email) | (User.username == username)).first():
            flash('Email or username already exists.', 'danger')
            return render_template('signup.html')
        user = User(full_name=full_name, email=email, username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/referral-dashboard')
@login_required
def referral_dashboard():
    referred_count = len(current_user.referrals)
    referral_points = referred_count * 100  # Example: 100 points per referral
    referral_link = url_for('signup', _external=True) + f'?ref={current_user.referral_code}'
    return render_template('referral_dashboard.html',
                           referred_count=referred_count,
                           referral_points=referral_points,
                           referral_link=referral_link)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.full_name = request.form['full_name']
        current_user.email = request.form['email']
        current_user.phone = request.form['phone']
        db.session.commit()
        flash('Profile updated successfully.', 'success')
    referral_link = url_for('signup', _external=True) + f'?ref={current_user.referral_code}'
    return render_template('profile.html', user=current_user, referral_link=referral_link)

@app.route('/dashboard')
@login_required
def dashboard():
    user = current_user
    total_earned = user.points  # Placeholder, can sum all earned points
    redeemed_points = 0  # Placeholder, can sum redeemed transactions
    referred_count = len(user.referrals)
    announcement_obj = Announcement.query.order_by(Announcement.id.desc()).first()
    announcement = announcement_obj.message if announcement_obj else None
    return render_template('dashboard.html', user=user, total_earned=total_earned, redeemed_points=redeemed_points, referred_count=referred_count, announcement=announcement)

@app.route('/transactions')
@login_required
def transactions():
    q = request.args.get('q', '')
    tx_type = request.args.get('type', '')
    status = request.args.get('status', '')
    query = Transaction.query.filter_by(user_id=current_user.id)
    if q:
        query = query.filter(Transaction.name.ilike(f'%{q}%'))
    if tx_type:
        query = query.filter_by(type=tx_type)
    if status:
        query = query.filter_by(status=status)
    txs = query.order_by(Transaction.date.desc()).all()
    return render_template('transactions.html', transactions=txs)

@app.route('/redeem', methods=['GET', 'POST'])
@login_required
def redeem():
    if request.method == 'POST':
        reward_key = request.form.get('reward')
        reward = REWARDS.get(reward_key)
        if not reward:
            flash('Invalid reward selected.', 'danger')
            return redirect(url_for('redeem'))
        if current_user.points < reward['points']:
            flash('Not enough points to redeem this reward.', 'danger')
            return redirect(url_for('redeem'))
        # Deduct points and create transaction
        current_user.points -= reward['points']
        tx = Transaction(
            name=f"{reward['name']} {reward['amount']}",
            points=reward['points'],
            user_id=current_user.id,
            type='redeem',
            status='pending'
        )
        db.session.add(tx)
        db.session.commit()
        flash('Redemption request submitted! Processed weekly.', 'success')
        return redirect(url_for('transactions'))
    return render_template('redeem.html')

@app.route('/daily-checkin', methods=['POST'])
@login_required
def daily_checkin():
    today = date.today()
    already_checked = DailyCheckin.query.filter_by(user_id=current_user.id, date=today).first()
    if already_checked:
        flash('You have already checked in today!', 'info')
    else:
        current_user.points += 25
        db.session.add(DailyCheckin(user_id=current_user.id, date=today))
        db.session.commit()
        flash('Daily check-in successful! You earned 25 points.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/admin/announcement', methods=['GET', 'POST'])
@login_required
def admin_announcement():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    announcement = Announcement.query.order_by(Announcement.id.desc()).first()
    if request.method == 'POST':
        message = request.form['message']
        if announcement:
            announcement.message = message
        else:
            announcement = Announcement(message=message)
            db.session.add(announcement)
        db.session.commit()
        flash('Announcement updated.', 'success')
        return redirect(url_for('admin_announcement'))
    return render_template('admin_announcement.html', announcement=announcement)

@app.route('/admin/redemptions', methods=['GET', 'POST'])
@login_required
def admin_redemptions():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        tx_id = request.form.get('tx_id')
        action = request.form.get('action')
        tx = Transaction.query.get(tx_id)
        if tx and tx.type == 'redeem' and tx.status == 'pending':
            if action == 'approve':
                tx.status = 'approved'
                flash('Redemption approved.', 'success')
            elif action == 'reject':
                tx.status = 'rejected'
                # Optionally refund points
                user = User.query.get(tx.user_id)
                if user:
                    user.points += tx.points
                flash('Redemption rejected and points refunded.', 'warning')
            db.session.commit()
    redemptions = Transaction.query.filter_by(type='redeem').order_by(Transaction.date.desc()).all()
    return render_template('admin_redemptions.html', redemptions=redemptions)

@app.route('/leaderboard')
def leaderboard():
    # Top 10 by points
    top_points = User.query.order_by(User.points.desc()).limit(10).all()
    # Top 10 by referrals (annotate with referral_count)
    referral_counts = db.session.query(User, func.count(Referral.id).label('referral_count'))\
        .outerjoin(Referral, Referral.referrer_id == User.id)\
        .group_by(User.id)\
        .order_by(func.count(Referral.id).desc())\
        .limit(10).all()
    # Unpack users and set referral_count attribute
    top_referrals = []
    for user, count in referral_counts:
        user.referral_count = count
        top_referrals.append(user)
    return render_template('leaderboard.html', top_points=top_points, top_referrals=top_referrals)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True) 