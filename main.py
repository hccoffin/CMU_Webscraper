import time
import getpass
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import json

def init_driver():
    driver = webdriver.Chrome()
    return driver

def login(driver, user, password):
    driver.get("http://www.cmu.edu/hub/sio")
    userInput = driver.find_element_by_id('j_username')
    passInput = driver.find_element_by_id('j_password')
    userInput.send_keys(user)
    passInput.send_keys(password)
    passInput.send_keys(Keys.RETURN)

def navigateToPlanSchedule(driver):
    schedule = driver.find_element_by_id('gwt-uid-7')
    hover = ActionChains(driver).move_to_element(schedule)
    hover.perform()
    time.sleep(1)
    planSchedule = driver.find_element_by_id('gwt-uid-9')
    planSchedule.click()
    time.sleep(1)
    addClass = driver.find_element_by_link_text('Search for a course to add')
    addClass.click()

def searchForCourse(driver, course):
    searchBar = driver.find_element_by_css_selector('.input-txt.float-left')
    searchBar.send_keys(course)
    searchBar.send_keys(Keys.RETURN)

def getCourseInfo(driver, course):
    searchForCourse(driver, course)
    time.sleep(1.5)

    courseElement = driver.find_element_by_css_selector('.grid.course-description-sections-tbl')
    html = courseElement.get_attribute('outerHTML')
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.find_all("div", class_="txt display-inline")

    try:
        # goes through pages if there are any
        for page in range(5): # assumes no more than 5 pages
            nextButton = driver.find_element_by_xpath(
                '/html/body/div[3]/div/table/tbody/tr[2]/td[2]/div/div/div[3]/div/div[3]/div/div[1]/div[2]/div[5]')
            nextButton.click()
            courseElement = driver.find_element_by_css_selector('.grid.course-description-sections-tbl')
            html = courseElement.get_attribute('outerHTML')
            soup = BeautifulSoup(html, 'html.parser')
            text.extend(soup.find_all("div", class_="txt display-inline"))
            time.sleep(1)
    except:
        pass

    lectures = {}
    lec = 'No Lecture'
    lectures[lec] = []
    for line in text:
        # filters out non-class data
        item = line.contents[0]
        if(item.find('::') == -1 and item.find('.') == -1):
            if(item.find('Lec') != -1):
                lec = item
                lectures[lec] = []
            else:
                lectures[lec].append(item)

    searchButton = driver.find_element_by_css_selector('.clickable-text.display-inline.mar-right-sm')
    searchButton.click()

    time.sleep(.5)

    clearButton = driver.find_element_by_id('Clear')
    clearButton.click()

    return lectures

def findLectureRecitations(driver):
    courses = ['21-257', '05-430', '48-205', '21-256', '21-242', '18-202', '02-250', '21-241', '48-105', '12-358', '80-311', '24-262', '03-344', '18-345', '38-301', '21-260', '17-355', '15-210', '24-101', '12-201', '17-214', '70-257', '67-272', '73-240', '03-124', '36-200', '21-269', '21-112', '80-100', '09-222', '18-310', '18-220', '73-274', '48-410', '21-127', '27-212', '80-136', '36-315', '09-208', '17-356', '33-152', '09-101', '80-135', '09-220', '33-232', '33-104', '24-231', '48-305', '57-337', '21-111', '15-121', '12-232', '33-141', '73-230', '33-100', '03-232', '21-122', '15-112', '15-451', '33-121', '09-348', '03-116', '18-447', '09-331', '09-322', '76-487', '15-494', '21-240', '36-202', '21-261', '09-106', '15-359', '18-451', '12-352', '02-201', '15-312', '21-259', '09-218', '79-104', '33-122', '18-240', '67-262', '18-213', '76-245', '15-150', '09-105', '18-290', '33-228', '15-110', '70-462', '73-103', '24-352', '73-102', '27-202', '33-342', '88-252', '18-100', '19-101', '12-271', '73-160', '21-268', '85-102', '18-491', '21-484', '06-100', '06-363', '18-320', '18-452', '21-292', '15-251', '09-221', '15-213', '33-340', '33-142', '70-122', '27-217', '12-100', '15-122', '02-261', '80-150', '03-345', '03-231', '80-180', '21-228', '21-120', '88-223', '03-250', '27-100', '09-345', '21-124']
    courseSchedules = {}
    n = 1;
    for course in courses:
        courseSchedules[course] = getCourseInfo(driver, course)
        time.sleep(1)
        print('{}/{} classes done'.format(n, len(courses)))
        n += 1
    return courseSchedules

def main():
    user = input('User: ')
    password = getpass.getpass()
    driver = init_driver()
    login(driver, user, password)
    time.sleep(2)
    navigateToPlanSchedule(driver)
    time.sleep(1)

    courseSchedules = findLectureRecitations(driver)
    with open('lectureData.json', 'w') as filepath:
        json.dump(courseSchedules, filepath, sort_keys=True, indent=4)

    time.sleep(5)
    driver.quit()

if __name__ == '__main__':
	main()