####################################
# COMPANY: Quokka
# AUTHOR: Scott Mercer
#         
# Requires
# Appium v2.5.1 (distribution)
# Python 3.11 & Appium-Python-Client 3.2.1

from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_actions import PointerActions
from typing import Tuple, TypeVar
import enum
import unittest
import time


# HELPERS / BASE 

T = TypeVar("T")
Locator = Tuple[By, str]

class ScrollDirection(enum.Enum):
    down = enum.auto()
    left = enum.auto()
    right = enum.auto()
    up = enum.auto()

class nonzero_size(object):
    def __init__(self, el: WebElement) -> "nonzero_size":
        self.el = el

    def __call__(self, driver: webdriver.Remote):
        rect = self.el.rect
        return rect["width"] != 0 and rect["height"] != 0


class has_url_text(object):
    def __init__(self: "has_url_text", el: WebElement) -> "has_url_text":
        self.el = el

    def __call__(self: "has_url_text", driver: webdriver.Remote):
        text: str = self.el.get_attribute("value")
        return text.startswith("http")


class BasePage(object):
    def __init__(self: "BasePage", driver: webdriver.Remote) -> "BasePage":
        self.driver = driver
        self._wait = WebDriverWait(driver, 60)
        self._short_wait = WebDriverWait(driver, 3)
        self._long_wait = WebDriverWait(driver, 60)

    def wait(
        self: "BasePage", locator: Locator, waiter: WebDriverWait = None
    ) -> WebElement:
        if waiter is None:
            waiter = self._wait
        return waiter.until(EC.presence_of_element_located(locator))

    def short_wait(self: "BasePage", locator: Locator) -> WebElement:
        return self.wait(locator, waiter=self._short_wait)

    def long_wait(self: "BasePage", locator: Locator) -> WebElement:
        return self.wait(locator, waiter=self._long_wait)

    def long_wait(self: "BasePage", locator: Locator) -> WebElement:
        return self.wait(locator, waiter=self._long_wait)
    
    def wait_for_nonzero_size(self: "BasePage", locator: Locator) -> WebElement:
        el = self.wait(locator)
        self._wait.until(nonzero_size(el))
        return el

    def wait_for_url(self: "BasePage", locator: Locator) -> str:
        el = self.wait(locator)
        self._wait.until(has_url_text(el))
        return el.get_attribute("value")

    def tap_at(self: "BasePage", x: int, y: int) -> None:
        actions = ActionBuilder(self.driver)
        p = actions.add_pointer_input("touch", "finger")
        p_actions = PointerActions(p)
        p.create_pointer_move(duration=0, x=x, y=y, origin="viewport")
        p_actions.pointer_down()
        p_actions.pause(0.2)
        p_actions.pointer_up()
        actions.perform()

    def tap_el(self: "BasePage", el: WebElement) -> None:
        rect = el.rect
        x = rect["x"] + (rect["width"] / 2)
        y = rect["y"] + (rect["height"] / 2)
        self.tap_at(x, y)

    def tap_el_at(self: "BasePage", el: WebElement, x_pct: float, y_pct: float) -> None:
        rect = el.rect
        x = rect["x"] + (rect["width"] * x_pct)
        y = rect["y"] + (rect["height"] * y_pct)
        self.tap_at(x, y)

    def swipe_by_pixels(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration_ms: int = 1500,
    ) -> None:
        actions = ActionBuilder(self.driver)
        p = actions.add_pointer_input("touch", "finger1")
        p_actions = PointerActions(p)
        p.create_pointer_move(duration=0, x=start_x, y=start_y, origin="viewport")
        # TODO make cross platform
        p_actions.pointer_down()
        p.create_pointer_move(duration=duration_ms, x=end_x, y=end_y, origin="viewport")
        p_actions.pause(duration=duration_ms / 1000)
        p_actions.pointer_up()
        actions.perform()

    def swipe(
        self,
        relative_start_x: float,
        relative_start_y: float,
        relative_end_x: float,
        relative_end_y: float,
        duration_ms: int = 200,
    ) -> None:
        size = self.driver.get_window_size()
        width = size["width"]
        height = size["height"]
        start_x = int(width * relative_start_x)
        start_y = int(height * relative_start_y)
        end_x = int(width * relative_end_x)
        end_y = int(height * relative_end_y)
        self.swipe_by_pixels(start_x, start_y, end_x, end_y, duration_ms)

    def swipe_in_el(
        self,
        el: WebElement,
        relative_start_x: float = 0.5,
        relative_start_y: float = 0.5,
        relative_end_x: float = 0.5,
        relative_end_y: float = 0.5,
        duration_ms: int = 200,
    ) -> None:
        rect = el.rect
        start_x = rect["x"] + (rect["width"] * relative_start_x)
        start_y = rect["y"] + (rect["height"] * relative_start_y)
        end_x = rect["x"] + (rect["width"] * relative_end_x)
        end_y = rect["y"] + (rect["height"] * relative_end_y)
        self.swipe_by_pixels(start_x, start_y, end_x, end_y, duration_ms)

    def scroll(
        self, direction: ScrollDirection, amount: float = 0.5, duration_ms: int = 500
    ) -> None:
        relative_start_x = 0.5
        relative_start_y = 0.5
        relative_end_x = 0.5
        relative_end_y = 0.5
        if direction == ScrollDirection.down:
            relative_start_y += amount / 2
            relative_end_y -= amount / 2
        elif direction == ScrollDirection.up:
            relative_start_y -= amount / 2
            relative_end_y += amount / 2
        elif direction == ScrollDirection.left:
            relative_start_x -= amount / 2
            relative_end_x += amount / 2
        elif direction == ScrollDirection.right:
            relative_start_x += amount / 2
            relative_end_x -= amount / 2
        else:
            raise ValueError("Scroll direction is not valid")
        self.swipe(
            relative_start_x,
            relative_start_y,
            relative_end_x,
            relative_end_y,
            duration_ms,
        )

    def scroll_to(
        self,
        locator: Locator,
        max_scrolls: int = 10,
        direction: ScrollDirection = ScrollDirection.down,
    ) -> WebElement:
        first_scroll = True
        scrolls = 0
        while scrolls < max_scrolls:
            try:
                if first_scroll:
                    # first time through the loop of scrolling, do an actual wait in case the
                    # element is already on the screen
                    first_scroll = False
                    return self.short_wait(locator)
                return self.driver.find_element(*locator)
            except NoSuchElementException:
                self.scroll(direction)
            scrolls += 1
        raise NoSuchElementException(
            f"Could not find element after {max_scrolls} scrolls"
        )
    
## CAPABILITIES / DRIVER INFORMATION
    
capabilities = dict(
    platformName='Android',
    automationName='uiautomator2',
    deviceName='Android',
    # deviceId='emulator-5554',
    deviceId='RF8X309MLKK',
    language='en',
    locale='US',
    noReset=True,
    autoLaunch=False
)

appium_server_url = 'http://localhost:4723'

capabilities_options = UiAutomator2Options().load_capabilities(capabilities)

## TEST CLASS / CASES
class TestAppium(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = webdriver.Remote(command_executor=appium_server_url, options=capabilities_options)
        self.basePage = BasePage(self.driver)

    def tearDown(self) -> None:
        if self.driver:
            self.driver.terminate_app('nl.nn.retailapp')
            self.driver.quit()

    def test_launch_app(self) -> None:
        ACCEPT = (By.XPATH, '//android.widget.TextView[@text="Aan de slag!"]')
        NEXT = (By.XPATH, '//android.widget.TextView[@text="Ja, en ik wil de app activeren"]')
        CHECKBOX = (By.ID, 'checkbox')
        FORWARD = (By.XPATH, '//android.widget.TextView[@text="Opslaan"]')
        USERNAME = (By.XPATH, '//android.widget.EditText[@content-desc="Gebruikersnaam"]')
        PASSWORD = (By.XPATH, '//android.widget.EditText[@content-desc="Wachtwoord"]')
        LOGIN = (By.XPATH, '//android.widget.Button[@content-desc="Inloggen"]')
        
        self.driver.activate_app('nl.nn.retailapp')

        try:
            self.basePage.wait(ACCEPT).click()
            self.basePage.wait(NEXT).click()
            self.basePage.short_wait(CHECKBOX).click()
            self.basePage.short_wait(FORWARD).click()
        except Exception as e:
            print(f"Element not found")
            pass
        
        self.basePage.wait(USERNAME).send_keys('smercer@quokka.io')
        self.basePage.wait(PASSWORD).send_keys('test123')
        self.basePage.wait(LOGIN).click()
        


## MAIN FUNCTION
if __name__ == '__main__':
    unittest.main()