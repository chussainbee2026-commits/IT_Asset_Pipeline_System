from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file
)

from flask_sqlalchemy import SQLAlchemy

from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from datetime import datetime

from pytz import timezone
import pandas as pd
import os

# ================= APP =================

app = Flask(__name__)

# ================= CONFIG =================

app.config['SECRET_KEY'] = 'secretkey'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assets.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ================= LOGIN MANAGER =================

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = 'login'

# ================= USER MODEL =================

class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

# ================= ASSET MODEL =================

class Asset(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    asset_name = db.Column(
        db.String(100),
        nullable=False
    )

    asset_type = db.Column(
        db.String(100),
        nullable=False
    )

    employee = db.Column(
        db.String(100),
        nullable=False
    )

    # AUTO DATE & TIME

    assigned_date = db.Column(
        db.DateTime,
        default=lambda: datetime.now(
            timezone('Asia/Kolkata')
        )
    )

    status = db.Column(
        db.String(100),
        nullable=False
    )

    reason = db.Column(
        db.String(300)
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(
            timezone('Asia/Kolkata')
        )
    )

# ================= LOAD USER =================

@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))

# ================= LOGIN =================

@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form[
            'username'
        ]

        password = request.form[
            'password'
        ]

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            flash(
                'Login Successful',
                'success'
            )

            return redirect(
                url_for('dashboard')
            )

        flash(
            'Invalid Username or Password',
            'danger'
        )

    return render_template(
        'login.html'
    )

# ================= REGISTER =================

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form[
            'username'
        ]

        password = request.form[
            'password'
        ]

        confirm_password = request.form[
            'confirm_password'
        ]

        if password != confirm_password:

            flash(
                'Passwords do not match',
                'danger'
            )

            return redirect(
                url_for('register')
            )

        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:

            flash(
                'Username already exists',
                'warning'
            )

            return redirect(
                url_for('register')
            )

        hashed_password = generate_password_hash(
            password
        )

        new_user = User(

            username=username,

            password=hashed_password

        )

        db.session.add(new_user)

        db.session.commit()

        flash(
            'Account Created Successfully',
            'success'
        )

        return redirect(
            url_for('login')
        )

    return render_template(
        'register.html'
    )

# ================= DASHBOARD =================

@app.route('/dashboard')
@login_required
def dashboard():

    search = request.args.get('search')

    if search:

        assets = Asset.query.filter(
            Asset.user_id == current_user.id,
            Asset.employee.contains(search)
        ).all()

    else:

        assets = Asset.query.filter_by(
            user_id=current_user.id
        ).order_by(
            Asset.created_at.desc()
        ).all()

    total_assets = Asset.query.filter_by(
        user_id=current_user.id
    ).count()

    active_assets = Asset.query.filter_by(
        user_id=current_user.id,
        status='Active'
    ).count()

    repair_assets = Asset.query.filter_by(
        user_id=current_user.id,
        status='Repair'
    ).count()

    retired_assets = Asset.query.filter_by(
        user_id=current_user.id,
        status='Retired'
    ).count()

    return render_template(

        'dashboard.html',

        assets=assets,

        total_assets=total_assets,

        active_assets=active_assets,

        repair_assets=repair_assets,

        retired_assets=retired_assets,

        username=current_user.username
    )

# ================= ADD ASSET =================

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_asset():

    if request.method == 'POST':

        asset = Asset(

            user_id=current_user.id,

            asset_name=request.form[
                'asset_name'
            ],

            asset_type=request.form[
                'asset_type'
            ],

            employee=request.form[
                'employee'
            ],

            status=request.form[
                'status'
            ],

            reason=request.form[
                'reason'
            ]
        )

        db.session.add(asset)

        db.session.commit()

        flash(
            'Asset Added Successfully',
            'success'
        )

        return redirect(
            url_for('dashboard')
        )

    return render_template(
        'add_asset.html'
    )

# ================= EDIT ASSET =================

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_asset(id):

    asset = Asset.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    if request.method == 'POST':

        asset.asset_name = request.form[
            'asset_name'
        ]

        asset.asset_type = request.form[
            'asset_type'
        ]

        asset.employee = request.form[
            'employee'
        ]

        asset.status = request.form[
            'status'
        ]

        asset.reason = request.form[
            'reason'
        ]

        # AUTO UPDATE CURRENT DATE & TIME

        asset.assigned_date = datetime.now(
            timezone('Asia/Kolkata')
        )

        db.session.commit()

        flash(
            'Asset Updated Successfully',
            'info'
        )

        return redirect(
            url_for('dashboard')
        )

    return render_template(
        'edit_asset.html',
        asset=asset
    )

# ================= DELETE =================

@app.route('/delete/<int:id>')
@login_required
def delete_asset(id):

    asset = Asset.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(asset)

    db.session.commit()

    flash(
        'Asset Deleted Successfully',
        'danger'
    )

    return redirect(
        url_for('dashboard')
    )


# ================= EXPORT CSV =================

@app.route('/export')
@login_required
def export_assets():
    assets = Asset.query.filter_by(user_id=current_user.id).all()
    data = []
    for a in assets:
        data.append({
            "Asset Name": a.asset_name,
            "Asset Type": a.asset_type,
            "Employee": a.employee,
            "Status": a.status,
            "Reason": a.reason
        })

    df = pd.DataFrame(data)
    path = "asset_export.csv"
    df.to_csv(path, index=False)
    return send_file(path, as_attachment=True)

# ================= IMPORT CSV =================

@app.route('/import', methods=['POST'])
@login_required
def import_assets():
    file = request.files.get('csv_file')

    if not file:
        flash('Please select a CSV file', 'danger')
        return redirect(url_for('dashboard'))

    df = pd.read_csv(file)

    for _, row in df.iterrows():
        asset = Asset(
            user_id=current_user.id,
            asset_name=str(row.get('Asset Name', row.get('asset_name', ''))),
asset_type=str(row.get('Asset Type', row.get('asset_type', ''))),
employee=str(row.get('Employee', row.get('employee', ''))),
status=str(row.get('Status', row.get('status', 'Active'))),
reason=str(row.get('Reason', row.get('reason', '')))
        )
        db.session.add(asset)

    db.session.commit()
    flash('CSV Imported Successfully', 'success')
    return redirect(url_for('dashboard'))

# ================= LOGOUT =================

@app.route('/logout')
@login_required
def logout():

    logout_user()

    flash(
        'Logged Out Successfully',
        'info'
    )

    return redirect(
        url_for('login')
    )

# ================= DATABASE =================

with app.app_context():

    db.create_all()

# ================= RUN =================

if __name__ == '__main__':

    app.run(debug=True)