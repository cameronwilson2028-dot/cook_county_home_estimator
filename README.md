# Cook County Home Estimator for Streamlit

The Streamlit app uses the exact same saved coefficients, preprocessing, smearing adjustment and 80% range calibration as the existing website. No retraining is required and no raw property records are included.

## Deploy to Streamlit Community Cloud

1. Create a GitHub repository and upload this folder's contents. Keep `app.py`, `predictor.py`, `model.json` and `requirements.txt` at the repository root. Include `.streamlit/config.toml` to preserve the theme.
2. Sign in at https://share.streamlit.io with GitHub and connect the repository.
3. Choose **Create app**, select the repository and branch (usually `main`), and set the main file to `app.py`.
4. Choose an available address such as `cook-county-home-estimator.streamlit.app`. Availability is not guaranteed. Choose Python 3.12 in advanced settings.
5. Deploy, then check the page and configure app access for your intended audience. A private GitHub repository and a private deployed app are separate settings.

Official instructions: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

## Run locally

```text
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Model

OLS on log price, one random sale per PIN, fixed 60/20/20 train/calibration/test split. Point estimates use a training-residual smearing adjustment. The range uses the finite-sample 80th-percentile absolute log error from a separate calibration sample. The model has not been refit after calibration. Predictions describe historical 2022–2025 prices, not current 2026 values. This model's sample split differs from the earlier project notebook; its performance must not be described as that notebook's results.

The raw sample had 9,972 sales; one sale per PIN leaves 9,837 properties. No outlier-based $1.5 million filtering is applied. Test coverage: 79.93%; MAE: $113,367.90; RMSE: $236,353.80; R²: 0.64435. No performance guarantee applies to an individual home or subgroup.

No API keys or credentials are needed. Users' form entries are processed on the Streamlit server; this app does not save them to a database. The supporting house image is loaded from Wikimedia Commons with linked attribution.
