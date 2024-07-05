import time
import use_chat_gpt as gpt
import os
import re


from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from datetime import date

load_dotenv()

ID = os.environ.get("ID")
PASSWORD = os.environ.get("PASSWORD")
JOKBO_DIC = gpt.get_jokbo_dic()


def get_date_by_pattern(str):
    pattern = r'\b\d{4}-\d{2}-\d{2}\b'
    matches = re.findall(pattern, str)

    return datetime.strptime(matches[0], '%Y-%m-%d').date()


def wait():
    time.sleep(2)


# 시험보기
def do_test(browser, jokbo):
    browser.find_element(By.ID, "exam_agree_check").click()
    browser.find_element(By.XPATH, '/html/body/div/div/div/div/span[2]/input').click()

    try:
        browser.switch_to.alert.accept()
        wait()

    except:
        pass

    time.sleep(5)

    exam_list = browser.find_element(By.ID, 'exam_list').find_elements(By.CLASS_NAME, 'exam_area')
    for exam in exam_list:
        question = exam.find_element(By.CLASS_NAME, 'exam_q').text

        choice_list = exam.find_element(By.CLASS_NAME, 'exam_a').find_elements(By.TAG_NAME, 'a')
        for choice in choice_list:
            question = question + choice.text + '\n'

        question = question + '번호로만 대답해 줘'
        gpt_answer = int(gpt.ask_to_chat_gpt(jokbo, question))

        choice_list[gpt_answer - 1].click()

    browser.find_element(By.XPATH, '/html/body/div/div[2]/div[1]/div[3]/a/span').click()
    wait()

    browser.find_element(By.ID, 'popup_ok').click()
    wait()

    browser.find_element(By.ID, 'popup_ok').click()
    wait()


# 로그인
def login_site(browser):
    browser.get("https://www.allteaching.biz/member/login.php")
    wait()

    browser.find_element(By.XPATH, '//*[@id="login_id"]').send_keys(ID)
    browser.find_element(By.XPATH, '//*[@id="login_pw"]').send_keys(PASSWORD)

    browser.find_element(By.ID, "smt_login").click()
    wait()

    try:
        browser.switch_to.alert.accept()
        wait()

        browser.get("https://www.allteaching.biz/member/login.php")
        wait()

        browser.find_element(By.XPATH, '//*[@id="login_id"]').send_keys(ID)
        browser.find_element(By.XPATH, '//*[@id="login_pw"]').send_keys(PASSWORD)

        browser.find_element(By.ID, "smt_login").click()
        wait()

        try:
            browser.switch_to.alert.accept()
        except:
            pass

    except:
        pass


# 강의현황으로 이동
def move_to_my_lecture(browser):
    browser.get("https://www.allteaching.biz/lms/class/student/")
    wait()


# 미수료 강의 시작
def start_my_lecture(browser):
    finished = False

    lecture_table = browser.find_element(By.CLASS_NAME, 'statusWrap').find_element(By.TAG_NAME, 'table')
    lecture_list = lecture_table.find_elements(By.TAG_NAME, 'tr')
    lecture_count = len(lecture_list)
    for i in range(1, lecture_count):
        td_list = lecture_list[i].find_elements(By.TAG_NAME, 'td')

        duration = td_list[2]
        is_status_progressing = "진행중" in td_list[3].text
        is_finished = "미수료" == td_list[8].text

        if is_in_progress(duration) and is_status_progressing and is_finished:
            td_list[9].find_element(By.TAG_NAME, 'a').click()

            while finished is False:
                finished = do_process(browser)

            move_to_my_lecture(driver)
            return False

    return True


# 강의시험 클릭
def click_lecture_test(browser, lecture_number):
    (browser.find_element(By.XPATH, "/html/body/div/div[3]/div[2]/div[1]/div[3]/div/table")
     .find_element(By.TAG_NAME, "tbody")
     .find_elements(By.TAG_NAME, "tr")[lecture_number - 1]
     .find_elements(By.TAG_NAME, "td")[11]
     .find_element(By.TAG_NAME, "span")
     .find_element(By.TAG_NAME, "a").click())
    wait()


# 강의 듣기 - 시험 - 평가를 포함한 모든 과정
def do_process(browser):
    lecture_table = browser.find_element(By.XPATH, "/html/body/div/div[3]/div[2]/div[1]/div[3]/div/table").find_element(
        By.TAG_NAME, "tbody")
    tr_list = lecture_table.find_elements(By.TAG_NAME, "tr")
    lecture_number = 0
    for tr in tr_list:
        lecture_number += 1
        td_list = tr.find_elements(By.TAG_NAME, "td")
        rate_td = td_list[5]
        listen_td = td_list[7]
        test_td = td_list[11]
        current_jokbo = JOKBO_DIC[lecture_number]
        process_rate = rate_td.find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME, "div").find_element(
            By.TAG_NAME, "span").text
        is_listen_completed = process_rate == "100%"
        is_test_completed = test_td.find_element(By.TAG_NAME, "a").text == "시험완료"

        if is_listen_completed:
            if is_test_completed:
                continue

            else:
                click_lecture_test(browser, lecture_number)
                evaluation_lecture(browser)
                do_test(browser, current_jokbo)
                return False
        else:
            try:
                listen_td.find_element(By.TAG_NAME, "span").find_element(By.TAG_NAME, "a").click()
                browser.switch_to.window(browser.window_handles[1])
                wait()

            except:
                browser.switch_to.alert.accept()
                wait()
                continue

            try:
                before_video_btn = browser.find_element(By.XPATH, "/html/body/div[1]/div[3]/div/button")
                if before_video_btn.text == '사전영상 보기':
                    before_video_btn.click()
                    time.sleep(120)
            except:
                pass

            try:
                browser.find_element(By.ID, "agree_chk_safety").click()
                browser.find_element(By.XPATH, "/html/body/div[1]/div[3]/div/button[1]").click()
                wait()
            except:
                pass

            try:
                browser.switch_to.alert.accept()
                wait()
            except:
                pass

            current_page = int(browser.find_element(By.ID, "now").text)
            total_page = int(browser.find_element(By.ID, "total").text)

            while current_page <= total_page:
                next_btn = browser.find_element(By.ID, "btn_next")
                btn_cls_nm = next_btn.get_attribute("class")
                wait()
                browser.switch_to.frame(browser.find_element(By.ID, "content_frame"))
                browser.find_element(By.ID, "volume").click()
                browser.switch_to.default_content()
                while btn_cls_nm != "btn_next on":
                    btn_cls_nm = browser.find_element(By.ID, "btn_next").get_attribute("class")
                    print(btn_cls_nm)
                    if "btn_last_page" in btn_cls_nm:
                        break

                    time.sleep(10)

                if "btn_last_page" in btn_cls_nm:
                    try:
                        time.sleep(20)
                        browser.find_element(By.XPATH, "/html/body/div[3]/div[3]/div/button[2]").click()
                    except:
                        browser.close()
                    finally:
                        browser.switch_to.window(browser.window_handles[0])
                        break

                else:
                    next_btn.click()
                    current_page = current_page + 1

            # 회차 끝
            click_lecture_test(browser, lecture_number)
            evaluation_lecture(browser)
            do_test(browser, current_jokbo)
            return False

    return True


# 강의 평가
def evaluation_lecture(browser):
    try:
        if "강의평가설문을 작성해주세요" in browser.switch_to.alert.text:
            browser.switch_to.alert.accept()
            wait()

            table = browser.find_element(By.NAME, 'fwrite').find_element(By.TAG_NAME, 'table')
            survey_div = table.find_elements(By.CLASS_NAME, 'evaluation_radio_b')
            survey_text = table.find_elements(By.TAG_NAME, 'textarea')
            for survey in survey_div:
                if "매우그렇다" in survey.find_element(By.TAG_NAME, 'label').text:
                    survey.find_element(By.TAG_NAME, 'input').click()

            for survey in survey_text:
                survey.send_keys("-")

            browser.find_element(By.ID, 'btn_submit').click()
            wait()

            buttons = browser.find_elements(By.TAG_NAME, 'button')
            for button in buttons:
                if "시험응시" in button.text:
                    button.click()

            wait()

    except:
        return


def is_in_progress(duration):
    span_list = duration.find_elements(By.TAG_NAME, 'span')
    start_date = get_date_by_pattern(span_list[0].text)
    end_date = get_date_by_pattern(span_list[1].text)

    today = date.today()

    return start_date <= today <= end_date


if __name__ == '__main__':
    driver = webdriver.Chrome()
    driver.maximize_window()

    login_site(driver)

    try:
        # 강의로 이동
        move_to_my_lecture(driver)
        finish = False
        while finish is False:
            finish = start_my_lecture(driver)

    except Exception as e:
        print(e)
        driver.close()
        os.system('taskkill /f /im chromedriver.exe')