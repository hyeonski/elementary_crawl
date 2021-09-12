from selenium import webdriver

driver = webdriver.Chrome('./chromedriver')
driver.get("https://seo2.sen.es.kr")

driver.get("https://seo2.sen.es.kr/78584/subMenu.do")


def click_notice(driver, index, list_size):
    if (index == list_size):
        return
    a_list = driver.find_element_by_xpath('//*[@id="board_area"]/table/tbody').find_elements_by_tag_name('a')
    a_list[index].click()
    driver.implicitly_wait(1)

    title = driver.find_element_by_xpath('//*[@id="board_area"]/table/tbody/tr[2]/td/div')
    print(title.text)
    driver.find_element_by_xpath('//*[@id="list_btn"]').click()
    click_notice(driver, index + 1, list_size)

def load_notice_list(driver, index, list_size):
    if (index == list_size - 2):
        return

    a_list = driver.find_element_by_xpath('//*[@id="board_area"]/div[4]').find_elements_by_tag_name('a')
    a_list[index].click()

    a_list = driver.find_element_by_xpath('//*[@id="board_area"]/table/tbody').find_elements_by_tag_name('a')
    click_notice(driver, 0, len(a_list))
    load_notice_list(driver, index + 1, list_size)

def load_next_page(driver):
    while True:
        a_list = driver.find_element_by_xpath('//*[@id="board_area"]/div[4]').find_elements_by_tag_name('a')
        last_page = a_list[len(a_list) - 3].text

        load_notice_list(driver, 2, len(a_list))

        a_list = driver.find_element_by_xpath('//*[@id="board_area"]/div[4]').find_elements_by_tag_name('a')
        a_list[len(a_list) - 2].click()

        a_list = driver.find_element_by_xpath('//*[@id="board_area"]/div[4]').find_elements_by_tag_name('a')
        if (last_page == a_list[len(a_list) - 3].text):
            break

load_next_page(driver)

