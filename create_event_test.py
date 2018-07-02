import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime

@pytest.mark.webtest
class TestCalendar(object):
    @classmethod
    def setup_class(cls):
        cls.driver = webdriver.Chrome()
        cls.driver.switch_to_window(cls.driver.current_window_handle)

    @classmethod
    def teardown_class(cls):
        cls.driver.quit()

    def scroll_element_to_view(self, element):
        self.driver.execute_script("return arguments[0].scrollIntoView();", element)

    def select_popup_item(self, input_label, item_text):
        input_el = self.driver.find_element(By.XPATH, "//input[@aria-label = '%s']" % input_label)
        input_el.click()

        item_el = self.driver.find_element(By.XPATH,
                                      "//input[@aria-label = '%s']/../../../../../../div[@tabindex = -1]//div[contains(text(), '%s')]" % (
                                      input_label, item_text))
        self.scroll_element_to_view(item_el)
        item_el.click()

    def select_autocomplete_popup_item(self, input_label, item_text, type_text):
        input_el = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@aria-label = '%s']" % input_label))
        )
        input_el.click()
        input_el.send_keys(type_text)
        input_el.click()

        item_el = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                                        "//input[@aria-label = '%s']/../../../../../..//div[@role = 'listbox']//div[@role = 'option']//div[contains(text(), '%s')]" % (
                                            input_label, item_text)))
        )

        item_el.click()

        time.sleep(1)

    def test_add_event_to_calendar(self):
        baseUrl = "https://calendar.google.com/calendar/r/month"

        # User credentials
        email = "stanza.test10@gmail.com"
        password = "QWErty654321"

        title = 'Rugby World Cup 7s 2018 - Time %s' % time.time()
        description = "Rugby World Cup 7s 2018 - in San Francisco"
        location_name = "AT&T Park"
        location_address = "24 Willie Mays Plaza, San Francisco, CA 94107, USA"

        self.driver.get(baseUrl)
        self.driver.maximize_window()
        self.driver.implicitly_wait(7)

        # Sign in to Google Calendar
        email_phone = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "identifierId"))
        )
        email_phone.click()
        email_phone.send_keys(email)

        next_button = self.driver.find_element(By.ID, "identifierNext")
        next_button.click()

        password_input = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type = 'password']"))
        )
        password_input.click()
        password_input.send_keys(password)

        password_next = self.driver.find_element(By.ID, "passwordNext")
        password_next.click()

        # Create event
        create_event = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@data-tooltip = 'Create event']"))
        )
        create_event.click()

        add_title = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@aria-label = 'Title']"))
        )
        add_title.click()
        add_title.send_keys(title)

        start_date = "20"
        start_time = "10:00am"
        end_time = "10:00pm"
        end_date = "21"

        self.select_popup_item("Start date", start_date)
        self.select_popup_item("Start time", start_time)
        self.select_popup_item("End time", end_time)
        self.select_popup_item("End date", end_date)

        self.select_autocomplete_popup_item("Location", location_name, "att")

        add_description = self.driver.find_element(By.XPATH, "//div[@aria-label = 'Description']")
        add_description.click()
        add_description.send_keys(description)

        save_event = self.driver.find_element(By.XPATH, "//div[@aria-label = 'Save']")
        save_event.click()

        time.sleep(1)
        # Finding of just created event
        event_added = self.driver.find_element(By.XPATH, "(//div[@role = 'gridcell']//div[@role = 'presentation']//html-blob[contains(text(), '%s')])[1]" % title)
        event_added.click()

        # Checking the title name
        event_dialog_selector = "//div[@id = 'xDetDlg']"
        event_title = self.driver.find_element(By.XPATH, event_dialog_selector + "//span[@role = 'heading']").text
        assert event_title == title

        # Checking event date and time
        event_dialog_date = self.driver.find_element(By.XPATH, event_dialog_selector + "//div[@id = 'xDetDlgWhen']").text

        current_month = datetime.datetime.now().strftime("%B")
        current_year = datetime.datetime.now().year
        expected_date = "%s %s, %s, %s – %s %s, %s, %s" % (current_month, start_date, current_year, start_time, current_month, end_date, current_year, end_time)

        assert event_dialog_date == expected_date

        # Checking event dialog description
        event_dialog_description = self.driver.find_element(By.XPATH, event_dialog_selector + "//div[@id = 'xDetDlgDesc']").text
        event_dialog_description = event_dialog_description.replace("Description:\n", "")

        assert event_dialog_description == description

        # Checking event location
        event_dialog_location = self.driver.find_element(By.XPATH, event_dialog_selector + "//div[@id = 'xDetDlgLoc']").text
        assert event_dialog_location == "%s\n%s" % (location_name, location_address)


