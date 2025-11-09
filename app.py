from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import boto3
from botocore.exceptions import ClientError
import os
from datetime import datetime
import uuid

app = Flask(__name__) 
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost/cloudcampus') commented out for sql lite the line for sql lite is below
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///cloudcampus.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# AWS S3 Configuration
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_BUCKET_NAME = os.environ.get('AWS_BUCKET_NAME')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
) if AWS_ACCESS_KEY else None

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx'}

# Database Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.relationship('Note', backref='uploader', lazy=True, cascade='all, delete-orphan')

class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    subject = db.Column(db.String(100), nullable=False)
    file_name = db.Column(db.String(200), nullable=False)
    file_key = db.Column(db.String(300), nullable=False)  # S3 key
    file_type = db.Column(db.String(10), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    downloads = db.Column(db.Integer, default=0)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_to_s3(file, filename):
    """Upload file to S3 bucket"""
    if not s3_client:
        return None
    
    try:
        file_key = f"notes/{uuid.uuid4()}_{filename}"
        s3_client.upload_fileobj(
            file,
            AWS_BUCKET_NAME,
            file_key,
            ExtraArgs={'ContentType': file.content_type}
        )
        return file_key
    except ClientError as e:
        print(f"Error uploading to S3: {e}")
        return None

def generate_presigned_url(file_key, expiration=3600):
    """Generate presigned URL for downloading"""
    if not s3_client:
        return None
    
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': AWS_BUCKET_NAME, 'Key': file_key},
            ExpiresIn=expiration
        )
        return url
    except ClientError as e:
        print(f"Error generating presigned URL: {e}")
        return None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            verified=True  # Auto-verify for demo purposes
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            if not user.verified:
                flash('Your account is not verified yet', 'warning')
                return redirect(url_for('login'))
            
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_notes = Note.query.filter_by(uploaded_by=current_user.id).order_by(Note.uploaded_at.desc()).all()
    return render_template('dashboard.html', notes=user_notes)

@app.route('/browse')
@login_required
def browse():
    search = request.args.get('search', '')
    subject = request.args.get('subject', '')
    
    query = Note.query
    
    if search:
        query = query.filter(Note.title.ilike(f'%{search}%'))
    if subject:
        query = query.filter_by(subject=subject)
    
    notes = query.order_by(Note.uploaded_at.desc()).all()
    subjects = db.session.query(Note.subject).distinct().all()
    subjects = [s[0] for s in subjects]
    
    return render_template('browse.html', notes=notes, subjects=subjects)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if not current_user.verified:
            flash('Only verified users can upload notes', 'danger')
            return redirect(url_for('dashboard'))
        
        title = request.form.get('title')
        description = request.form.get('description')
        subject = request.form.get('subject')
        file = request.files.get('file')
        
        if not file or file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('upload'))
        
        if not allowed_file(file.filename):
            flash('Invalid file type. Only PDF, DOC, DOCX, PPT, PPTX allowed', 'danger')
            return redirect(url_for('upload'))
        
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        
        # Upload to S3
        file_key = upload_to_s3(file, filename)
        
        if not file_key:
            flash('Error uploading file. Please try again.', 'danger')
            return redirect(url_for('upload'))
        
        note = Note(
            title=title,
            description=description,
            subject=subject,
            file_name=filename,
            file_key=file_key,
            file_type=file_ext,
            uploaded_by=current_user.id
        )
        
        db.session.add(note)
        db.session.commit()
        
        flash('Note uploaded successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('upload.html')

@app.route('/download/<int:note_id>')
@login_required
def download(note_id):
    note = Note.query.get_or_404(note_id)
    
    # Generate presigned URL
    download_url = generate_presigned_url(note.file_key)
    
    if not download_url:
        flash('Error generating download link', 'danger')
        return redirect(url_for('browse'))
    
    # Increment download count
    note.downloads += 1
    db.session.commit()
    
    return redirect(download_url)

@app.route('/delete/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    
    if note.uploaded_by != current_user.id:
        flash('You can only delete your own notes', 'danger')
        return redirect(url_for('dashboard'))
    
    # Delete from S3
    if s3_client:
        try:
            s3_client.delete_object(Bucket=AWS_BUCKET_NAME, Key=note.file_key)
        except ClientError as e:
            print(f"Error deleting from S3: {e}")
    
    db.session.delete(note)
    db.session.commit()
    
    flash('Note deleted successfully', 'success')
    return redirect(url_for('dashboard'))

@app.route('/profile')
@login_required
def profile():
    total_uploads = Note.query.filter_by(uploaded_by=current_user.id).count()
    total_downloads = db.session.query(db.func.sum(Note.downloads)).filter_by(uploaded_by=current_user.id).scalar() or 0
    return render_template('profile.html', total_uploads=total_uploads, total_downloads=total_downloads)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

