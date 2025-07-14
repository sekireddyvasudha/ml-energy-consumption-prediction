# 🔋 Energy Consumption Prediction Web App

This is a full-stack Flask web application that predicts building energy efficiency (Heating & Cooling Load) based on architectural design parameters. It features secure login, CSV upload, batch prediction, SHAP explainability, and light/dark theme.

---

## 🚀 Features

✅ User Authentication (Register/Login)  
✅ Upload your dataset in CSV format  
✅ Predict Heating Load (Y1) or Cooling Load (Y2)  
✅ Batch predictions for entire datasets  
✅ SHAP feature importance explanations  
✅ Downloadable prediction results  
✅ Dark / Light mode toggle  
✅ Responsive UI with Bootstrap

---

## 📂 Folder Structure

energy_app/ ├── app.py # Main Flask backend ├── templates/ # HTML templates │ ├── index.html │ ├── login.html │ └── register.html ├── static/ # Static assets │ ├── script.js │ ├── style.css │ └── shap_plot.png ├── model/ # Trained model and scaler │ ├── model.h5 │ └── scaler.save ├── ENB2012_data.csv # Sample dataset ├── requirements.txt # Python dependencies └── README.md


---

## 🛠 Tech Stack

- **Frontend**: HTML, CSS (Bootstrap), JavaScript (Chart.js)
- **Backend**: Flask, Flask-Session, Flask-CORS
- **Machine Learning**: TensorFlow, SHAP, Scikit-learn
- **Other**: Pandas, NumPy, Matplotlib

---

## ⚙️ Setup Instructions

### 1. Clone this repo

```bash
git clone https://github.com/your-username/energy-prediction-app.git
cd energy-prediction-app


2. Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

4. Run the app
python app.py
Then open your browser to http://localhost:5000.

🧪 Sample Credentials
Username: admin
Password: password123
Or register a new user.

📈 Dataset

The model was trained on ENB2012_data.csv, which includes features such as:
Relative Compactness
Surface Area
Wall Area
Roof Area
Overall Height
Orientation
Glazing Area
Glazing Area Distribution

💡 Future Improvements

Add database integration (e.g. SQLite/PostgreSQL)
Store user prediction history
Allow model retraining with uploaded data
Deploy online using Render or Railway

📜 License
MIT License — free to use and modify.

