from flask import Flask, request, jsonify, session, send_file, render_template, redirect, url_for
from flask_cors import CORS
from flask_session import Session
import numpy as np
import pandas as pd
import tensorflow as tf
import shap
import joblib
import os
import io
from datetime import timedelta
import matplotlib.pyplot as plt

app = Flask(__name__)

# -------------------- SESSION & SECURITY --------------------
app.secret_key = 'supersecretkey'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production w/ HTTPS

Session(app)
CORS(app, supports_credentials=True)

# -------------------- MODEL LOADING --------------------
model = tf.keras.models.load_model("model/model.h5", compile=False)
scaler = joblib.load("model/scaler.save")

# Dummy in-memory user store (for demo)
users = {"admin": "password123"}

# Shared global state
stored_input = None
stored_df = None
stored_predictions = None

# -------------------- ROUTES --------------------

@app.route('/')
def home():
    if 'user' in session:
        return render_template("index.html")
    return redirect(url_for('login_page'))

@app.route('/login.html')
def login_page():
    return render_template("login.html")

@app.route('/register.html')
def register_page():
    return render_template("register.html")

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required"}), 400
    if username in users:
        return jsonify({"success": False, "message": "Username already exists"}), 409
    users[username] = password
    return jsonify({"success": True, "message": "Registered successfully"})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if users.get(data["username"]) == data["password"]:
        session['user'] = data["username"]
        print(">>> Logged in:", session.get('user'))
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({"message": "Logged out"})

@app.route('/check_session', methods=['GET'])
def check_session():
    print(">>> Session content:", dict(session))
    return jsonify({"logged_in": 'user' in session})

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    global stored_input, stored_df
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 403

    file = request.files.get('file')
    if not file or file.filename == '':
        return jsonify({"error": "No file provided"}), 400

    try:
        df = pd.read_csv(file)
        if df.shape[1] < 9:
            return jsonify({"error": "CSV must have at least 9 columns (8 input + 1 target)"}), 400
        df = df.dropna().apply(pd.to_numeric, errors='coerce').dropna()
        stored_df = df.copy()
        stored_input = df.iloc[:, :8].values.tolist()
        preview = df.head(10).to_dict(orient='records')
        return jsonify({"message": "CSV uploaded", "preview": preview})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/predict', methods=['POST'])
def predict():
    global stored_input, stored_predictions
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 403
    if stored_input is None:
        return jsonify({"error": "No data uploaded yet"}), 400

    data = request.get_json()
    target = data.get("target", "Y1")
    col_index = 8 if target == "Y1" else 9

    try:
        input_array = np.array(stored_input).astype(np.float32)
        scaled = scaler.transform(input_array)
        preds = model.predict(scaled).flatten().tolist()
        actual = stored_df.iloc[:, col_index].values.tolist()
        stored_predictions = preds

        return jsonify({
            "predictions": preds,
            "actual": actual[:len(preds)]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download_predictions', methods=['GET'])
def download_predictions():
    global stored_predictions
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 403
    if stored_predictions is None:
        return jsonify({"error": "No predictions available"}), 400

    df = pd.DataFrame({"Prediction": stored_predictions})
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return send_file(io.BytesIO(buffer.read().encode()), as_attachment=True,
                     download_name="predictions.csv", mimetype='text/csv')

@app.route('/explain', methods=['GET'])
def explain():
    global stored_input
    if stored_input is None:
        return jsonify({"error": "Upload data first"}), 400

    try:
        background = np.array(stored_input[:100])
        explainer = shap.Explainer(model, background)
        shap_values = explainer(background[:10])
        shap.plots.bar(shap_values[0], show=False)
        plt.tight_layout()
        plt.savefig("static/shap_plot.png")
        plt.close()
        return jsonify({"message": "SHAP plot created"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------- MAIN --------------------
if __name__ == '__main__':
    app.run(debug=True)
