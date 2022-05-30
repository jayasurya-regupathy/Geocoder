try:
    import unittest
    import requests
    from app import app

except Exception as e:
    print("Some Modules are Missing {}".format(e))

base_url = "http://127.0.0.1:5000/geocoder"
class FlaskTest(unittest.TestCase):
    #Check for 200 response
    def test_positive(self):   
        response = requests.get(base_url, params = {'address':'Coolnakisha, Leighlinbridge, carlow'})
        statuscode = response.status_code
        self.assertEqual(statuscode,200)

    #Check for 400 response
    def test_negative(self):  
        response = requests.get(base_url, params = {'address':''})
        statuscode = response.status_code
        self.assertEqual(statuscode,400)

    #Check for content type - json
    def test_content(self):  
        tester = app.test_client(self)
        response = tester.get(base_url+'?address=Coolnakisha, Leighlinbridge, carlow')
        self.assertEqual(response.content_type,'application/json')

    #Check for returned data
    def test_data(self):  
        tester = app.test_client(self)
        response = tester.get(base_url+'?address=Coolnakisha, Leighlinbridge, carlow')
        self.assertTrue(b'data' in response.data)

    #Check for returned error
    def test_error(self):  
        tester = app.test_client(self)
        response = tester.get(base_url+'?address=')
        self.assertTrue(b'error' in response.data)
if __name__ == "__main__":
    unittest.main()