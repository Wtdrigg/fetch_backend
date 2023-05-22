from flask import Flask, request, abort
from datetime import datetime, time
from uuid import uuid4 as id_generator
import json
import math

# Instantiates the flask app
app = Flask(__name__)


class Backend:
    # Stores the receipt ID numbers and points earned as Key:Value Pairs
    stored_data = {}

    # Called when a POST request is made to "Domain"/receipts/process
    @app.route('/receipts/process', methods=['POST'])
    def process():
        try:
            if request.method == 'POST':
                # Generates a unique ID
                unique_id = id_generator()

                # Calculates points earned
                points_earned = Backend.calculate_points(request.json, unique_id)

                # Stores the points earned in memory along with the associated ID
                Backend.stored_data[str(unique_id)] = points_earned

                # Prepares an HTTP response showing the ID
                response_data = {"id": str(unique_id)}

                # Loads the response into a JSON format
                response_payload = json.dumps(response_data, ensure_ascii=False)

            # Sends the response.
            return response_payload

        # Responds with a 400 code if the payload received did not contain valid JSON data.
        except json.decoder.JSONDecodeError:
            abort(400, 'Invalid request data: JSON payload must be a string. Please check your JSON format')

    # Called when a GET request is made to "Domain"/receipts/{unique ID}/points.
    # Note that the id must be in UUID format, as that is what is generated when Backend.process() is called.
    @app.route('/receipts/<uuid("uuid4"):id>/points', methods=['GET'])
    def points(id):

        # Prepares an HTTP response showing the points associated with the receipt ID provided in the URL.
        response_data = {"points": Backend.stored_data[str(id)]}

        # Loads the response into a JSON format.
        response_payload = json.dumps(response_data, ensure_ascii=False)

        # Sends the response.
        return response_payload

    # calculates the number of points a receipt is worth. This done by calling several functions and adding their
    # return values
    def calculate_points(reciept, unique_id):

        # verifies that the data provided is a JSON string, or a Python Dict
        if type(reciept) == str:
            receipt_dict = json.loads(reciept)
        elif type(reciept) == dict:
            receipt_dict = reciept
        else:
            raise TypeError("Invalid JSON format, please uses a JSON string or a Python Dictionary")

        # Starts with 0 points. Each function calculates points from one of the rules provided with the assessment.
        print("----------------------------------------------------")
        print("Receipt ID: " + str(unique_id))
        total_points = 0
        total_points += Backend.points_retailer_name(receipt_dict)
        total_points += Backend.points_dollar_amount(receipt_dict)
        total_points += Backend.points_item_amount(receipt_dict)
        total_points += Backend.points_item_name_length(receipt_dict)
        total_points += Backend.points_item_purchase_date(receipt_dict)
        total_points += Backend.points_item_purchase_time(receipt_dict)
        print("Total Points: " + str(total_points))
        return total_points

    # Gives 1 point for every alphanumeric character of the retailers name.
    def points_retailer_name(receipt_dict):
        name_points = 0
        for char in (receipt_dict['retailer']):
            if char.isalnum():
                name_points += 1
        print("Retailer Name Points: " + str(name_points))
        return name_points

    # Calculates the number of points received based on the total dollar amount of the receipt.
    def points_dollar_amount(receipt_dict):
        total_amount = receipt_dict['total']

        # Checks if the total is an even dollar amount. Note this awards 75 points because 
        # Any even dollar amounts will always also be a multiple of .25, so it gets both the 50 points
        # for an even amount and the 25 points for being a multiple of .25.
        if Backend.is_round_dollar(total_amount):
            print("Dollar Amount Points: " + str(75))
            return 75

        # Checks if the total is a multiple of .25
        elif Backend.is_multiple(total_amount):
            print("Dollar Amount Points: " + str(25))
            return 25

        # No points are given if neither of the above conditions are true.
        else:
            print("Dollar Amount Points: " + str(0))
            return 0

    # Gives 5 points for every 2 items on the receipt.
    def points_item_amount(receipt_dict):

        # get the list of items from the receipt
        items_list = receipt_dict['items']

        # take the length of that list
        list_length = len(items_list)

        # divide the length by 2 to get the number of every 2 items on the list.
        # Convert to an int to truncate any decimals in the event of an odd number of items, 
        # then multiply that by 5 points per 2 items and return
        amount_points = (int(list_length / 2)) * 5
        print("Item Amount Points: " + str(amount_points))
        return amount_points

    # Gives points for every item whose name has a number of characters equal to a multiple of 3.
    # Leading and Trailing spaces are not counted.
    def points_item_name_length(receipt_dict):
        total_item_name_points = 0

        # pulls a list of all items and iterates through it, getting the item name and price for each.
        items_list = receipt_dict['items']
        for item in items_list:
            item_name = item['shortDescription']
            item_price = float(item['price'])

            # Removes leading and trailing spaces from the name and checks if the length is a multiple of 3.
            # Award points equal to 20 percent of the item price (rounded up to the nearest point) if so.
            if len(item_name.strip()) % 3 == 0:
                total_item_name_points += math.ceil(item_price * 0.2)
        print("Total Item Name Points: " + str(total_item_name_points))
        return total_item_name_points

    # Gives 6 points if the item was purchased on an odd numbered date, otherwise gives 0 points.
    def points_item_purchase_date(receipt_dict):

        # gets the date from the receipt and creates a datatime object from it.
        purchase_date = receipt_dict['purchaseDate']
        purchase_date_datetime = datetime.strptime(purchase_date, "%Y-%m-%d").date()

        # Checks if the day is odd
        if purchase_date_datetime.day % 2 == 1:
            print("Date Points: " + str(6))
            return 6
        else:
            print("Date Points: " + str(0))
            return 0

    # gives 10 points if the item was purchased between 2PM and 4PM. 
    def points_item_purchase_time(receipt_dict):

        # Gets the time and creates a datetime object
        purchase_time = receipt_dict['purchaseTime']
        purchase_time_datetime = datetime.strptime(purchase_time, "%H:%M").time()

        # Creates 2 additional time objects and measures the purchase time against them.
        minimum_time = time(hour=14)
        maximum_time = time(hour=16)
        if (purchase_time_datetime > minimum_time) and (purchase_time_datetime < maximum_time):
            print("Time Points: " + str(10))
            return 10
        else:
            print("Time Points: " + str(0))
            return 0

    # Returns true if the dollar amount is a whole dollar with .00 cents.
    def is_round_dollar(string_param):

        # try casting as an int to test if param is a whole number
        try:
            int(string_param)
            return True
        except ValueError:

            # if not, iterate through it until you reach the decimal
            for count, char in enumerate(string_param):
                if (char == "."):

                    # slice all digits after the decimal and convert to int
                    remaining_digits = int(string_param[count + 1::])

                    # check their value to see if it matches 0, if yes then the dollar amount has no cents.
                    if remaining_digits == 0:
                        return True

            # otherwise return false
            return False

    # Returns true if the cents are a multiple of .25
    def is_multiple(string_param):

        # iterate through the amount until you reach a decimal
        for count, char in enumerate(string_param):
            if (char == "."):

                # slice all digits after the decimal and remove trailing zeros
                remaining_digits = (string_param[count + 1::]).rstrip('0')

                # convert to an int
                remaining_digits = int(remaining_digits)

                # if that int divided by 100 equals either 0.25, 0.50, or 0.75 return true
                if (remaining_digits / 100 == 0.25) or (remaining_digits / 100 == 0.50) or (
                        remaining_digits / 100 == 0.75):
                    return True

        # otherwise return false
        return False


if __name__ == '__main__':
    # Starts the flask server, running on localHost be default.
    with app.app_context():
        app.run(host='0.0.0.0')
