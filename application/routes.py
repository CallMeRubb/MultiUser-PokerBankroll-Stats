from flask import render_template, flash, redirect, url_for
from application import app, db
from application.form import UserInputForm
from application.models import IncomeExpenses
from datetime import datetime, date
import json

@app.route("/")
def index():
    # Query to get aggregated data
    aggregated_data = db.session.query(
        db.func.sum(IncomeExpenses.total_pot).label("total_pot"),
        db.func.sum(IncomeExpenses.earnings).label("earnings"),
        db.func.sum(IncomeExpenses.buy_in).label("total_buy_in"),  # Calculate total buy-ins
        IncomeExpenses.game_type,
        IncomeExpenses.date
    ).group_by(IncomeExpenses.game_type, IncomeExpenses.date).order_by(IncomeExpenses.game_type, IncomeExpenses.date).all()

    income_expense = []
    over_time_expenditure = []
    dates_labels = []
    earnings_over_time = []
    total_buy_ins = []

    for total_pot, earnings, total_buy_in, game_type, date in aggregated_data:
        income_expense.append(total_pot)
        over_time_expenditure.append(total_buy_in)
        dates_labels.append(date.strftime("%m-%d-%Y"))
        earnings_over_time.append(earnings)
        total_buy_ins.append(total_buy_in)

    return render_template("dashboard.html",
                           income_vs_expenses=json.dumps(income_expense),
                           over_time_expenditure=json.dumps(over_time_expenditure),
                           dates_label=json.dumps(dates_labels),
                           earnings=json.dumps(earnings_over_time),
                           total_buy_ins=json.dumps(total_buy_ins),
                           total_earnings=sum(earnings_over_time),  # Pass total earnings
                           total_buy_in=sum(total_buy_ins))  # Pass total buy-ins

@app.route("/add", methods=["GET", "POST"])
def add_expenses():
    form = UserInputForm()

    if form.validate_on_submit():
        earnings = form.total_pot.data - form.buy_in.data  # Calculate earnings

        if form.custom_date.data:  # Check if custom date checkbox is checked
            entry_date = form.custom_date_input.data  # Use custom date if provided
        else:
            entry_date = date.today()  # Use today's date if custom date is not provided

        entry = IncomeExpenses(
            game_type=form.game_type.data,
            buy_in=form.buy_in.data,
            total_pot=form.total_pot.data,
            earnings=earnings,  # Store earnings in the database
            date=entry_date  # Use the determined date
        )

        db.session.add(entry)
        db.session.commit()

        flash("Successful Entry", 'success')
        return redirect(url_for('index'))

    return render_template("add.html", title="Add", form=form)

@app.route("/delete/<int:entry_id>")
def delete(entry_id):
    entry = IncomeExpenses.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash("Deletion was successful", 'success')
    return redirect(url_for("index"))

@app.route('/history')
def history():
    entries = IncomeExpenses.query.order_by(IncomeExpenses.date.desc()).all()
    return render_template("index.html", title="Index", entries=entries)
