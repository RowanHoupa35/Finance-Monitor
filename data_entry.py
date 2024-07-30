from datetime import datetime

dateFormat = "%d-%m-%Y"
CATEGORIES = {"I": "Income", "E": "Expense"}

def get_Date(prompt, allow_default=False):
    date_str = input(prompt)
    if allow_default and not date_str:
        return datetime.today().strftime(dateFormat)
    try:
        valid_date = datetime.strptime(date_str, dateFormat)
        return valid_date.strftime(dateFormat)
    except ValueError:
        print('Invalid date format. Please enter the date in dd-mm-yyyy format')
        return get_Date(prompt, allow_default)
        

def get_Amount():
    try:
        amount = float(input('Enter the amount: '))
        if amount <= 0:
            raise ValueError('Amount must be a positive value')
        return amount
    except ValueError as e:
        print(e)
        return get_Amount()


def get_Category():
    category = input("Enter a category ('I' for Income or 'E' for Expense): ").upper()
    if category in CATEGORIES:
        return CATEGORIES[category]
    
    print("Invalid category, please enter 'I' for Income or 'E' for Expense.")
    return get_Category()


def get_Description():
    return input("Enter a description: ")
