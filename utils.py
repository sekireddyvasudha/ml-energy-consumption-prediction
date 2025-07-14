import os
from tensorflow.keras.models import load_model
import joblib

base_path = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(base_path, 'model', 'model.h5')
scaler_path = os.path.join(base_path, 'model', 'scaler.save')

model = load_model(model_path, compile=False)
scaler = joblib.load(scaler_path)
def generate_shap_plot(model, input_data):
    import shap
    import matplotlib.pyplot as plt

    background = input_data[:100]
    explainer = shap.Explainer(model, background)
    shap_values = explainer(background[:10])
    shap.plots.bar(shap_values[0], show=False)
    plt.tight_layout()
    plt.savefig("static/shap_plot.png")
    plt.close()
