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

class InformeMod(db.Model):
    __tablename__ = "informe_mod"
    __table_args__ = {"schema": "reporte"}

    id = db.Column(db.Integer, primary_key=True)
    responsable = db.Column(db.Text)
    fecha = db.Column(db.Date)
    numero = db.Column(db.Integer)
    rol = db.Column(db.Text)
    rut = db.Column(db.Text)
    nombre = db.Column(db.Text)
    cargo = db.Column(db.Text)
    horas_trabajo_a = db.Column(db.Integer)
    horas_trabajo_b = db.Column(db.Integer)
    horas_trabajo_c = db.Column(db.Integer)
    horas_trabajo_d = db.Column(db.Integer)
    horas_trabajo_e = db.Column(db.Integer)
    horas_trabajo_f = db.Column(db.Integer)
    horas_trabajo_g = db.Column(db.Integer)
    horas_trabajo_h = db.Column(db.Integer)
    horas_trabajo_i = db.Column(db.Integer)
    horas_trabajo_j = db.Column(db.Integer)
    horas_trabajo_k = db.Column(db.Integer)
    horas_trabajo_l = db.Column(db.Integer)
    horas_trabajo_m = db.Column(db.Integer)
    horas_trabajo_n = db.Column(db.Integer)
    horas_trabajo_o = db.Column(db.Integer)
    hh = db.Column(db.Integer)
    observaciones = db.Column(db.Text)

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
'''@app.route("/")
def index():
    if "user_id" in session:
        trabajadores = Trabajador.query.all()
        actividades = Actividad.query.all()
        tipo = 'trabajadores'  # default
        return render_template("upload.html", role=session["rol"], username=session["username"],
                               trabajadores=trabajadores, actividades=actividades, tipo=tipo)
    return redirect(url_for("login"))
'''
@app.route("/")
def index():
    if "user_id" in session:
        trabajadores = Trabajador.query.all()
        actividades = Actividad.query.all()
        return render_template(
            "upload.html",
            role=session["rol"],
            username=session["username"],
            trabajadores=trabajadores,
            actividades=actividades
        )
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
'''
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
                    id_1=row['ID1'], id_2=row['ID2'], descripcion=row['DESCRIPCION'],
                    rendimiento=row['RENDIMIENTO'], ponderacion=row['PONDERACION'], unidad=row['UNIDAD']
                ))
        db.session.commit()
        return jsonify({"message": "Archivo cargado correctamente!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
'''

@app.route("/upload_excel", methods=["POST"])
@login_required(roles=["uploader"])
def upload_excel():
    if 'file' not in request.files:
        return "No hay archivo", 400
    file = request.files['file']
    tipo = request.form.get('tipo')
    if file.filename == '':
        return "Archivo vacío", 400

    # Funciones auxiliares
    def clean_numeric(x):
        """Convierte a float o devuelve None si es NaN o vacío."""
        if pd.isna(x):
            return None
        if isinstance(x, str):
            x = x.replace('%', '').strip()  # Quitar %
        try:
            return float(x)
        except:
            return None

    def clean_string(x):
        """Convierte a str o devuelve None si es NaN o vacío."""
        if pd.isna(x):
            return None
        return str(x).strip()

    try:
        df = pd.read_excel(file)

        if tipo == "trabajadores":
            for _, row in df.iterrows():
                db.session.add(Trabajador(
                    rut=clean_string(row.get('RUT')),
                    nombre=clean_string(row.get('Nombre')),
                    cargo=clean_string(row.get('Cargo'))
                ))

        elif tipo == "actividades":
            for _, row in df.iterrows():
                db.session.add(Actividad(
                    id_1=clean_string(row.get('ID1')),
                    id_2=clean_string(row.get('ID2')),  # Si quieres numérico: clean_numeric
                    descripcion=clean_string(row.get('DESCRIPCION')),
                    rendimiento=clean_numeric(row.get('RENDIMIENTO')),
                    ponderacion=clean_numeric(row.get('PONDERACION')),
                    unidad=clean_string(row.get('UNIDAD'))
                ))

        db.session.commit()
        return jsonify({"message": "Archivo cargado correctamente!"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/informe_mod")
@login_required()
def informe_mod_list():
    registros = InformeMod.query.order_by(InformeMod.id.desc()).all()
    return render_template("informe_mod_list.html", registros=registros)

# Modelo base (ajústalo si ya lo tienes definido)
class RegistroMod(db.Model):
    __tablename__ = 'registro_mod'
    __table_args__ = {'schema': 'reporte'}
    rut = db.Column(db.String, primary_key=True)
    rol = db.Column(db.String)
    nombre = db.Column(db.String)
    cargo = db.Column(db.String)

@app.route('/buscar_trabajador', methods=['GET'])
def buscar_trabajador():
    rut = request.args.get('rut')
    if not rut:
        return jsonify({'error': 'RUT no proporcionado'}), 400

    trabajador = RegistroMod.query.filter_by(rut=rut).first()
    if trabajador:
        return jsonify({
            'rol': trabajador.rol,
            'nombre': trabajador.nombre,
            'cargo': trabajador.cargo
        })
    else:
        return jsonify({'error': 'No encontrado'}), 404

@app.route("/informe_mod/nuevo", methods=["GET", "POST"])
@login_required(roles=["uploader"])
def informe_mod_nuevo():
    if request.method == "POST":
        data = request.form
        try:
            nuevo = InformeMod(
                responsable=data.get("responsable"),
                fecha=data.get("fecha"),
                numero=data.get("numero"),
                rol=data.get("rol"),
                rut=data.get("rut"),
                nombre=data.get("nombre"),
                cargo=data.get("cargo"),
                horas_trabajo_a=data.get("horas_trabajo_a"),
                horas_trabajo_b=data.get("horas_trabajo_b"),
                horas_trabajo_c=data.get("horas_trabajo_c"),
                horas_trabajo_d=data.get("horas_trabajo_d"),
                horas_trabajo_e=data.get("horas_trabajo_e"),
                horas_trabajo_f=data.get("horas_trabajo_f"),
                horas_trabajo_g=data.get("horas_trabajo_g"),
                horas_trabajo_h=data.get("horas_trabajo_h"),
                horas_trabajo_i=data.get("horas_trabajo_i"),
                horas_trabajo_j=data.get("horas_trabajo_j"),
                horas_trabajo_k=data.get("horas_trabajo_k"),
                horas_trabajo_l=data.get("horas_trabajo_l"),
                horas_trabajo_m=data.get("horas_trabajo_m"),
                horas_trabajo_n=data.get("horas_trabajo_n"),
                horas_trabajo_o=data.get("horas_trabajo_o"),
                hh=data.get("hh"),
                observaciones=data.get("observaciones")
            )
            db.session.add(nuevo)
            db.session.commit()
            flash("Registro agregado correctamente", "success")
            return redirect(url_for("informe_mod_list"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al guardar: {str(e)}", "danger")

    return render_template("informe_mod_form.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
