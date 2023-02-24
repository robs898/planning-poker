import time

from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By

num_browsers = 10
options = FirefoxOptions()
options.add_argument("--headless")
browsers = [webdriver.Firefox(options=options) for _ in range(num_browsers)]

start_time = time.time()

for browser in browsers:
    browser.get("http://127.0.0.1:8888/")

print(f"Spawned {num_browsers} browsers")

for i, browser in enumerate(browsers):
    browser.find_element(By.ID, "name").send_keys(f"dave{i}")
    browser.find_element(By.XPATH, "//button[text()='Connect']").click()
    print(f"dave{i} connected")

for browser in browsers:
    browser.find_element(By.XPATH, "//button[text()='2']").click()

browsers[0].find_element(By.XPATH, "//button[text()='show']").click()
print("show votes")

for browser in browsers:
    assert 'class="rainbow"' in browser.page_source
    print("rainbow showing")
    assert "<td>2</td>" in browser.page_source
    for i in range(num_browsers):
        assert f"<td>dave{i}</td>" in browser.page_source
        print(f"Found <td>dave{i}</td> in page source")


# test we disconnect failed heartbeat users
browsers[0].quit()
time.sleep(2)
assert "<td>dave0</td>" not in browsers[1].page_source

# finish
for browser in browsers:
    browser.quit()

end_time = time.time()
time_taken = end_time - start_time
print(f"tests took {time_taken} seconds")
