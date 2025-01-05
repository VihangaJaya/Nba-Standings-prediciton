import pandas as pd
import numpy as np
import joblib
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


class NBAStandingPredictor:
    def __init__(self, model_path, scaler_path):
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)

    def preprocess_data(self, input_data):
        required_features = ["PW", "SRS", "NRtg", "ORtg", "TS%", "DRtg", "PA/G", "eFG%", "3P%", "FG%"]

        print(f"Input data columns before filtering: {input_data.columns.tolist()}")
        print(f"Input data shape before filtering: {input_data.shape}")

        # Select required features and handle missing values
        input_data = input_data[required_features]
        input_data.fillna(input_data.mean(), inplace=True)

        # Debugging: Check input data after filtering
        print(f"Input data columns after filtering: {input_data.columns.tolist()}")
        print(f"Input data shape after filtering: {input_data.shape}")

        # Convert to NumPy array to avoid feature name mismatches
        input_data_array = input_data.to_numpy()

        # Debugging: Check array shape
        print(f"Processed data shape (NumPy): {input_data_array.shape}")

        # Scale the data
        input_data_scaled = self.scaler.transform(input_data_array)

        # Debugging: Check scaled data shape
        print(f"Scaled data shape: {input_data_scaled.shape}")
        return input_data_scaled

    def predict_standings(self, input_data, team_names):
        # Preprocess the data
        processed_data = self.preprocess_data(input_data)

        # Debugging: Check processed data before prediction
        print(f"Processed data shape before prediction: {processed_data.shape}")

        # Predict standings
        predictions = self.model.predict(processed_data)

        # Debugging: Print predictions
        print(f"Predictions: {predictions}")

        # Create standings DataFrame
        standings = pd.DataFrame({
            "Team": team_names,
            "Predicted W/L%": predictions
        }).sort_values(by="Predicted W/L%", ascending=False).reset_index(drop=True)
        standings["Predicted Rank"] = standings.index + 1
        return standings


if __name__ == "__main__":
    MODEL_PATH = "ridge_model.joblib"
    SCALER_PATH = "scaler.joblib"

    predictor = NBAStandingPredictor(model_path=MODEL_PATH, scaler_path=SCALER_PATH)

    # Load and preprocess the data
    current_season_data = pd.read_csv("Featured_data_2025.csv")

    # Drop unwanted columns
    team_names = current_season_data["Team"]
    current_season_data = current_season_data.drop(columns=["Team", "Unnamed: 0"])

    # Debugging: Check initial data
    print(f"Initial data shape: {current_season_data.shape}")
    print(f"Initial data columns: {current_season_data.columns.tolist()}")

    # Make predictions
    predicted_standings = predictor.predict_standings(current_season_data, team_names)

    # Save or display results
    predicted_standings.to_csv("predicted_standings.csv", index=False)
    print(predicted_standings)
