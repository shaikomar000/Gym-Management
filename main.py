import os, re, secrets, smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta, date
from decimal import Decimal
from functools import wraps
from flask import Flask, render_template, redirect, request, session, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import formula

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'CHANGE-ME-USE-A-RANDOM-SECRET-KEY'),
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/gym'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax'
)
db = SQLAlchemy(app)
ADMIN_EMAIL = os.environ.get('IRONPATH_ADMIN_EMAIL', 'shaikomar000@gmail.com').strip().lower()

class Account(db.Model):
    __tablename__ = 'account'
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(80), nullable=False)
    email=db.Column(db.String(100), unique=True, nullable=False)
    phone_num=db.Column(db.String(12), nullable=False)
    age=db.Column(db.Integer, nullable=False)
    password_hash=db.Column(db.String(255), nullable=False)
    is_verified=db.Column(db.Boolean, nullable=False, default=False)
    role=db.Column(db.String(20), nullable=False, default='member')
    created_at=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Workout(db.Model):
    __tablename__='workouts'
    sno=db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer, nullable=True, index=True)
    part=db.Column(db.Enum('chest','back','shoulders','biceps','triceps','abs','legs'), nullable=False)
    types=db.Column(db.Enum('compound','isolate'), nullable=False)
    sets=db.Column(db.Integer, nullable=False); reps=db.Column(db.Integer, nullable=False)
    weight=db.Column(db.Numeric(6,2), nullable=False); date=db.Column(db.DateTime, nullable=False)
    volume=db.Column(db.Numeric(10,2), nullable=False)

class Cardio(db.Model):
    __tablename__='cardio'
    sno=db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer, nullable=True, index=True)
    activity=db.Column(db.Enum('Cycling','Walking','Running','Stair Climbing','Elliptical','Swimming','Jump Rope','Rowing'), nullable=False)
    duration=db.Column(db.Integer, nullable=False)
    intensity=db.Column(db.Enum('light','moderate','vigorous'), nullable=False)
    body_weight=db.Column(db.Numeric(10,2), nullable=False)
    date=db.Column(db.DateTime, nullable=False)
    calories_burned=db.Column(db.Numeric(10,2), nullable=False)

class Attendance(db.Model):
    __tablename__='attendance'
    sno=db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer, nullable=False, index=True)
    target=db.Column(db.Integer, nullable=False, default=3)
    day=db.Column(db.Enum('monday','tuesday','wednesday','thursday','friday','saturday','sunday'), nullable=False)
    percentage=db.Column(db.Numeric(10,2), nullable=False, default=0)
    date=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    approved=db.Column(db.Integer, nullable=False, default=0) # 0 pending, 1 approved, 2 rejected
    admin_id=db.Column(db.Integer, nullable=True)

class Contact(db.Model):
    __tablename__='contacts'
    sno=db.Column(db.Integer, primary_key=True); name=db.Column(db.String(80), nullable=False)
    email=db.Column(db.String(100), nullable=False); msg=db.Column(db.Text, nullable=False)
    date=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Review(db.Model):
    __tablename__='reviews'
    sno=db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer, nullable=True, index=True)
    name=db.Column(db.String(20), nullable=False)
    star=db.Column(db.Integer, nullable=False)
    review=db.Column(db.Text, nullable=False)
    date=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

def current_user():
    uid=session.get('user_id')
    return db.session.get(Account, uid) if uid else None

def login_required(fn):
    @wraps(fn)
    def wrapped(*a, **kw):
        if not current_user():
            if request.path.startswith('/api/'): return jsonify(error='Please log in.'), 401
            return redirect(url_for('login', next=request.path))
        return fn(*a, **kw)
    return wrapped

def admin_required(fn):
    @wraps(fn)
    def wrapped(*a, **kw):
        user=current_user()
        if not user or user.email.lower()!=ADMIN_EMAIL:
            if request.path.startswith('/api/'): return jsonify(error='Administrator access required.'), 403
            return redirect(url_for('login'))
        return fn(*a, **kw)
    return wrapped

def send_otp(to_email, otp):
    host=os.getenv('SMTP_HOST','smtp.gmail.com'); port=int(os.getenv('SMTP_PORT','465'))
    user=os.getenv('SMTP_USER'); password=os.getenv('SMTP_PASSWORD'); sender=os.getenv('SMTP_FROM',user or '')
    if not user or not password: raise RuntimeError('SMTP_USER and SMTP_PASSWORD environment variables are required.')
    msg=EmailMessage(); msg['Subject']='Your IronPath verification code'; msg['From']=sender; msg['To']=to_email
    msg.set_content(f'Your IronPath verification code is {otp}. It expires in 5 minutes. If you did not request this, ignore this email.')
    with smtplib.SMTP_SSL(host,port,timeout=20) as smtp: smtp.login(user,password); smtp.send_message(msg)

def password_ok(p):
    if len(p)<8 or len(p)>128: return False,'Password must be 8–128 characters.'
    if not re.search(r'[A-Z]',p) or not re.search(r'[a-z]',p) or not re.search(r'\d',p) or not re.search(r'[^A-Za-z0-9]',p):
        return False,'Use uppercase, lowercase, a number and a special character.'
    return True,''

@app.context_processor
def inject_auth():
    u=current_user()
    return {'logged_in_user':u, 'is_admin_user':bool(u and u.email.lower()==ADMIN_EMAIL)}

@app.route('/')
def home(): return render_template('index.html')
@app.route('/about')
def about(): return redirect('/#about-section')
@app.route('/branches')
def branches(): return render_template('branches.html')
@app.route('/coaches')
def coaches(): return render_template('coaches.html')
@app.route('/reviews')
def reviews(): return render_template('reviews.html')

@app.route('/api/reviews', methods=['GET', 'POST'])
def reviews_api():
    if request.method == 'GET':
        rows = Review.query.order_by(Review.date.desc(), Review.sno.desc()).limit(100).all()
        return jsonify(reviews=[{
            'id': r.sno, 'name': r.name, 'star': r.star, 'review': r.review,
            'date': r.date.strftime('%d %b %Y') if r.date else ''
        } for r in rows])

    user = current_user()
    if not user:
        return jsonify(error='Please log in with your IronPath account to post a review.'), 401
    data = request.get_json(silent=True) or request.form
    try:
        stars = int(data.get('star', data.get('rating', 0)))
    except (TypeError, ValueError):
        stars = 0
    review_text = str(data.get('review', '')).strip()
    if stars < 1 or stars > 5:
        return jsonify(error='Choose a rating from 1 to 5 stars.'), 400
    if not review_text or len(review_text) > 2000:
        return jsonify(error='Write a review between 1 and 2000 characters.'), 400
    row = Review(user_id=user.id, name=user.name[:20], star=stars, review=review_text)
    db.session.add(row)
    db.session.commit()
    return jsonify(message='Your review has been published.', review={
        'id': row.sno, 'name': row.name, 'star': row.star, 'review': row.review,
        'date': row.date.strftime('%d %b %Y')
    }), 201
@app.route('/membership')
def membership_removed():
    # Backward-compatible redirect for old bookmarks; membership sales are disabled.
    return redirect(url_for('signup'))
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form.get('email','').strip().lower(); password=request.form.get('password','')
        user=Account.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash,password):
            flash('Email or password is incorrect.','error')
        elif not user.is_verified: flash('Please verify your email before logging in.','error')
        else:
            session.clear(); session['user_id']=user.id
            return redirect('/admin' if email==ADMIN_EMAIL else request.args.get('next') or '/attendance')
    return render_template('login.html')
@app.route('/logout', methods=['GET','POST'])
def logout(): session.clear(); return redirect('/')
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method=='POST':
        name=request.form.get('name','').strip(); email=request.form.get('email','').strip().lower()
        phone=(request.form.get('phone') or request.form.get('phone_num') or '').strip()
        age=request.form.get('age','').strip(); password=request.form.get('password',''); confirm=request.form.get('confirm_password') or password
        ok,msg=password_ok(password)
        if not name or not email or not re.fullmatch(r'\d{10,12}',phone) or not age.isdigit() or not 13<=int(age)<=100:
            flash('Please enter valid details. Phone must contain 10–12 digits.','error')
        elif not ok: flash(msg,'error')
        elif password!=confirm: flash('Passwords do not match.','error')
        elif Account.query.filter_by(email=email).first(): flash('An account with this email already exists.','error')
        else:
            otp=f'{secrets.randbelow(10000):04d}'
            session['signup_pending']={'name':name,'email':email,'phone':phone,'age':int(age),'password_hash':generate_password_hash(password),'otp_hash':generate_password_hash(otp),'expires':(datetime.utcnow()+timedelta(minutes=5)).isoformat(),'attempts':0}
            try: send_otp(email,otp)
            except Exception as e:
                session.pop('signup_pending',None); app.logger.exception('OTP send failed'); flash(f'Could not send verification email: {e}','error')
            else: return redirect('/verify-otp')
    return render_template('signup.html')
@app.route('/verify-otp', methods=['GET','POST'])
def verify_otp():
    pending=session.get('signup_pending')
    if not pending: return redirect('/signup')
    if request.method=='POST':
        otp=request.form.get('otp','').strip(); pending['attempts']=int(pending.get('attempts',0))+1
        if datetime.fromisoformat(pending['expires'])<datetime.utcnow(): session.pop('signup_pending',None); flash('OTP expired. Please sign up again.','error'); return redirect('/signup')
        if pending['attempts']>5: session.pop('signup_pending',None); flash('Too many attempts. Please sign up again.','error'); return redirect('/signup')
        if not check_password_hash(pending['otp_hash'],otp): session['signup_pending']=pending; flash('Incorrect OTP.','error')
        else:
            user=Account(name=pending['name'],email=pending['email'],phone_num=pending['phone'],age=pending['age'],password_hash=pending['password_hash'],is_verified=True)
            db.session.add(user); db.session.commit(); session.pop('signup_pending',None); session.clear(); session['user_id']=user.id
            return redirect('/admin' if user.email==ADMIN_EMAIL else '/attendance')
    return render_template('verify_otp.html')
@app.route('/forgot-password',methods=['GET','POST'])
def forgot_password():
    if request.method=='POST':
        email=request.form.get('email','').strip().lower(); user=Account.query.filter_by(email=email,is_verified=True).first()
        if user:
            otp=f'{secrets.randbelow(10000):04d}'; session['reset_pending']={'uid':user.id,'hash':generate_password_hash(otp),'expires':(datetime.utcnow()+timedelta(minutes=5)).isoformat(),'attempts':0}
            try: send_otp(email,otp)
            except Exception: app.logger.exception('Reset OTP failed')
        flash('If the verified account exists, a reset code has been sent.','success'); return redirect('/reset-password')
    return render_template('forgot_password.html')
@app.route('/reset-password',methods=['GET','POST'])
def reset_password():
    p=session.get('reset_pending')
    if not p: return redirect('/forgot-password')
    if request.method=='POST':
        otp=request.form.get('otp',''); pw=request.form.get('password',''); confirm=request.form.get('confirm_password','')
        p['attempts']+=1
        if p['attempts']>5 or datetime.fromisoformat(p['expires'])<datetime.utcnow(): session.pop('reset_pending',None); flash('Code expired or too many attempts.','error'); return redirect('/forgot-password')
        if not check_password_hash(p['hash'],otp): session['reset_pending']=p; flash('Incorrect code.','error')
        else:
            ok,msg=password_ok(pw)
            if not ok or pw!=confirm: session['reset_pending']=p; flash(msg or 'Passwords do not match.','error')
            else:
                user=db.session.get(Account,p['uid']); user.password_hash=generate_password_hash(pw); db.session.commit(); session.pop('reset_pending',None); flash('Password updated. Please log in.','success'); return redirect('/login')
    return render_template('reset_password.html')
@app.route('/attendance')
@login_required
def attendance(): return render_template('attendance.html')
@app.route('/api/attendance',methods=['GET','POST'])
@login_required
def attendance_api():
    user=current_user()
    if request.method=='POST':
        data=request.get_json(silent=True) or request.form
        try: target=max(1,min(7,int(data.get('target',3))))
        except: return jsonify(error='Invalid weekly target.'),400
        day=datetime.utcnow().strftime('%A').lower(); today=date.today()
        exists=Attendance.query.filter(Attendance.user_id==user.id,db.func.date(Attendance.date)==today).first()
        if exists: return jsonify(error='You already submitted an attendance request today.'),409
        row=Attendance(user_id=user.id,target=target,day=day,percentage=0,date=datetime.utcnow(),approved=0,admin_id=None)
        db.session.add(row); db.session.commit(); return jsonify(message='Attendance request sent to admin.',request_id=row.sno),201
    rows=Attendance.query.filter_by(user_id=user.id).order_by(Attendance.date.desc()).limit(60).all()
    approved=Attendance.query.filter_by(user_id=user.id,approved=1).filter(Attendance.date>=datetime.utcnow()-timedelta(days=7)).count()
    target=rows[0].target if rows else 3
    return jsonify(target=target,approved_this_week=approved,percentage=min(100,round(approved/max(target,1)*100)),requests=[{'id':r.sno,'date':r.date.isoformat(),'day':r.day,'status':{0:'Pending',1:'Approved',2:'Rejected'}.get(r.approved,'Pending')} for r in rows])
@app.route('/admin')
@admin_required
def admin(): return render_template('admin.html')
@app.route('/api/admin/attendance')
@admin_required
def admin_attendance_api():
    rows=Attendance.query.order_by(Attendance.date.desc()).limit(300).all()
    return jsonify(requests=[{'id':r.sno,'name':(db.session.get(Account,r.user_id).name if db.session.get(Account,r.user_id) else 'Unknown'),'email':(db.session.get(Account,r.user_id).email if db.session.get(Account,r.user_id) else ''),'date':r.date.strftime('%d %b %Y %I:%M %p'),'status':{0:'Pending',1:'Approved',2:'Rejected'}.get(r.approved,'Pending')} for r in rows])
@app.route('/api/admin/attendance/<int:rid>',methods=['POST'])
@admin_required
def admin_decide_attendance(rid):
    data=request.get_json(silent=True) or {}; decision=data.get('decision')
    if decision not in ('approve','reject'): return jsonify(error='Invalid decision.'),400
    row=db.session.get(Attendance,rid)
    if not row: return jsonify(error='Request not found.'),404
    row.approved=1 if decision=='approve' else 2; row.admin_id=current_user().id; db.session.commit()
    return jsonify(message=f'Request {decision}d.')
@app.route('/workouts',methods=['GET','POST'])
@login_required
def workouts():
    if request.method=='POST':
        f=request.form
        try:
            part=f.get('part'); typ=f.get('types'); sets=int(f.get('sets') or f.get('sets ') or 0); reps=int(f.get('reps') or 0); weight=Decimal(f.get('weight') or '0')
            dt=datetime.strptime(f.get('date') or date.today().isoformat(),'%Y-%m-%d')
            if part not in ('chest','back','shoulders','biceps','triceps','abs','legs') or typ not in ('compound','isolate') or not 1<=sets<=100 or not 1<=reps<=1000 or weight<0: raise ValueError
        except Exception: flash('Please check workout details.','error'); return redirect('/workouts')
        db.session.add(Workout(user_id=current_user().id,part=part,types=typ,sets=sets,reps=reps,weight=weight,date=dt,volume=Decimal(sets*reps)*weight)); db.session.commit(); flash('Workout saved.','success'); return redirect('/workouts')
    return render_template('workouts.html')
@app.route('/api/workouts')
@login_required
def workout_data():
    rows=Workout.query.filter_by(user_id=current_user().id).order_by(Workout.date.desc()).limit(100).all()
    return jsonify(records=[{'date':r.date.strftime('%Y-%m-%d'),'part':r.part,'type':r.types,'sets':r.sets,'reps':r.reps,'weight':float(r.weight),'volume':float(r.volume)} for r in rows])
@app.route('/cardio',methods=['GET','POST'])
@login_required
def cardio():
    if request.method=='POST':
        f=request.form
        try:
            activity=f.get('activity'); intensity=f.get('intensity'); duration=int(f.get('duration')); weight=Decimal(f.get('body_weight'))
            dt=datetime.strptime(f.get('date') or date.today().isoformat(),'%Y-%m-%d')
            met=formula.met_values[activity][intensity]
            if not 1<=duration<=600 or not 20<=weight<=300: raise ValueError
        except Exception: flash('Please check cardio details.','error'); return redirect('/cardio')
        calories=Decimal(str(met*3.5*float(weight)*duration/200)).quantize(Decimal('.01'))
        db.session.add(Cardio(user_id=current_user().id,activity=activity,duration=duration,intensity=intensity,body_weight=weight,date=dt,calories_burned=calories)); db.session.commit(); flash('Cardio session saved.','success'); return redirect('/cardio')
    return render_template('cardio.html')
@app.route('/api/cardio')
@login_required
def cardio_data():
    rows=Cardio.query.filter_by(user_id=current_user().id).order_by(Cardio.date.desc()).limit(100).all()
    return jsonify(records=[{'date':r.date.strftime('%Y-%m-%d'),'activity':r.activity,'duration':r.duration,'weight':float(r.body_weight),'calories':float(r.calories_burned)} for r in rows])
@app.route('/contact',methods=['GET','POST'])
def contact():
    if request.method=='POST':
        db.session.add(Contact(name=request.form.get('name','').strip(),email=request.form.get('email','').strip(),msg=request.form.get('message','').strip())); db.session.commit(); flash('Message sent.','success')
    return render_template('contact.html')

if __name__=='__main__': app.run(debug=True)
