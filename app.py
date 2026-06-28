from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from elastic.logger import send_log
from datetime import datetime, UTC          # Fix 5: import UTC
from crypto.index_verifier import verify_index
from alerts.alert_manager import get_recent_alerts
from crypto.seal_metadata import get_all_seals
from pki.certificate_manager import get_certificate_status
from opensearchpy import OpenSearch
import os
from export_logs import export_logs
from crypto.hybrid_encrypt import encrypt_file
from dotenv import load_dotenv

es = OpenSearch(
    hosts=[os.getenv("OPENSEARCH_URL", "http://opensearch:9200")],
    use_ssl=False,
    verify_certs=False
)
load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///logseal.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user")


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
    quantity = db.Column(db.Integer, default=1)
    product = db.relationship("Product")


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def log_event(event_type, message, user_id=None, username=None, status="success"):
    if current_user.is_authenticated:
        user_id = user_id or current_user.id
        username = username or current_user.username
    else:
        user_id = 0
        username = username or "guest"

    send_log(user_id, username, event_type, message, status)


def seed_products():
    if Product.query.count() == 0:
        products = [
            Product(name="Premium Hoodie", price=59.99, description="Comfortable black hoodie."),
            Product(name="Classic T-Shirt", price=29.99, description="Simple cotton t-shirt."),
            Product(name="Leather Jacket", price=129.99, description="Stylish jacket."),
            Product(name="Baseball Cap", price=24.99, description="Adjustable cap."),
        ]
        db.session.add_all(products)
        db.session.commit()


@app.route("/")
def index():
    log_event("VIEW_HOME", "User visited home page")
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or email already exists.")
            log_event("USER_REGISTER_FAILED", f"Registration failed for {email}", 0, "guest", "failed")
            return redirect(url_for("register"))

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()

        log_event(
            "USER_REGISTER",
            f"New user registered: {username}",
            user.id,
            username
        )

        flash("Account created. Please login.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if user.role == "admin":
                log_event("ADMIN_LOGIN", f"Admin {user.username} logged in", user.id, user.username)
                return redirect(url_for("admin_dashboard"))
            log_event("USER_LOGIN", f"{user.username} logged in", user.id, user.username)
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.")
        log_event("USER_LOGIN_FAILED",f"Failed login attempt for {email}",0, "guest","failed")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    username = current_user.username
    user_id = current_user.id
    role = current_user.role

    if role == "admin":
        log_event("ADMIN_LOGOUT", f"Admin {username} logged out", user_id, username)
    else:
        log_event("USER_LOGOUT", f"{username} logged out", user_id, username)

    logout_user()
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
    return render_template("dashboard.html", cart_count=cart_count)


@app.route("/products")
def products():
    log_event("VIEW_PRODUCTS", "User viewed products page")
    all_products = Product.query.all()
    return render_template("products.html", products=all_products)


@app.route("/add-to-cart/<int:product_id>")
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)

    cart_item = CartItem.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id)
        db.session.add(cart_item)

    db.session.commit()

    log_event(
        "ADD_TO_CART",
        f"{current_user.username} added {product.name} to cart",
        current_user.id,
        current_user.username
    )

    flash(f"{product.name} added to cart.")
    return redirect(url_for("products"))


@app.route("/cart")
@login_required
def cart():
    log_event(
        "VIEW_CART",
        f"{current_user.username} viewed cart",
        current_user.id,
        current_user.username
    )

    items = CartItem.query.filter_by(user_id=current_user.id).all()
    return render_template("cart.html", items=items)


@app.route("/blog")
def blog():
    log_event("VIEW_BLOG", "User viewed blog page")
    return render_template("blog.html")


def admin_required():
    if not current_user.is_authenticated:
        abort(403)
    if current_user.role != "admin":
        abort(403)


def is_admin():
    return current_user.is_authenticated and current_user.role == "admin"


@app.route("/admin")
@login_required
def admin_dashboard():
    admin_required()

    log_event(
        "ADMIN_VIEW_DASHBOARD",
        "Admin viewed dashboard",
        current_user.id,
        current_user.username
    )

    return render_template("admin_dashboard.html")


@app.route("/admin/verify")
@login_required
def admin_verify():
    admin_required()

    # Fix 5: replaced datetime.utcnow() with datetime.now(UTC)
    index_name = "logs-" + datetime.now(UTC).strftime("%Y-%m-%d")
    result = verify_index(index_name)

    log_event(
        "ADMIN_VERIFY_INDEX",
        f"Admin verified index {index_name}",
        current_user.id,
        current_user.username
    )

    return render_template("admin_verify.html", result=result)


@app.route("/admin/seals")
@login_required
def admin_seals():
    admin_required()
    log_event("ADMIN_VIEW_SEALS", "Admin viewed seal metadata", current_user.id, current_user.username)

    seals = get_all_seals()
    return render_template("admin_seals.html", seals=seals)


@app.route("/admin/alerts")
@login_required
def admin_alerts():
    admin_required()

    log_event(
        "ADMIN_VIEW_ALERTS",
        "Admin viewed security alerts",
        current_user.id,
        current_user.username
    )

    alerts = get_recent_alerts()
    return render_template("admin_alerts.html", alerts=alerts)


@app.route("/admin/certificates")
@login_required
def admin_certificates():
    admin_required()

    log_event(
        "ADMIN_VIEW_CERTIFICATES",
        "Admin viewed certificate status",
        current_user.id,
        current_user.username
    )

    cert_status = get_certificate_status()
    return render_template("admin_certificates.html", cert_status=cert_status)


@app.route("/admin/audit-logs")
@login_required
def admin_audit_logs():
    admin_required()

    log_event(
        "ADMIN_VIEW_AUDIT_LOGS",
        "Admin reviewed audit logs",
        current_user.id,
        current_user.username
    )

    # Fix 1: corrected typo `responsresponse` → `response`
    # Fix 3: wrapped query in body={} for OpenSearch compatibility
    response = es.search(
        index="logs-*",
        body={
            "size": 100,
            "sort": [
                {
                    "timestamp": {
                        "order": "desc"
                    }
                }
            ],
            "query": {
                "match_all": {}
            }
        }
    )

    logs = [hit["_source"] for hit in response["hits"]["hits"]]
    return render_template("admin_audit_logs.html", logs=logs)


@app.route("/admin/users")
@login_required
def admin_users():
    admin_required()

    users = User.query.all()

    log_event(
        "ADMIN_VIEW_USERS",
        "Admin viewed users",
        current_user.id,
        current_user.username
    )

    return render_template("admin_users.html", users=users)


@app.route("/admin/users/<int:user_id>/delete")
@login_required
def admin_delete_user(user_id):
    admin_required()

    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash("You cannot delete your own admin account.")
        return redirect(url_for("admin_users"))

    username = user.username
    email = user.email

    db.session.delete(user)
    db.session.commit()

    log_event(
        "ADMIN_DELETE_USER",
        f"Admin deleted user {email}",
        current_user.id,
        current_user.username
    )

    flash(f"User {username} deleted successfully.")
    return redirect(url_for("admin_users"))


@app.route("/admin/keystore")
@login_required
def admin_keystore():
    admin_required()

    keystore_path = "pki/certs/logseal.p12"

    log_event(
        "ADMIN_VIEW_KEYSTORE",
        "Admin viewed PKCS12 keystore status",
        current_user.id,
        current_user.username
    )

    return render_template(
        "admin_keystore.html",
        keystore_exists=os.path.exists(keystore_path),
        keystore_path=keystore_path
    )


@app.route("/admin/export-archive")
@login_required
def admin_export_archive():
    admin_required()

    archive_file = export_logs()
    encrypt_file(archive_file)

    log_event(
        "ADMIN_EXPORT_ENCRYPTED_ARCHIVE",
        "Admin exported encrypted log archive using AES-GCM and RSA key wrapping",
        current_user.id,
        current_user.username
    )

    return render_template(
        "admin_export_archive.html",
        archive_file=archive_file,
        encrypted_file=archive_file + ".enc",
        encrypted_key=archive_file + ".enc.key"
    )


@app.route("/admin/automation")
@login_required
def admin_automation():
    admin_required()

    try:
        with open("automation.log", "r") as f:
            verification_logs = f.readlines()[-20:]
    except:
        verification_logs = []

    try:
        with open("seal_automation.log", "r") as f:
            seal_logs = f.readlines()[-20:]
    except:
        seal_logs = []

    log_event(
        "ADMIN_VIEW_AUTOMATION",
        "Admin viewed automation status",
        current_user.id,
        current_user.username
    )

    return render_template(
        "admin_automation.html",
        verification_logs=verification_logs,
        seal_logs=seal_logs
    )


@app.route("/admin/encryption")
@login_required
def admin_encryption():
    admin_required()
    log_event("ADMIN_VIEW_ENCRYPTION", "Admin viewed hybrid encryption status", current_user.id, current_user.username)
    return render_template("admin_encryption.html")


@app.route("/admin/statistics")
@login_required
def admin_statistics():
    admin_required()

    try:
        # Fix 4: wrapped query in body={} for OpenSearch compatibility
        response = es.search(
            index="logseal-alerts",
            body={
                "size": 1000,
                "query": {
                    "match_all": {}
                }
            }
        )
        alerts = response["hits"]["hits"]
    except:
        alerts = []

    total_alerts = len(alerts)
    critical = sum(1 for a in alerts if a["_source"].get("severity") == "CRITICAL")
    high = sum(1 for a in alerts if a["_source"].get("severity") == "HIGH")
    medium = sum(1 for a in alerts if a["_source"].get("severity") == "MEDIUM")

    log_event("ADMIN_VIEW_STATISTICS", "Admin viewed security statistics", current_user.id, current_user.username)

    return render_template(
        "admin_statistics.html",
        total_alerts=total_alerts,
        critical=critical,
        high=high,
        medium=medium
    )


@app.route("/admin/crl")
@login_required
def admin_crl():
    admin_required()

    crl_path = "pki/ca/rootCA.crl"

    log_event(
        "ADMIN_VIEW_CRL",
        "Admin viewed certificate revocation status",
        current_user.id,
        current_user.username
    )

    return render_template(
        "admin_crl.html",
        crl_exists=os.path.exists(crl_path),
        crl_path=crl_path
    )


@app.route("/admin/email-alerts")
@login_required
def admin_email_alerts():
    admin_required()
    log_event("ADMIN_VIEW_EMAIL_ALERTS", "Admin viewed email alert status", current_user.id, current_user.username)
    return render_template("admin_email_alerts.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_products()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
