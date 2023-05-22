import requests

class BackendTest:

    def __init__(self):
        self.test_json = {
                        "retailer": "Target",
                        "purchaseDate": "2022-01-01",
                        "purchaseTime": "13:01",
                        "items": [
                            {
                            "shortDescription": "Mountain Dew 12PK",
                            "price": "6.49"
                            },{
                            "shortDescription": "Emils Cheese Pizza",
                            "price": "12.25"
                            },{
                            "shortDescription": "Knorr Creamy Chicken",
                            "price": "1.26"
                            },{
                            "shortDescription": "Doritos Nacho Cheese",
                            "price": "3.35"
                            },{
                            "shortDescription": "   Klarbrunn 12-PK 12 FL OZ  ",
                            "price": "12.00"
                            }
                        ],
                        "total": "35.35"
                        }
        
        self.test_json2 = {
                        "retailer": "M&M Corner Market",
                        "purchaseDate": "2022-03-20",
                        "purchaseTime": "14:33",
                        "items": [
                            {
                            "shortDescription": "Gatorade",
                            "price": "2.25"
                            },{
                            "shortDescription": "Gatorade",
                            "price": "2.25"
                            },{
                            "shortDescription": "Gatorade",
                            "price": "2.25"
                            },{
                            "shortDescription": "Gatorade",
                            "price": "2.25"
                            }
                        ],
                        "total": "9.00"
                        }

    def post_test(self, json_param):
        response = requests.post('http://127.0.0.1:5000/receipts/process', json=json_param)
        return response

    def get_test(self, uuid):
        response = requests.get(f'http://127.0.0.1:5000/receipts/{uuid}/points') 
        return response


if __name__ == '__main__':

    test = BackendTest()
    
    response = test.post_test(test.test_json)
    responsejson = response.json()
    print(response)
    print(response.json())
    print()

    response2 = test.get_test(responsejson['id'])
    print(response2)
    print(response2.json())
    print()

    response = test.post_test(test.test_json2)
    responsejson = response.json()
    print(response)
    print(response.json())
    print()

    response2 = test.get_test(responsejson['id'])
    print(response2)
    print(response2.json())
    print()

    