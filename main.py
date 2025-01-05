import os
import pandas as pd
from DataExtractor import DataExtractor
from NBAStandingPredictor import NBAStandingPredictor

def main():
    # Define constants
    SEASON = 2025  # Update this to the desired season
    MODEL_PATH = "ridge_model.joblib"
    SCALER_PATH = "scaler.joblib"
    EXTRACTED_DATA_PATH = "extracted_data.csv"
    PREDICTED_STANDINGS_PATH = "predicted_standings_ridge.csv"

    # Step 1: Data Extraction and Cleaning
    print("Starting data extraction...")
    extractor = DataExtractor(season=SEASON)
    extracted_data = extractor.extract()
    print(f"Extracted data saved to {EXTRACTED_DATA_PATH}.")

    # Step 2: Load extracted data
    print("Loading extracted data...")
    extracted_data = pd.read_csv(EXTRACTED_DATA_PATH)

    # Extract team names and drop unnecessary columns for predictions
    team_names = extracted_data["Team"]
    prediction_input_data = extracted_data.drop(columns=["Team", "Season"], errors="ignore")

    # Step 3: Predict Standings
    print("Initializing predictor...")
    predictor = NBAStandingPredictor(model_path=MODEL_PATH, scaler_path=SCALER_PATH)

    print("Making predictions...")
    predicted_standings = predictor.predict_standings(prediction_input_data, team_names)

    # Step 4: Save and display predictions
    predicted_standings.to_csv(PREDICTED_STANDINGS_PATH, index=False)
    print(f"Predicted standings saved to {PREDICTED_STANDINGS_PATH}.")
    print(predicted_standings)

if __name__ == "__main__":
    main()
