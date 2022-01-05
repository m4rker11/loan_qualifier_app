# -*- coding: utf-8 -*-
"""Loan Qualifier Application.

This is a command line application to match applicants with qualifying loans.

Example:
    $ python app.py
"""
import sys
import fire
import questionary
from pathlib import Path

from qualifier.utils.fileio import load_csv

from qualifier.utils.calculators import (
    calculate_monthly_debt_ratio,
    calculate_loan_to_value_ratio,
)

from qualifier.filters.max_loan_size import filter_max_loan_size
from qualifier.filters.credit_score import filter_credit_score
from qualifier.filters.debt_to_income import filter_debt_to_income
from qualifier.filters.loan_to_value import filter_loan_to_value


def load_bank_data():
    """Ask for the file path to the latest banking data and load the CSV file.

    Returns:
        The bank data from the data rate sheet CSV file.
    """

    csvpath = questionary.text("Enter a file path to a rate-sheet (.csv):").ask()
    csvpath = Path(csvpath)
    if not csvpath.exists():
        sys.exit(f"Oops! Can't find this path: {csvpath}")

    return load_csv(csvpath)


def get_applicant_info():
    """Prompt dialog to get the applicant's financial information.

    Returns:
        Returns the applicant's financial information.
    """

    credit_score = questionary.text("What's your credit score?").ask()
    debt = questionary.text("What's your current amount of monthly debt?").ask()
    income = questionary.text("What's your total monthly income?").ask()
    loan_amount = questionary.text("What's your desired loan amount?").ask()
    home_value = questionary.text("What's your home value?").ask()

    credit_score = int(credit_score)
    debt = float(debt)
    income = float(income)
    loan_amount = float(loan_amount)
    home_value = float(home_value)

    return credit_score, debt, income, loan_amount, home_value


def find_qualifying_loans(bank_data, credit_score, debt, income, loan, home_value):
    """Determine which loans the user qualifies for.

    Loan qualification criteria is based on:
        - Credit Score
        - Loan Size
        - Debit to Income ratio (calculated)
        - Loan to Value ratio (calculated)

    Args:
        bank_data (list): A list of bank data.
        credit_score (int): The applicant's current credit score.
        debt (float): The applicant's total monthly debt payments.
        income (float): The applicant's total monthly income.
        loan (float): The total loan amount applied for.
        home_value (float): The estimated home value.

    Returns:
        A list of the banks willing to underwrite the loan.

    """

    # Calculate the monthly debt ratio
    monthly_debt_ratio = calculate_monthly_debt_ratio(debt, income)
    print(f"The monthly debt to income ratio is {monthly_debt_ratio:.02f}")

    # Calculate loan to value ratio
    loan_to_value_ratio = calculate_loan_to_value_ratio(loan, home_value)
    print(f"The loan to value ratio is {loan_to_value_ratio:.02f}.")

    # Run qualification filters
    bank_data_filtered = filter_max_loan_size(loan, bank_data)
    bank_data_filtered = filter_credit_score(credit_score, bank_data_filtered)
    bank_data_filtered = filter_debt_to_income(monthly_debt_ratio, bank_data_filtered)
    bank_data_filtered = filter_loan_to_value(loan_to_value_ratio, bank_data_filtered)

    print(f"Found {len(bank_data_filtered)} qualifying loans")

    return bank_data_filtered


def save_csv(qualifying_loans, path):
    """Save the qualifying loans to a CSV file.

    Args:
        Qualifying_loans (list): A list of qualifying loans.
        path (str): The path to save the CSV file to.
    """

    with open(path, 'w') as f:
        f.write(f"Lender, Max Loan, Max LTV, Max DTI, Min Credit, Interest Rate\n")
        for loan in qualifying_loans:
            f.write(f"{loan[0]},{loan[1]},{loan[2]},{loan[3]},{loan[4]}, {loan[5]}\n")
    f.close()

def save_qualifying_loans(qualifying_loans):
    """Saves the qualifying loans to a CSV file.
    Given that I’m using the loan qualifier CLI, when I run the qualifier, then the tool should prompt the user to save the results as a CSV file.

    Given that no qualifying loans exist, when prompting a user to save a file, then the program should notify the user and exit.

    Given that I have a list of qualifying loans, when I’m prompted to save the results, then I should be able to opt out of saving the file.

    Given that I have a list of qualifying loans, when I choose to save the loans, the tool should prompt for a file path to save the file.

    Given that I’m using the loan qualifier CLI, when I choose to save the loans, then the tool should save the results as a CSV file.
    Args:
        qualifying_loans (list of lists): The qualifying bank loans.
    """
    # @TODO: Complete the usability dialog for savings the CSV Files.
    if qualifying_loans is None:
        sys.exit(f"Oops! No qualifying loans found. Exiting.")
    save = questionary.confirm("Would you like to save the qualifying loans?").ask()
    if save: 
        save_location = questionary.text("Where would you like to save the csv file of your qualifying loans?").ask()
        saved_location = Path(save_location)
        if not saved_location.exists():
            save = questionary.confirm(f"Oops! Can't find this path: {save_location}, would you like to try again?").ask()
            if save:
                save_qualifying_loans(qualifying_loans)
            else:
                sys.exit(f"Exiting.")
        else:
            save_location = save_location + "results.csv"
            save_location = Path(save_location)
            save_csv(qualifying_loans, save_location)
            print(f"Qualifying loans saved to {save_location}")
    else:
        sys.exit(f"Exiting.")

        



def run():
    """The main function for running the script."""

    # Load the latest Bank data
    bank_data = load_bank_data()

    # Get the applicant's information
    credit_score, debt, income, loan_amount, home_value = get_applicant_info()

    # Find qualifying loans
    qualifying_loans = find_qualifying_loans(
        bank_data, credit_score, debt, income, loan_amount, home_value
    )

    # Save qualifying loans
    save_qualifying_loans(qualifying_loans)


if __name__ == "__main__":
    fire.Fire(run)
