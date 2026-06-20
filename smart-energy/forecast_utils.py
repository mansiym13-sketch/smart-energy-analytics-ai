import joblib

model = joblib.load("forecast_model.pkl")

def get_forecast(days=30):
    future = model.make_future_dataframe(
        periods=days
    )

    forecast = model.predict(future)

    return forecast[
        ["ds", "yhat", "yhat_lower", "yhat_upper"]
    ]