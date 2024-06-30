import time
import use_chat_gpt as gpt

from selenium import webdriver
from selenium.webdriver.common.by import By

ID = "{아이디}"
PASSWORD = "{비밀번호}"
JOKBO_DIC = gpt.get_jokbo_dic()


def wait():
    time.sleep(2)


def do_test(browser, jokbo):
    wait()
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

    # / html / body / div / div[2] / div[1] / div[3] / a
    browser.find_element(By.XPATH, '/html/body/div/div[2]/div[1]/div[3]/a/span').click()
    wait()

    browser.find_element(By.ID, 'popup_ok').click()
    wait()

    browser.find_element(By.ID, 'popup_ok').click()
    wait()


if __name__ == '__main__':
    driver = webdriver.Chrome()
    driver.maximize_window()

    driver.get("https://www.allteaching.biz/member/login.php")
    wait()

    driver.find_element(By.XPATH, '//*[@id="login_id"]').send_keys(ID)
    driver.find_element(By.XPATH, '//*[@id="login_pw"]').send_keys(PASSWORD)

    driver.find_element(By.ID, "smt_login").click()
    wait()

    try:
        driver.switch_to.alert.accept()
        wait()

        driver.get("https://www.allteaching.biz/member/login.php")
        wait()

        driver.find_element(By.XPATH, '//*[@id="login_id"]').send_keys(ID)
        driver.find_element(By.XPATH, '//*[@id="login_pw"]').send_keys(PASSWORD)

        driver.find_element(By.ID, "smt_login").click()
        wait()

        try:
            driver.switch_to.alert.accept()
        except:
            pass

    except:
        pass

    try:
        driver.get("https://www.allteaching.biz/lms/class/student/")
        wait()

        driver.get("https://www.allteaching.biz/lms/class/set_session.php?ps_id=2608cfdf30839b2cd3ebc60fe65ea6ee@kwto@2024&url=%2Flms%2Fclass%2Fstudent%2Fpage.php%3Fp%3Dcl_lecture")
        wait()

        lecture_table = driver.find_element(By.XPATH, "/html/body/div/div[3]/div[2]/div[1]/div[3]/div/table").find_element(By.TAG_NAME, "tbody")
        tr_list = lecture_table.find_elements(By.TAG_NAME, "tr")
        lecture_number = 0
        for tr in tr_list:
            lecture_number += 1
            td_list = tr.find_elements(By.TAG_NAME, "td")
            rate_td = td_list[5]
            listen_td = td_list[7]
            test_td = td_list[11]
            current_jokbo = JOKBO_DIC[lecture_number]
            process_rate = rate_td.find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME, "span").text
            is_listen_completed = process_rate == "100%"
            is_test_completed = test_td.find_element(By.TAG_NAME, "a").text == "시험완료"

            if is_listen_completed:
                if is_test_completed:
                    continue

                else:
                    test_td.find_element(By.TAG_NAME, "span").find_element(By.TAG_NAME, "a").click()
                    wait()

                    do_test(driver, current_jokbo)
            else:
                try:
                    listen_td.find_element(By.TAG_NAME, "span").find_element(By.TAG_NAME, "a").click()
                    driver.switch_to.window(driver.window_handles[1])
                    wait()

                except:
                    driver.switch_to.alert.accept()
                    wait()

                    td_idx = td_idx + 1
                    continue

                try:
                    driver.find_element(By.ID, "agree_chk_safety").click()
                    driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div/button[1]").click()
                    wait()
                except:
                    pass

                try:
                    driver.switch_to.alert.accept()
                    wait()
                except:
                    pass

                current_page = int(driver.find_element(By.ID, "now").text)
                total_page = int(driver.find_element(By.ID, "total").text)

                while current_page <= total_page:
                    next_btn = driver.find_element(By.ID, "btn_next")
                    btn_cls_nm = next_btn.get_attribute("class")
                    wait()
                    driver.switch_to.frame(driver.find_element(By.ID, "content_frame"))
                    driver.find_element(By.ID, "volume").click()
                    driver.switch_to.default_content()
                    while btn_cls_nm != "btn_next on":
                        btn_cls_nm = driver.find_element(By.ID, "btn_next").get_attribute("class")
                        print(btn_cls_nm)
                        if "btn_last_page" in btn_cls_nm:
                            break

                        time.sleep(10)

                    if "btn_last_page" in btn_cls_nm:
                        try:
                            driver.find_element(By.XPATH, "/html/body/div[3]/div[3]/div/button[1]").click()
                        except:
                            driver.close()
                        finally:
                            break

                    else:
                        next_btn.click()
                        current_page = current_page + 1

                # 회차 끝
                driver.switch_to.window(driver.window_handles[0])

                do_test(driver, current_jokbo)

    except Exception as e:
        print(e)
        driver.close()