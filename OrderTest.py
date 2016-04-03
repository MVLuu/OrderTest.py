import unittest
import time
import base64
import uuid
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ContactInformation:
        def __init__(self, firstName=0, lastName=0, address=0, city=0, state=0, postalCode=0, email=0, phone=0):
                self.firstName = firstName
                self.lastName = lastName
                self.address = address
                self.city = city
                self.state = state
                self.postalCode = postalCode
                self.email = email
                self.phone = phone

class OrderTest(unittest.TestCase):

        def setUp(self):
                self.driver = webdriver.Firefox()
                self.driver.get("http://<private site>/en-us/")
                self.ot = OrderTest()

        """
        Test steps:
        1) Visit store.23andme.com/en-us/ 
        2) Add 5 kits and enters unique names for each kit 
        3) Continue to the shipping page and enter a valid US shipping address and other info. 
        4) Continue through the shipping verification page and verifies that the payment page is reached. 

        Verify:
        The general test purpose is to verify that the store website is functioning correctly. 
        In your test, check and assert what you feel to be most important in verifying this. 
        Finally this test must be fully functioning so provide instructions on how to run it. 
        """
        def test_basic_functional(self):

                driver = self.driver
                self.ot.add_test_kit(driver, 5)
                self.ot.add_test_kit_name(driver)
                
                subTotal = self.ot.verify_subTotal(driver)
                saving = self.ot.verify_saving(driver)
                self.ot.verify_total(driver, subTotal, saving)
                
                delay = 25 # seconds
                try:
                        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,".//input[@class='submit button-continue']")))
                        elementContinue = driver.find_element_by_xpath(".//input[@class='submit button-continue']")
                        elementContinue.click()
                except TimeoutException:
                        self.fail("Failed to find button")
                
                elementContinue = None
                while not elementContinue:
                        try:
                                elementContinue = driver.find_element_by_xpath(".//input[@class='submit button-continue']")
                                
                        except NoSuchElementException:
                                time.sleep(2)
                
                
                elementContinue.click()

                contact = ContactInformation("First name", "Last name", "4000 Madison Drive", "SAN JOSE", "California", "90210-0000", "test@test.com", "3217654321")

                self.ot.shipping_information(driver, contact)

                shipToVerifiedAddress = self.driver.find_element_by_xpath(".//input[@class='button-continue']")
                shipToVerifiedAddress.click()

                paymemntTotal = self.driver.find_element_by_class_name("payment-total")
                self.assertEqual(paymemntTotal.text, "Order total: $945.35", "Total not matching expected value.") 

        """
        Test steps:
        1) Visit store.23andme.com/en-us/ 
        2) Add 1 kits and enters unique names for each kit 
        3) Continue to the shipping page and enter an invalid US shipping city.
        
        Verify:
        Check and assert invalid city is detected. 
        """
        def test_invalid_address(self):

                driver = self.driver
                self.ot.add_test_kit(driver, 1)
                self.ot.add_test_kit_name(driver)
                
                delay = 25 # seconds
                try:
                        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,".//input[@class='submit button-continue']")))
                        elementContinue = driver.find_element_by_xpath(".//input[@class='submit button-continue']")
                        elementContinue.click()
                except TimeoutException:
                        self.fail("Failed to find button")
                
                invalidCity = "WASHINGTON DC"
                invalidPostalCode = "99999"
                contact = ContactInformation("First name", "Last name", "4000 Madison Drive", invalidCity, "California", invalidPostalCode, "test@test.com", "5557654321")

                self.ot.shipping_information(driver, contact)

                try:
                        element = driver.find_element_by_xpath(".//input[@value='ship to verified address']")
                except NoSuchElementException:
                        return
                
                self.fail("Failed to catch invalid city")
                
        
        def shipping_information(self, driver, contactInformation):

                firstName = driver.find_element_by_id("id_first_name")
                firstName.send_keys(contactInformation.firstName)

                lastName = driver.find_element_by_id("id_last_name")
                lastName.send_keys(contactInformation.lastName)

                address = driver.find_element_by_id("id_address")
                address.send_keys(contactInformation.address)

                city = driver.find_element_by_id("id_city")
                city.send_keys(contactInformation.city)

                stateDropdown = Select(driver.find_element_by_id("id_state"))
                stateDropdown.select_by_visible_text(contactInformation.state)

                postalCode = driver.find_element_by_id("id_postal_code")
                postalCode.send_keys(contactInformation.postalCode);

                email = driver.find_element_by_id("id_email")
                email.send_keys(contactInformation.email);

                phone = driver.find_element_by_id("id_int_phone")
                phone.send_keys(contactInformation.phone);

                elementContinue = driver.find_element_by_xpath(".//input[@class='submit button-continue']")
                elementContinue.click()

        def add_test_kit_name(self, driver):
                elements = driver.find_elements_by_xpath(".//input[@class='js-kit-name']")
                for element in elements:
                        element.send_keys(str(datetime.datetime.now()) + str(base64.urlsafe_b64encode(uuid.uuid4().bytes)))
                
        def add_test_kit(self, driver, numberOfKits):
                if numberOfKits >= 1:
                        elem = driver.find_element_by_xpath("//*[contains(text(), 'Add a kit.')]")
                        elem.click()
                        
                for i in range(1, numberOfKits):
                        
                        elem = driver.find_element_by_xpath("//img[@alt='Add another kit']")
                        elem.click()

                        
        def verify_total(self, driver, subTotal, saving):
                priceDisplay = driver.find_elements_by_class_name("price-display")
                priceDisplay = float(priceDisplay[2].text.replace("$",""))

                self.assertEqual(float(subTotal) - float(saving), priceDisplay, "Total not matching expected value.") 
                        
                
        def verify_subTotal(self, driver):
                prices = driver.find_elements_by_class_name("price")

                total = 0.00
                for price in prices:
                        value = price.text.replace("$","")
                        current = float(value)
                        total = total + current
                        
                priceTotal = driver.find_element_by_class_name("price-display")
                subTotalValue = priceTotal.text.replace("$","")
                subTotal = float(subTotalValue)

                self.assertEqual(subTotal, total, "SubTotal not matching expected value.")
                return subTotal
                
        
        def verify_saving(self, driver):
                prices = driver.find_elements_by_class_name("price")

                total = 0.00
                
                for i in range(1, len(prices)):
                        value = prices[i].text.replace("$","")
                        current = float(value) * 0.1
                        total = total + current

                total = float(total)
                rountTotal = "%.2f" % total
                
                prices = driver.find_elements_by_class_name("price-display")
                saving = prices[1].text.replace("$","")
                saving = float(saving)
                saving = "%.2f" % saving

                self.assertEqual(saving, rountTotal, "Saving not matching expected value.")
                return saving

        def tearDown(self):
                self.driver.close()

if __name__ == "__main__":
	unittest.main()
