
# Get credit card number from user
while True:
    try:
        card_number = int(input("Number: "))
    except ValueError:
        print("Number must be an integer.")
        continue

    if card_number < 0:
        print("Number must be a positive integer.")
        continue

    break

# Validate credit card number using Luhn's algorithm
def luhn_algorithm(card_number):
    total_sum = 0
    num_digits = len(str(card_number))
    is_second = False

    for i in range(num_digits - 1, -1, -1):
        digit = int(str(card_number)[i])

        if is_second:
            digit *= 2
            if digit > 9:
                digit -= 9

        total_sum += digit
        is_second = not is_second

    return total_sum % 10 == 0

# Check if the card number is valid
if luhn_algorithm(card_number):
    print("Valid credit card number.")
else:
    print("Invalid credit card number.")

# Determine the type of credit card based on the number
def get_card_type(card_number):
    card_number_str = str(card_number)
    if card_number_str.startswith("4") and len(card_number_str) in [13, 16]:
        return "VISA"
    elif card_number_str.startswith(("34", "37")) and len(card_number_str) == 15:
        return "AMEX"
    elif card_number_str.startswith(("51", "52", "53", "54", "55")) and len(card_number_str) == 16:
        return "MASTERCARD"
    else:
        return "INVALID"


# Print the type of credit card
if luhn_algorithm(card_number):
    card_type = get_card_type(card_number)

    if card_type != "INVALID":
        print(card_type)
    else:
        print("INVALID")
else:
    print("INVALID")


