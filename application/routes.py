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
        db.func.avg(IncomeExpenses.buy_in).label("average_buy_in"),  # Calculate average buy-in
        db.func.avg(IncomeExpenses.hours_played).label("average_hours_played"),  # Calculate average hours played
        db.func.count().label("num_games_played"),  # Calculate number of games played
        IncomeExpenses.game_type,
        IncomeExpenses.date
    ).group_by(IncomeExpenses.game_type, IncomeExpenses.date).order_by(IncomeExpenses.game_type, IncomeExpenses.date).all()

    income_expense = []
    over_time_expenditure = []
    dates_labels = []
    earnings_over_time = []
    total_buy_ins = []
    sit_and_go_earnings = 0
    tournament_earnings = 0
    num_games_played = 0

    if aggregated_data:
        for total_pot, earnings, total_buy_in, average_buy_in, average_hours_played, num_games, game_type, date in aggregated_data:
            income_expense.append(total_pot)
            over_time_expenditure.append(total_buy_in)
            dates_labels.append(date.strftime("%m-%d-%Y"))
            earnings_over_time.append(earnings)
            total_buy_ins.append(total_buy_in)
            if game_type == 'sit_and_go':
                sit_and_go_earnings += earnings
            elif game_type == 'tournament':
                tournament_earnings += earnings
            num_games_played += num_games
    else:
        average_buy_in = 0
        average_hours_played = 0

    # Calculate total hours played and total months
    total_hours_played = sum([entry.hours_played for entry in IncomeExpenses.query.all()])
    earliest_date = IncomeExpenses.query.order_by(IncomeExpenses.date.asc()).first()
    if earliest_date:
        total_months = (date.today().year - earliest_date.date.year) * 12 + (date.today().month - earliest_date.date.month)
    else:
        total_months = 0

    # Calculate average monthly hours played
    average_monthly_hours_played = total_hours_played / total_months if total_months != 0 else 0

    return render_template("dashboard.html",
                           income_vs_expenses=json.dumps(income_expense),
                           over_time_expenditure=json.dumps(over_time_expenditure),
                           dates_label=json.dumps(dates_labels),
                           earnings=json.dumps(earnings_over_time),
                           total_buy_ins=json.dumps(total_buy_ins),
                           total_earnings=sum(earnings_over_time),  # Pass total earnings
                           total_buy_in=sum(total_buy_ins),  # Pass total buy-ins
                           average_buy_in=average_buy_in,  # Pass average buy-in
                           average_hours_played=average_hours_played,  # Pass average hours played
                           sit_and_go_earnings=sit_and_go_earnings,
                           tournament_earnings=tournament_earnings,
                           num_games_played=num_games_played,
                           average_monthly_hours_played=average_monthly_hours_played)

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
            hours_played=form.hours_played.data,  # Store hours played in the database
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
