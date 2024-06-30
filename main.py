import json
import csv
import datetime
from PyQt5 import QtWidgets, QtGui, QtCore

# Load loan data from JSON file
def load_loan_data():
    with open('loan_data.json', 'r') as file:
        loan_data = json.load(file)
    return loan_data

# Save loan data to JSON file
def save_loan_data(loan_data):
    with open('loan_data.json', 'w') as file:
        json.dump(loan_data, file, indent=4)

# Calculate remaining balance after additional payment
def calculate_remaining_balance(loan_data, additional_payment):
    remaining_balance = loan_data.get('remaining')
    if remaining_balance is None:
        # Calculate initial balance if the loan is new
        principle = loan_data['p']
        down_payment = loan_data['dp']
        remaining_balance = principle - down_payment
    else:
        principle = remaining_balance

    # Calculate monthly interest
    interest_rate = loan_data['rate'] / 100 / 12
    monthly_interest = principle * interest_rate

    # Calculate new balance after monthly payment and additional payment
    monthly_payment = loan_data['monthly']
    total_payment = monthly_payment + additional_payment
    remaining_balance = principle + monthly_interest - total_payment

    loan_data['remaining'] = f"{remaining_balance:.2f}"
    save_loan_data(loan_data)
    return remaining_balance

# Save payment history to CSV file
def save_payment_history(date, remaining_balance, additional_payment):
    with open('history.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date, f"{remaining_balance:.2f}", additional_payment])

class MortgageCalculatorApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        # Load loan data and set initial remaining balance
        loan_data = load_loan_data()
        remaining_balance = loan_data.get('remaining')
        if remaining_balance is None:
            remaining_balance = loan_data['p'] - loan_data['dp']
            loan_data['remaining'] = remaining_balance
            save_loan_data(loan_data)

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        input_layout = QtWidgets.QHBoxLayout()

        # Widgets
        self.additional_payment_label = QtWidgets.QLabel("Additional Payment Amount:")
        self.additional_payment_entry = QtWidgets.QLineEdit()
        self.remaining_balance_label = QtWidgets.QLabel(f"Remaining Balance: ${remaining_balance:,.2f}")
        self.submit_button = QtWidgets.QPushButton("Submit Payment")

        # Connect button click to submit_payment method
        self.submit_button.clicked.connect(self.submit_payment)

        # Add widgets to layout
        input_layout.addWidget(self.additional_payment_label)
        input_layout.addWidget(self.additional_payment_entry)
        layout.addLayout(input_layout)
        layout.addWidget(self.remaining_balance_label)
        layout.addWidget(self.submit_button)

        # Set layout
        self.setLayout(layout)
        self.setWindowTitle("Mortgage Calculator")
        self.setGeometry(100, 100, 400, 150)

    def submit_payment(self):
        additional_payment = float(self.additional_payment_entry.text())
        loan_data = load_loan_data()

        # Initial down payment handling
        if loan_data['remaining'] is None:
            loan_data['remaining'] = loan_data['p'] - loan_data['dp']

        remaining_balance = calculate_remaining_balance(loan_data, additional_payment)

        # Save the payment history
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        save_payment_history(current_date, remaining_balance, additional_payment)

        # Update the remaining balance label
        self.remaining_balance_label.setText(f"Remaining Balance: ${remaining_balance:,.2f}")
        QtWidgets.QMessageBox.information(self, "Payment Submitted", "Your payment has been recorded.")

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    ex = MortgageCalculatorApp()
    ex.show()
    app.exec_()
