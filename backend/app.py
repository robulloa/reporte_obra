from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from functools import wraps
import os
import pandas as pd

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "secret_key")

# BD
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# MODELOS
class User(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    rol = db.Column(db.String(20), nullable=False)

class Trabajador(db.Model):
    __tablename__ = "trabajadores"
    id = db.Column(db.Integer, primary_key=True)
    rut = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(50), nullable=False)

class Actividad(db.Model):
    __tablename__ = "actividades"
    id = db.Column(db.Integer, primary_key=True)
    id_1 = db.Column(db.String(20))
    id_2 = db.Column(db.String(20))
    descripcion = db.Column(db.Text, nullable=False)
    rendimiento = db.Column(db.Numeric)
    ponderacion = db.Column(db.Numeric)
    unidad = db.Column(db.String(20))

# DECORADOR
def login_required(roles=None):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                flash("Debes iniciar sesión", "warning")
                return redirect(url_for("login"))
            if roles and session.get("rol") not in roles:
                flash("No tienes permiso", "danger")
                return redirect(url_for("index"))
            return f(*args, **kwargs)
        return decorated_function
    return wrapper

# RUTAS
@app.route("/")
def index():
    if "user_id" in session:
        trabajadores = Trabajador.query.all()
        actividades = Actividad.query.all()
        tipo = 'trabajadores'  # default
        return render_template("upload.html", role=session["rol"], username=session["username"],
                               trabajadores=trabajadores, actividades=actividades, tipo=tipo)
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["rol"] = user.rol
            session["username"] = user.username
            flash("Bienvenido!", "success")
            return redirect(url_for("index"))
        else:
            flash("Usuario o contraseña incorrectos", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada", "info")
    return redirect(url_for("login"))

@app.route("/upload_excel", methods=["POST"])
@login_required(roles=["uploader"])
def upload_excel():
    if 'file' not in request.files:
        return "No hay archivo", 400
    file = request.files['file']
    tipo = request.form.get('tipo')
    if file.filename == '':
        return "Archivo vacío", 400
    try:
        df = pd.read_excel(file)
        if tipo == "trabajadores":
            for _, row in df.iterrows():
                db.session.add(Trabajador(rut=row['RUT'], nombre=row['Nombre'], cargo=row['Cargo']))
        elif tipo == "actividades":
            for _, row in df.iterrows():
                db.session.add(Actividad(
                    id_1=row['ID1'], id_2=row['ID2'], descripcion=row['Descripción'],
                    rendimiento=row['Rendimiento'], ponderacion=row['Ponderación'], unidad=row['Unidad']
                ))
        db.session.commit()
        return jsonify({"message": "Archivo cargado correctamente!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
