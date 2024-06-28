import time

from selenium import webdriver
from selenium.webdriver.common.by import By

ID = "{아이디}"
PASSWORD = "{비밀번호}"

def wait():
    time.sleep(2)

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
except:
    pass


driver.get("https://www.allteaching.biz/lms/class/student/")
wait()

driver.get("https://www.allteaching.biz/lms/class/set_session.php?ps_id=2608cfdf30839b2cd3ebc60fe65ea6ee@kwto@2024&url=%2Flms%2Fclass%2Fstudent%2Fpage.php%3Fp%3Dcl_lecture")
wait()

lecture_table = driver.find_element(By.XPATH, "/html/body/div/div[3]/div[2]/div[1]/div[3]/div/table").find_element(By.TAG_NAME, "tbody")
tr_list = lecture_table.find_elements(By.TAG_NAME, "tr")
for tr in tr_list:
    td_list = tr.find_elements(By.TAG_NAME, "td")
    count = 0
    for td in td_list:
        if count == 5:
            process_rate = td.find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME, "span").text
            if process_rate == "100%":
                break

        if count == 7:
            td.find_element(By.TAG_NAME, "span").find_element(By.TAG_NAME, "a").click()
            driver.switch_to.window(driver.window_handles[1])
            wait()

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
                    driver.find_element(By.XPATH, "/html/body/div[3]/div[3]/div/button[1]").click()
                else:
                    next_btn.click()
                    current_page = current_page + 1

            driver.switch_to.window(driver.window_handles[0])

        count = count + 1