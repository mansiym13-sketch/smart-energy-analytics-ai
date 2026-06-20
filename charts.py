import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

GREEN = "#2E7D32"
LIGHT_GREEN = "#66BB6A"
ACCENT = "#A5D6A7"
BG = "#0A0A0A"
PAPER = "#1A1A1A"
TEXT = "#E8F5E9"
GRID = "#2A2A2A"

LAYOUT_BASE = dict(
    paper_bgcolor=PAPER,
    plot_bgcolor=BG,
    font=dict(color=TEXT, family="Inter, sans-serif"),
    xaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
    yaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
    margin=dict(l=40, r=20, t=40, b=40),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT)),
)


def daily_bar_chart(daily_df: pd.DataFrame, threshold: float = None) -> go.Figure:
    fig = go.Figure()
    if daily_df.empty:
        fig.update_layout(title="No data yet", **LAYOUT_BASE)
        return fig

    colors_list = [LIGHT_GREEN if (threshold is None or v <= threshold) else "#EF5350"
                   for v in daily_df["kwh"]]

    fig.add_trace(go.Bar(
        x=daily_df["date"].astype(str),
        y=daily_df["kwh"],
        marker_color=colors_list,
        name="Daily kWh",
        hovertemplate="<b>%{x}</b><br>%{y:.2f} kWh<extra></extra>",
    ))

    if threshold:
        fig.add_hline(y=threshold, line_dash="dash", line_color="#FFA726",
                      annotation_text=f"Threshold: {threshold} kWh",
                      annotation_font_color="#FFA726")

    fig.update_layout(title="Daily Energy Consumption", xaxis_title="Date",
                      yaxis_title="kWh", **LAYOUT_BASE)
    return fig


def weekly_line_chart(weekly_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if weekly_df.empty:
        fig.update_layout(title="No data yet", **LAYOUT_BASE)
        return fig

    fig.add_trace(go.Scatter(
        x=weekly_df["week"].astype(str),
        y=weekly_df["kwh"],
        mode="lines+markers",
        line=dict(color=LIGHT_GREEN, width=2),
        marker=dict(color=GREEN, size=8),
        fill="tozeroy",
        fillcolor="rgba(46,125,50,0.15)",
        name="Weekly kWh",
        hovertemplate="<b>%{x}</b><br>%{y:.2f} kWh<extra></extra>",
    ))

    fig.update_layout(title="Weekly Energy Consumption", xaxis_title="Week",
                      yaxis_title="kWh", **LAYOUT_BASE)
    return fig


def monthly_bar_chart(monthly_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if monthly_df.empty:
        fig.update_layout(title="No data yet", **LAYOUT_BASE)
        return fig

    fig.add_trace(go.Bar(
        x=monthly_df["month"].astype(str),
        y=monthly_df["kwh"],
        marker_color=GREEN,
        marker_line_color=LIGHT_GREEN,
        marker_line_width=1,
        name="Monthly kWh",
        hovertemplate="<b>%{x}</b><br>%{y:.2f} kWh<extra></extra>",
    ))

    fig.update_layout(title="Monthly Energy Consumption", xaxis_title="Month",
                      yaxis_title="kWh", **LAYOUT_BASE)
    return fig


def forecast_chart(history_df: pd.DataFrame, forecast_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    if not history_df.empty:
        fig.add_trace(go.Scatter(
            x=history_df["date"].astype(str),
            y=history_df["actual_kwh"],
            mode="lines",
            line=dict(color=ACCENT, width=1.5),
            name="Actual",
            hovertemplate="<b>%{x}</b><br>Actual: %{y:.2f} kWh<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=history_df["date"].astype(str),
            y=history_df["fitted_kwh"],
            mode="lines",
            line=dict(color=LIGHT_GREEN, width=1.5, dash="dot"),
            name="Model Fit",
            hovertemplate="<b>%{x}</b><br>Fitted: %{y:.2f} kWh<extra></extra>",
        ))

    if not forecast_df.empty:
        fig.add_trace(go.Scatter(
            x=pd.concat([forecast_df["date"], forecast_df["date"][::-1]]).astype(str),
            y=pd.concat([forecast_df["upper"], forecast_df["lower"][::-1]]),
            fill="toself",
            fillcolor="rgba(46,125,50,0.2)",
            line=dict(color="rgba(0,0,0,0)"),
            name="Confidence Band",
            showlegend=True,
        ))
        fig.add_trace(go.Scatter(
            x=forecast_df["date"].astype(str),
            y=forecast_df["predicted_kwh"],
            mode="lines+markers",
            line=dict(color="#FFA726", width=2, dash="dash"),
            marker=dict(color="#FFA726", size=6),
            name="Forecast",
            hovertemplate="<b>%{x}</b><br>Forecast: %{y:.2f} kWh<extra></extra>",
        ))

    fig.update_layout(title="Energy Forecast (14 Days)", xaxis_title="Date",
                      yaxis_title="kWh", **LAYOUT_BASE)
    return fig


def admin_user_comparison(all_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if all_df.empty:
        fig.update_layout(title="No data", **LAYOUT_BASE)
        return fig

    grouped = all_df.groupby("user_id")["kwh"].sum().reset_index()
    grouped.columns = ["User", "Total kWh"]

    fig.add_trace(go.Bar(
        x=grouped["User"],
        y=grouped["Total kWh"],
        marker_color=LIGHT_GREEN,
        hovertemplate="<b>%{x}</b><br>%{y:.2f} kWh<extra></extra>",
    ))
    fig.update_layout(title="Total Consumption by User", xaxis_title="User",
                      yaxis_title="Total kWh", **LAYOUT_BASE)
    return fig


def heatmap_chart(daily_df: pd.DataFrame) -> go.Figure:
    if daily_df.empty or len(daily_df) < 7:
        fig = go.Figure()
        fig.update_layout(title="Not enough data for heatmap", **LAYOUT_BASE)
        return fig

    df = daily_df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["week"] = df["date"].dt.isocalendar().week.astype(int)
    df["dow"] = df["date"].dt.dayofweek
    df["dow_name"] = df["date"].dt.day_name()

    pivot = df.pivot_table(index="dow", columns="week", values="kwh", aggfunc="sum")
    dow_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[f"W{w}" for w in pivot.columns],
        y=[dow_labels[i] for i in pivot.index],
        colorscale=[[0, "#0A0A0A"], [0.5, GREEN], [1, LIGHT_GREEN]],
        hovertemplate="Week: %{x}<br>Day: %{y}<br>kWh: %{z:.2f}<extra></extra>",
    ))
    fig.update_layout(title="Weekly Heatmap", **LAYOUT_BASE)
    return fig
