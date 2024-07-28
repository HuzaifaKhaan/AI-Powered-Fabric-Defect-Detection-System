from datetime import date, timedelta
from flask import render_template, Response,jsonify,request,session, redirect, url_for, current_app
from flask import Blueprint
import flask
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField,StringField,DecimalRangeField,IntegerRangeField
from wtforms.validators import InputRequired,NumberRange
from flask import request
from werkzeug.utils import secure_filename
from app.models import Defect,Fabric, FabricDefects, User
from app import db
from app.processing.videoProcess import video_detection
import os
import cv2
import base64
from werkzeug.security import generate_password_hash, check_password_hash

flag_check = False

def generate_frames(path_x=''):
    yolo_output = video_detection(path_x)
    for detection_ in yolo_output:
        if detection_ is None:
            break
        ref, buffer = cv2.imencode('.jpg', detection_)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
def login_required(func):
    def wrapper(*args, **kwargs):
        if 'logged_in' in session and session['logged_in']:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('Fabrico.login'))
    return wrapper
     
        
class UploadFileForm(FlaskForm):
    file = FileField("File",validators=[InputRequired()])
    submit = SubmitField("Run")

FabricoPrefix = Blueprint('Fabrico', __name__, url_prefix='/Fabrico',template_folder="templates")
UPLOAD_FOLDER = os.path.join('uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    


@FabricoPrefix.route('/')
def login():
    if 'logged_in' in session:
        return redirect(url_for('Fabrico.supervision'))
    title = "sign In"
    return render_template('login.html',title=title)

@FabricoPrefix.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect(url_for('Fabrico.login'))

@FabricoPrefix.route('/account')
def MyAccount():
    if 'logged_in' not in session:
        return redirect(url_for('Fabrico.login'))
    title = "MyAccount"
    return render_template('userAccount.html',title=title)

@FabricoPrefix.route('/fabrics')
def index():
    if 'logged_in' not in session:
        return redirect(url_for('Fabrico.login'))
    title = "Records"
    fabrics = Fabric.query.all()
    fabric_defects = {}
    userid = session['UserId']
    fabric_defects = {}
    for fabric in fabrics:
        defect_counts = {}
        fabric_defect_entries = FabricDefects.query.filter_by(fabric_id=fabric.fabric_id).all()
        for defect_entry in fabric_defect_entries:
            defect_counts[defect_entry.defect] = defect_counts.get(defect_entry.defect, 0) + 1
        fabric_defects[fabric.fabric_id] = defect_counts

    return render_template('fabricData.html', title=title, fabrics=fabrics, fabric_defects=fabric_defects,userid=userid)

@FabricoPrefix.route('/adminPortal')
def portal():
    if 'logged_in' not in session or session['UserId'] != 'Emp01':
        return redirect(url_for('Fabrico.login'))
    
    title = "Admin Portal"
    userid = session['UserId']
    users = User.query.filter(User.userid != 'Emp01').all()

    return render_template('portal.html', title=title, userid=userid, users=users)

@FabricoPrefix.route('/addPage')
def renderAddUser():
    title = "Add User"
    userid = session['UserId']
    return render_template('addUser.html', title=title,userid=userid)

@FabricoPrefix.route('/addUser', methods=['POST'])
def addUser():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return jsonify({'error': 'All fields are required'}), 400
        
        # Get the number of existing users
        num_users = User.query.count()
        
        # Generate the userid in the format "Emp{length of all users + 1}"
        userid = f"Emp{num_users + 1}"
        
        # Create the new user with the generated userid
        new_user = User(username=username, userid=userid)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('Fabrico.portal'))
    else:
        return jsonify({'error': 'Method not allowed'}), 405

@FabricoPrefix.route('/editUser/<int:userid>', methods=['GET', 'POST'])
def editUser(userid):
    user = User.query.filter_by(id=userid).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if request.method == 'POST':
        username = request.form.get('username')
        new_userid = request.form.get('userid')
        password = request.form.get('password')

        if not username:
            return jsonify({'error': 'Username and UserID are required'}), 400

        # Update user details
        user.username = username
        if password:
            # If password is provided, update it
            user.set_password(password)

        db.session.commit()
        return redirect(url_for('Fabrico.portal'))
    userid = session['UserId']
    return render_template('editUser.html', user=user,userid=userid)



@FabricoPrefix.route('/deleteUser/<int:userid>', methods=['POST', 'DELETE'])
def deleteUser(userid):
    user = User.query.filter_by(id=userid).first()
    if request.method in ['POST', 'DELETE']:
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('Fabrico.portal'))

@FabricoPrefix.route('/supervision',methods=['GET','POST'])
def supervision():
    if 'logged_in' not in session:
        return redirect(url_for('Fabrico.login'))
    title = "Supervision"
    form = UploadFileForm()
    userid = session['UserId']
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        session['video_path'] = file_path
    return render_template('supervision.html',title=title,form = form,userid=userid)

@FabricoPrefix.route('/video')
def video():
    if 'logged_in' not in session:
        return redirect(url_for('Fabrico.login'))
    global flag_check
    video_path = session.get('video_path', None)
    if video_path:
        defectDir = 'app/static/defects'
        if os.listdir(defectDir):
            for filename in os.listdir(defectDir):
                file_path = os.path.join(defectDir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"Error while deleting file: {e}")
        session.pop('video_path')  # Remove video_path from session after processing once
        flag_check = True
        return Response(generate_frames(video_path), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return "No video uploaded"
    
@FabricoPrefix.route('/LoginForm', methods=['POST'])
def loginForm():
    Userid = request.form.get('userid')
    Password = request.form.get('password')
    if not Userid or not Password:
        error_statement = 'All fields are required...'
        print('All fields are required.')
        return render_template('login.html', error_statement=error_statement,
                               username=Userid, password=Password)
    
    # Check if user exists
    user = User.query.filter_by(userid=Userid).first()
   
    if user and check_password_hash(user.password_hash, Password):
        print("Working")
        session['logged_in'] = True
        session['UserId'] = Userid
        title = "Supervision"
        form = UploadFileForm()
        return render_template('supervision.html', userid=Userid, title=title, form=form)
    else:
        error_statement = 'Invalid credentials. Please try again.'
        return render_template('login.html', error_statement=error_statement,
                               userid=Userid, password=Password)

 
@FabricoPrefix.route('/addFabric', methods=['GET', 'POST'])
def addFabric():
    if 'logged_in' not in session:
        return redirect(url_for('Fabrico.login'))
    title = "Fabric Report"
    userid = session['UserId']
    global flag_check
    if request.method == 'POST' and flag_check==True:
        defectDir = 'app/static/defects'  # Use forward slashes instead of backslashes
        total_defects = len(os.listdir(defectDir)) // 3
        fabrics = Fabric.query.all()
        fabricNum = len(fabrics)
        fabric_id = f"FAB{fabricNum + 1}"
        today_date = date.today()
        new_fabric = Fabric(
            fabric_id=fabric_id,
            total_defects=total_defects,
            date_added=today_date,
            userid=userid
        )
        db.session.add(new_fabric)
        db.session.commit()
        defect_types = {}
        defect_images = {}
        defect_coordinates = {}  # Store defect coordinates
        defect_meters = {} 
        with open("defect_times.txt", "r") as f:
                    for line in f:
                        parts = line.strip().split()
                        defect_type2 = parts[0]
                        meters = float(parts[1])  # Extract meters as float
                        coordinates = parts[2]  # Extract coordinates
                        defect_coordinates[defect_type2] = coordinates
                        defect_meters[defect_type2] = meters
                    print(defect_coordinates, defect_meters)
        for defect_type in ['Hole', 'Stain', 'Line', 'Knot']:
            count = len([f for f in os.listdir(defectDir) if f.startswith(defect_type)]) // 3
            if count > 0:
                defect_types[defect_type] = int(count)
                defect_images[defect_type] = []
                # Get the images for the defect type
                for i in range(1, count + 1):
                    original_image_name = f"{defect_type}_{i}.jpg"
                    gray_image_name = f"{defect_type}_{i}_Mask.jpg"
                    boundary_image_name = f"{defect_type}_{i}_boundary.jpg"
                     # Read images as binary data
                    with open(os.path.join(defectDir, original_image_name), 'rb') as f:
                        original_image_data = f.read()

                    with open(os.path.join(defectDir, gray_image_name), 'rb') as f:
                        gray_image_data = f.read()

                    with open(os.path.join(defectDir, boundary_image_name), 'rb') as f:
                        boundary_image_data = f.read()
                    defect_type2 = defect_type +"_"+str(i)
                    fabric_defect = FabricDefects(
                        defect=defect_type,
                        fabric_id=fabric_id,
                        defectimage=original_image_data,
                        defectGray=gray_image_data,
                        defectBoundary=boundary_image_data,
                        coordinates=defect_coordinates.get(defect_type2, ''),  # Store coordinates
                        meters=defect_meters.get(defect_type2, 0.0)  # Store meters
                    )
                    db.session.add(fabric_defect)
                    db.session.commit()
        defects = FabricDefects.query.filter_by(fabric_id=fabric_id).all()
    
        # List to store defect images, boundaries, and masks
        defect_data = []

        
        # Loop through each defect to get its images
        for defect in defects:
            if defect.defectimage:
                defect_image_base64 = base64.b64encode(defect.defectimage).decode('utf-8')
            
            if defect.defectBoundary:
                defect_boundary_base64 = base64.b64encode(defect.defectBoundary).decode('utf-8')
            
            if defect.defectGray:
                defect_mask_base64 = base64.b64encode(defect.defectGray).decode('utf-8')
            
            defect_data.append({
                'image': defect_image_base64,
                'boundary': defect_boundary_base64,
                'mask': defect_mask_base64,
                'coordinates': defect.coordinates,
                'defect_type': defect.defect,
                'meters': defect.meters,
                # Add other fields here as needed
            })
        return render_template('report.html', fabric_id=fabric_id, total_defects=total_defects,
                               date_added=today_date,defect_data = defect_data,
                               title=title, userid=userid)
    else:
        title = "Supervision"
        form = UploadFileForm()
        if form.validate_on_submit():
            file = form.file.data
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            session['video_path'] = file_path
            userid = session['UserId']
        flag_check = False
        return render_template('supervision.html',title=title,form = form,userid=userid)

@FabricoPrefix.route('/fabricDetail/<fabric_id>')
def fabricDetail(fabric_id):
    fabric = Fabric.query.filter_by(fabric_id=fabric_id).first()
    defects = FabricDefects.query.filter_by(fabric_id=fabric_id).all()
    
    # List to store defect data
    defect_data = []
    
    # Loop through each defect to get its details
    for defect in defects:
        defect_image_base64 = defect_boundary_base64 = defect_mask_base64 = None
        if defect.defectimage:
            defect_image_base64 = base64.b64encode(defect.defectimage).decode('utf-8')
        
        if defect.defectBoundary:
            defect_boundary_base64 = base64.b64encode(defect.defectBoundary).decode('utf-8')
        
        if defect.defectGray:
            defect_mask_base64 = base64.b64encode(defect.defectGray).decode('utf-8')
        
        defect_data.append({
            'image': defect_image_base64,
            'boundary': defect_boundary_base64,
            'mask': defect_mask_base64,
            'coordinates': defect.coordinates,
            'defect_type': defect.defect,
            'meters': defect.meters,
            # Add other fields here as needed
        })
    
    today_date = fabric.date_added.strftime('%d-%m-%Y')
    title = "Fabric Details"
    userid = session.get('UserId', 'Unknown')
    
    return render_template('report.html', fabric_id=fabric.fabric_id, defect_data=defect_data,
                           total_defects=len(defects), date_added=today_date,
                           title=title, userid=userid)

@FabricoPrefix.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('Fabrico.login'))
    title = "Dashboard"
    userid = session['UserId']
     # Get all fabrics
    fabrics = Fabric.query.all()

    # Count defected and non-defected fabrics for all fabrics
    defected_count = sum(1 for fabric in fabrics if fabric.total_defects)
    non_defected_count = len(fabrics) - defected_count
    
    # Get today's date
    today_date = date.today()
    # Get yesterday's date
    yesterday_date = today_date - timedelta(days=1)

    # Query fabrics added yesterday
    fabrics_yesterday = Fabric.query.filter(db.func.date(Fabric.date_added) == yesterday_date).all()
    # Query fabrics added today
    fabrics_today = Fabric.query.filter(db.func.date(Fabric.date_added) == today_date).all()

    # Calculate defected and non-defected counts for today
    defected_count_today = sum(1 for fabric in fabrics_today if fabric.total_defects)
    non_defected_count_today = len(fabrics_today) - defected_count_today
    defected_count_yesterday = sum(1 for fabric in fabrics_yesterday if fabric.total_defects)
    defect_counts = {}
    for defect_type in ['Hole', 'Stain', 'Line', 'Knot']:
        count = db.session.query(db.func.count(FabricDefects.id)).filter(FabricDefects.defect == defect_type).scalar()
        defect_counts[defect_type] = count

    # Get the count of "hole" defect, default to 0 if not found
    hole_count = defect_counts.get("Hole", 0)
    stain_count = defect_counts.get("Stain", 0)
    line_count = defect_counts.get("Line", 0)
    knot_count = defect_counts.get("Knot", 0)

    return render_template('dashboard.html', title=title, defected_count=defected_count, non_defected_count=non_defected_count, 
                           defected_count_today=defected_count_today, non_defected_count_today=non_defected_count_today,
                           hole_count=hole_count, stain_count=stain_count, line_count=line_count, knot_count=knot_count,defected_count_yesterday=defected_count_yesterday,userid=userid)
