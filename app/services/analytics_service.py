from datetime import datetime

from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from sqlalchemy.sql import asc, desc, func

from ..models.category import Category
from ..models.expense import Expense


def get_monthly_expenses(user_id: str, month_from: str, month_to: str, db: Session):
    if not month_from or not month_to:
        return []
    date_group = func.date_trunc("month", Expense.date)
    expenses = (
        db.query(
            date_group.label("month"),
            func.sum(Expense.amount).label("total_amount"),
        )
        .filter(Expense.user_id == user_id)
        .group_by("month")
    )
    expenses = expenses.filter(
        Expense.date.between(
            datetime.strptime(month_from, "%Y-%m"),
            datetime.strptime(month_to, "%Y-%m") + relativedelta(months=1),
        )
    )
    expenses = expenses.order_by(asc("month")).all()
    return expenses


def get_category_expenses(user_id: str, month_from: str, month_to: str, db: Session):
    if not month_from or not month_to:
        return []
    expenses = (
        db.query(
            Category.name.label("category"),
            func.sum(Expense.amount).label("total_amount"),
        )
        .join(Category, Expense.category_id == Category.id)
        .filter(Expense.user_id == user_id)
        .group_by(Category.name)
    )
    expenses = expenses.filter(
        Expense.date.between(
            datetime.strptime(month_from, "%Y-%m"),
            datetime.strptime(month_to, "%Y-%m") + relativedelta(months=1),
        )
    )
    expenses = expenses.order_by(desc(Category.name)).all()
    return expenses


def generate_recommendations(
    user_id: str,
    month_from: str,
    month_to: str,
    db: Session,
    spike_thresh=1.10,
    max_cat_thresh=0.35,
    small_total_thresh=0.5,
):
    monthly_expenses = get_monthly_expenses(
        user_id=user_id, month_from=month_from, month_to=month_to, db=db
    )
    category_expenses = get_category_expenses(
        user_id=user_id, month_from=month_from, month_to=month_to, db=db
    )
    monthly_values = [value[1] for value in monthly_expenses]
    category_data = dict(category_expenses)

    recs = []

    if category_data:
        total = sum(category_data.values())
        if total > 0:
            added = False
            for cat, val in category_data.items():
                ratio = val / total
                if ratio >= max_cat_thresh:
                    recs.append(
                        f"Категорія «{cat}» займає {ratio*100:.1f}% від ваших витрат — більше порогового значення {max_cat_thresh*100:.0f}%. "
                        "Можливо, варто переглянути витрати в цій сфері."
                    )
                    added = True
                    break
            if not added:
                recs.append(
                    f"Жодна категорія не перевищує порогову долю витрат. Ваші витрати у межах норми {max_cat_thresh*100:.0f}%."
                )

    if len(monthly_values) >= 2:
        last = monthly_values[-1]
        prev = monthly_values[-2]
        growth_ratio = last / prev if prev > 0 else 1.0

        if growth_ratio > spike_thresh:
            recs.append(
                f"Витрати за останній місяць зросли на {growth_ratio*100:.1f}% — перевищено глобальний поріг {spike_thresh*100:.0f}%. Спробуйте визначити причину стрибка."
            )
        else:
            recs.append(
                f"Витрати за останній місяць склали {last}, що на {growth_ratio*100:.1f}% більше, ніж попередній місяць ({prev}). "
                f"Це в межах норми {spike_thresh*100:.0f}%."
            )

    ignored_cats = ["Їжа", "Транспорт", "Комунальні послуги"]
    if category_data:
        total = sum(category_data.values())
        small_total = sum(
            val for cat, val in category_data.items() if cat not in ignored_cats
        )
        small_ratio = small_total / total if total > 0 else 0

        if small_ratio > small_total_thresh:
            recs.append(
                f"Дрібні витрати складають {small_ratio*100:.1f}% від загальних витрат — більше порогового значення {small_total_thresh*100:.0f}%. Рекомендується переглянути дрібні витрати."
            )
        else:
            recs.append(
                f"Дрібні витрати складають {small_ratio*100:.1f}% від загальних витрат — в межах норми {small_total_thresh*100:.0f}%."
            )

    if not monthly_expenses:
        recs.append("Оберіть період для аналізу та створення рекомендацій")

    return recs
