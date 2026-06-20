def generate_ai_recommendations(
    forecast_usage,
    anomaly_count,
    carbon_emission
):

    recommendations = []

    # Forecast-based
    if forecast_usage > 4:

        recommendations.append(
            "⚡ Forecast indicates high future energy consumption. Consider reducing peak-hour appliance usage."
        )

    # Anomaly-based
    if anomaly_count > 500:

        recommendations.append(
            "⚠ Multiple abnormal consumption spikes detected. Check air conditioners, heaters, and heavy appliances."
        )

    # Carbon-based
    if carbon_emission > 10000:

        recommendations.append(
            "🌱 Carbon footprint is above recommended levels. Consider energy-efficient devices and reduced usage."
        )

    if len(recommendations) == 0:

        recommendations.append(
            "✅ Energy usage patterns appear healthy. Keep maintaining efficient consumption habits."
        )

    return recommendations