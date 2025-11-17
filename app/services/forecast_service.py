from datetime import datetime

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import Session
from statsmodels.tsa.statespace.sarimax import SARIMAX

from ..services.analytics_service import get_monthly_expenses


def preprocess_expenses(user_id, month_from, month_to, db: Session):
    """Единая подготовка данных — формат результата не изменяем."""
    expenses = get_monthly_expenses(
        user_id=user_id, month_from=month_from, month_to=month_to, db=db
    )
    if not expenses:
        return None

    df = pd.DataFrame(expenses, columns=["month", "total"])
    df["month"] = pd.to_datetime(df["month"])
    df = df.set_index("month").sort_index()

    df = df.asfreq("MS", fill_value=0)

    # EMA сглаживание (во всех моделях одинаковое)
    # df["smooth"] = df["total"].ewm(alpha=0.8).mean()
    df["smooth"] = (
        0.5 * df["total"].ewm(alpha=0.6, adjust=False).mean()
        + 0.5 * df["total"].rolling(window=3, min_periods=1).mean()
    )

    avg = df["smooth"].mean()
    std = df["smooth"].std()

    return df, avg, std


def _build_result(month_to, predicted_months, prediction, db, user_id):
    """Формирование результата — одинаково для всех моделей."""
    predicted_expenses = []
    month_from_next = (
        datetime.strptime(month_to, "%Y-%m") + relativedelta(months=1)
    ).strftime("%Y-%m")
    expenses_period = get_monthly_expenses(
        user_id=user_id,
        month_from=month_from_next,
        month_to=(
            datetime.strptime(month_to, "%Y-%m")
            + relativedelta(months=predicted_months)
        ).strftime("%Y-%m"),
        db=db,
    )
    expenses_dict = {k.date(): v for k, v in expenses_period}

    current_month = datetime.strptime(month_to, "%Y-%m") + relativedelta(months=1)

    for value in prediction:
        predicted_expenses.append(
            {
                "month": current_month.strftime("%Y-%m"),
                "total": (
                    float(expenses_dict.get(current_month.date()))
                    if expenses_dict.get(current_month.date()) is not None
                    else None
                ),
                "predicted": float(value),
            }
        )
        current_month += relativedelta(months=1)

    return predicted_expenses


def get_linear_forecast(user_id, month_from, month_to, predicted_months, db: Session):
    df, avg, std = preprocess_expenses(user_id, month_from, month_to, db)
    if df is None:
        return []

    values = df["smooth"].values
    months = np.array([d.month for d in df.index])  # месяц года 1–12
    n = len(values)

    if n < 3:
        return _build_result(
            month_to, predicted_months, [avg] * predicted_months, db, user_id
        )

    window = 12 if n >= 24 else 9 if n >= 12 else n - 1

    X, y = [], []
    for i in range(n - window):
        seq_window = values[i : i + window]
        month_window = months[i : i + window] / 12  # нормализуем месяц 0-1
        X.append(np.hstack([seq_window, month_window]))
        y.append(values[i + window])

    X, y = np.array(X), np.array(y)

    model = LinearRegression()
    model.fit(X, y)

    prediction = []
    seq = values.copy()
    future_months = months.copy()

    for _ in range(predicted_months):
        inp = np.hstack([seq[-window:], future_months[-window:] / 12]).reshape(1, -1)
        next_val = model.predict(inp)[0]
        prediction.append(next_val)

        seq = np.append(seq, next_val)
        future_months = np.append(future_months, (future_months[-1] % 12) + 1)

    return _build_result(month_to, predicted_months, prediction, db, user_id)


def get_arima_forecast(user_id, month_from, month_to, predicted_months, db: Session):
    df, avg, std = preprocess_expenses(user_id, month_from, month_to, db)
    if df is None:
        return [], True

    series = df["total"]

    model_fit = None
    used_fallback = False

    model = SARIMAX(series, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
    model_fit = model.fit()

    if model_fit is None:
        used_fallback = True
        prediction = [avg] * predicted_months
    else:
        prediction = model_fit.forecast(predicted_months)

    return (
        _build_result(month_to, predicted_months, prediction, db, user_id),
        used_fallback,
    )


def get_mlp_forecast(user_id, month_from, month_to, predicted_months, db: Session):
    df, avg, std = preprocess_expenses(user_id, month_from, month_to, db)
    if df is None:
        return []

    # Основной сглаженный ряд — это важно!
    series = df["total"].values.astype(float)
    n = len(series)

    # Если данных мало — fallback
    if n < 4:
        return _build_result(
            month_to, predicted_months, [avg] * predicted_months, db, user_id
        )

    # Массштабируем ряд только для MLP
    scaler = StandardScaler()
    series_scaled = scaler.fit_transform(series.reshape(-1, 1)).flatten()

    # Оптимальное окно
    if n < 12:
        window = max(2, n - 1)
    elif n < 24:
        window = 6
    elif n < 36:
        window = 9
    else:
        window = 12

    # Формируем X, y
    X, y = [], []
    for i in range(n - window):
        X.append(series_scaled[i : i + window])
        y.append(series_scaled[i + window])

    X, y = np.array(X), np.array(y)

    # Модель MLP (твоя рабочая конфигурация)
    model = MLPRegressor(
        hidden_layer_sizes=(128, 64, 32),
        activation="relu",
        solver="adam",
        max_iter=2000,
        alpha=0.0008,
        random_state=42,
    )
    model.fit(X, y)

    # Прогноз
    seq = series_scaled.copy()
    prediction_scaled = []

    for _ in range(predicted_months):
        pred = model.predict(seq[-window:].reshape(1, -1))[0]
        prediction_scaled.append(pred)
        seq = np.append(seq, pred)

    # Обратная трансформация
    prediction = scaler.inverse_transform(
        np.array(prediction_scaled).reshape(-1, 1)
    ).flatten()

    return _build_result(month_to, predicted_months, prediction, db, user_id)
