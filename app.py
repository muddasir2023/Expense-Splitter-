from flask import Flask, request, jsonify, render_template
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

SWAGGER_URL = '/docs'
API_URL = '/static/openapi.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/split', methods=['POST'])
def split_expenses():
    data = request.get_json()
    participants = data['participants']
    total = sum(p['amount'] for p in participants)
    per_person = total / len(participants)

    transactions = []
    balances = {p['name']: p['amount'] - per_person for p in participants}
    debtors = sorted([(k, v) for k, v in balances.items() if v < 0], key=lambda x: x[1])
    creditors = sorted([(k, v) for k, v in balances.items() if v > 0], key=lambda x: x[1], reverse=True)

    i, j = 0, 0
    while i < len(debtors) and j < len(creditors):
        debtor, debt_amt = debtors[i]
        creditor, credit_amt = creditors[j]
        pay = min(-debt_amt, credit_amt)
        transactions.append(f"{debtor} pays {creditor} Rs{round(pay, 2)}")
        debtors[i] = (debtor, debt_amt + pay)
        creditors[j] = (creditor, credit_amt - pay)
        if debtors[i][1] == 0:
            i += 1
        if creditors[j][1] == 0:
            j += 1

    return jsonify({
        "per_person": round(per_person, 2),
        "transactions": transactions
    })

if __name__ == "__main__":
    app.run(debug=True)
