from datetime import datetime as dtm
import random
import re
import string
import time

# Selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from FileTranslator.Translator.ITranslator import ITranslator
import FileTranslator.Util.Logs as Logs
from FileTranslator.Util.PathInfo import PathInfo
from FileTranslator.Util.TranslateInfo import TranslateInfo

################################################################################

# Variables

timeout = 20
default_pause = 2
text_translation_pause = 0.5

pause_between_download = 1
small_request_pause = 0.3
wait_request_handle = 1


################################################################################

# static functions


def _rand_condition(probability: float = 50.0) -> bool:
    return random.uniform(0, 100) < probability


def _browser_options() -> Options:
    # Create options.
    options = Options()
    # Standard options.
    options.add_argument("headless")  # disable interactive mode
    options.add_argument("page_load_strategy=normal")
    options.add_argument("start-maximized")
    options.add_argument("incognito")
    options.add_argument("disable-infobars")
    options.add_argument("disable-popup-blocking")

    # Custom options.
    # prefs = {'download.default_directory': download_dir}
    # options.add_experimental_option("prefs", prefs)

    return options


def waiting_sleep(sec):
    Logs.dev(f"waiting {sec} sec")
    time.sleep(sec)
    Logs.dev(f"finished waiting")


################################################################################

# delays


def _time_before_start() -> float:
    return random.uniform(2.5, 3.5)


def _time_before_fake_action() -> float:
    return random.uniform(2, 3)


def _time_before_send() -> float:
    return random.uniform(1, 2)


def _time_before_retry() -> float:
    return random.uniform(2, 3)


def _time_fake_action_word() -> float:
    return random.uniform(0.5, 1.5)


def _time_fake_action_text() -> float:
    return random.uniform(0.5, 1.5)


def _time_to_vote() -> float:
    return random.uniform(2, 3)


def _time_to_reopen_browser() -> float:
    return 5.0


def _get_pages_before_action() -> int:
    return random.randint(5, 8)


################################################################################

# class YandexOnlineTranslator


class YandexOnlineTranslator(ITranslator):
    # Exceptions

    class TranslationTimeOut(Exception):
        pass

    ############################################################################

    # API

    def __init__(self):
        pass

    def init(self, path_info: PathInfo, translate_info: TranslateInfo) -> None:
        self.src_lang = translate_info.src_lang
        self.trg_lang = translate_info.trg_lang
        self._set_web_page()
        self._open_browser()
        self.fake_text_list = open(path_info.fake_text_path).read().split(" ")
        self.pages_before_fake_action = _get_pages_before_action()

    def set_source_language(self, language: str) -> None:
        self.src_lang = language
        self._set_web_page()

    def set_target_language(self, language: str) -> None:
        self.trg_lang = language
        self._set_web_page()

    def translate(self, to_translate: str) -> str:
        # prerequisites
        if len(to_translate) == 0:
            return ""
        self.src = to_translate
        self._prepare_send_text()

        # send text
        self._send_text()

        # wait text to be translated
        budget = timeout
        while not self._translation_ready():
            if budget < 0:
                if self._retry_attempt():
                    budget = timeout
                else:
                    raise YandexOnlineTranslator.TranslationTimeOut
            time.sleep(text_translation_pause)

        # get translated text in html
        elem = WebDriverWait(self.browser, timeout).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, self.selector.OUTPUT_DATA)
            ),
            "Unable to find 'OUTPUT_DATA'",
        )
        self.trg = elem.get_attribute("innerHTML")

        # extract translated text from html
        self._convert_from_html()

        if _rand_condition(15):
            self._vote()

        # reset variables
        res = self.trg
        self._reset_after_translation()
        return res

    def reset(self) -> None:
        self.src = self.trg = ""
        self.browser.close()
        Logs.user(f"Reopening browser")
        waiting_sleep(5)
        self._open_browser()

    ############################################################################

    # Internals

    class Selector:
        INPUT_DATA = "#fakeArea"
        OUTPUT_DATA = "#translation > span"
        TRANS_STATUS = "#app"
        INPUT_AREA = "#fakeArea"
        OUTPUT_AREA = "#translation"
        RETRY = (
            "#textbox2 > div.box-dstMessages >"
            "div.dstMsg.dstMsg_alert.dstMsg_translateFail > button"
        )
        CLEAR_BUTTON = "#clearButton"
        GOOD_VOTE = "#goodVoteButton"
        BAD_VOTE = "#badVoteButton"
        SRC_LANG = "#srcLangButton"
        AUTO_DETECT = (
            "#langSelect > div.langs-searchPanel >"
            "div.langs-autoLangSwitcher > div"
        )

    def _open_browser(self):
        self.browser = webdriver.Chrome(options=_browser_options())

        self.browser.get(self.web_page)
        self._update_timestamp()

        self._disable_auto_detect_language()

        self.pages_before_fake_action = _get_pages_before_action()

    def _set_web_page(self) -> None:
        self.web_page = (
            "https://translate.yandex.com/"
            f"?source_lang={self.src_lang}"
            f"&target_lang={self.trg_lang}"
        )

    def _update_timestamp(self) -> None:
        self.last_request_timestamp = dtm.now()

    def _pause_after_last_request(self, to_wait: float = default_pause) -> None:
        dif = (dtm.now() - self.last_request_timestamp).total_seconds()
        if dif < to_wait:
            dif = to_wait - dif
            Logs.dev(f"Pause after previous request: {dif:.2f} sec ...")
            time.sleep(dif)
            Logs.dev(f"Pause finished")

    def _try_find_elem(self, elem_nm: str, budget: float) -> (bool, WebElement):
        pause = 0.5
        while budget > 0:
            try:
                elem = self.browser.find_element(By.CSS_SELECTOR, elem_nm)
                return True, elem
            except:
                time.sleep(pause)
                budget -= pause
        return False, WebElement(0, 0)

    def _make_request(self, action, to_wait: float = default_pause) -> None:
        self._pause_after_last_request(to_wait)
        action()
        self._update_timestamp()

    def _prepare_send_text(self) -> None:
        # fake actions to cheat system
        self._make_fake_action()
        self._clear_input()

    def _clear_input(self):
        # remove input text or load start web page
        try:
            # language could change because of
            if self.web_page not in self.browser.current_url:
                raise Exception
            elem = self.browser.find_element(
                By.CSS_SELECTOR, self.selector.CLEAR_BUTTON
            )
            self._make_request(lambda: elem.click(), _time_before_start())
            Logs.dev("YandexTranslator: input cleared")
        except:
            self._make_request(
                lambda: self.browser.get(self.web_page), _time_before_start()
            )
            Logs.dev("YandexTranslator: can't clear input, reload page")

    def _make_fake_action(self) -> None:
        # action not required
        if self.pages_before_fake_action > 0:
            self.pages_before_fake_action -= 1
            return

        # update counter
        self.pages_before_fake_action = _get_pages_before_action()
        list_len = len(self.fake_text_list)

        # sleep some time before previous actions
        self._make_request(lambda: 0, _time_before_fake_action())

        if _rand_condition():
            self._clear_input()

        # start action
        if _rand_condition():
            # enter word
            word = self.fake_text_list[random.randint(0, list_len - 1)]
            # trick to cheat the system
            self._move_and_click(self.selector.INPUT_AREA, 2)
            input_elem = WebDriverWait(self.browser, timeout).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.selector.INPUT_DATA)
                ),
                "Unable to find 'INPUT_DATA'",
            )
            self._make_request(
                lambda: input_elem.send_keys(word), _time_fake_action_word()
            )
            if _rand_condition():
                return

            # enter one more word
            word = " " + self.fake_text_list[random.randint(0, list_len - 1)]
            self._make_request(
                lambda: input_elem.send_keys(word), _time_fake_action_word()
            )
            # randomly change order
            if _rand_condition():
                self._move_and_click(self.selector.INPUT_AREA, 1)
                self._move_and_click(self.selector.OUTPUT_AREA, 1)
            else:
                self._move_and_click(self.selector.OUTPUT_AREA, 1)
                self._move_and_click(self.selector.INPUT_AREA, 1)
        else:
            # enter text
            start = random.randint(0, list_len // 2)
            finish = random.randint(start + 1, list_len - 1)
            text = self.fake_text_list[start:finish]
            text = " ".join(text)
            input_elem = WebDriverWait(self.browser, timeout).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.selector.INPUT_DATA)
                ),
                "Unable to find 'INPUT_DATA'",
            )
            self._move_and_click(self.selector.INPUT_AREA, 2)
            self.browser.execute_script(
                "arguments[0].value=arguments[1]", input_elem, text
            )
            self._make_request(
                lambda: input_elem.send_keys(" "), _time_fake_action_text()
            )

    def _send_text(self) -> None:
        # find input element
        input_elem = WebDriverWait(self.browser, timeout).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, self.selector.INPUT_DATA)
            ),
            "Unable to find 'INPUT_DATA'",
        )

        # trick to cheat the system
        if _rand_condition():
            self._move_and_click(self.selector.INPUT_AREA)

        # paste text
        self.browser.execute_script(
            "arguments[0].value=arguments[1]", input_elem, self.src
        )

        # put enter to reformat text appropriately
        self._make_request(
            lambda: input_elem.send_keys(Keys.ENTER), _time_before_send()
        )

        # trick to cheat the system
        if _rand_condition():
            self._move_and_click(self.selector.OUTPUT_AREA)

    def _move_and_click(
        self, css_path: str, to_wait: float = default_pause
    ) -> None:
        # move cursor and enter to cheat the system
        elem = self.browser.find_element(By.CSS_SELECTOR, css_path)
        action = ActionChains(self.browser)
        action.move_to_element(elem).click()
        self._make_request(lambda: action.perform(), to_wait)

    def _retry_attempt(self) -> bool:
        try:
            elem = self.browser.find_element(
                By.CSS_SELECTOR, self.selector.RETRY
            )
            self._make_request(lambda: elem.click(), _time_before_retry())
            return True
        except:
            return False

    def _vote(self) -> None:
        try:
            button = self.browser.find_element(
                By.CSS_SELECTOR, self.selector.GOOD_VOTE
            )
            self._make_request(lambda: button.click(), _time_to_vote())
            Logs.dev("YandexTranslator: vote done")
        except:
            Logs.dev("YandexTranslator: vote failed")
            pass

    def _disable_auto_detect_language(self):
        try:
            button = self.browser.find_element(
                By.CSS_SELECTOR, self.selector.SRC_LANG
            )
            self._make_request(lambda: button.click(), 1)
            switcher = self.browser.find_element(
                By.CSS_SELECTOR, self.selector.AUTO_DETECT
            )
            self._make_request(lambda: switcher.click(), 1)
            escape = ActionChains(self.browser).send_keys(Keys.ESCAPE)
            self._make_request(lambda: escape.perform(), 1)
        except:
            Logs.dev(
                "YandexTranslator: Unable to disable auto detection of language"
            )

    def _translation_ready(self) -> bool:
        elem = self.browser.find_element(
            By.CSS_SELECTOR, self.selector.TRANS_STATUS
        )
        return "state-has_translation" in elem.get_attribute("class").split(" ")

    def _convert_from_html(self) -> None:
        # remove all <span> tags
        Logs.dev(f"YandexTranslator, html code:\n{self.trg}\n-------")
        self.trg = re.sub("<span.*?>((?:.|\n)*?)</span>", "\g<1>", self.trg)
        Logs.dev(f"YandexTranslator, converted html code:\n{self.trg}\n-------")
        # move leading punctuation marks to previous line
        self.trg = re.sub(
            f"([^\n])\n([{string.punctuation}]) ([^\n])",
            "\g<1>\g<2>\n\g<3>",
            self.trg,
        )

    def _reset_after_translation(self) -> None:
        self.src = self.trg = ""

    # member fields
    selector = Selector

    web_page: str
    browser: webdriver.Chrome
    last_request_timestamp: dtm
    src: str  # current text to translate
    trg: str  # current text to translate
    pages_before_fake_action: int
    fake_text_list: list[str]
