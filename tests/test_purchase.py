
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def test_purchase():
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 15)

    try:
        # 1. Открываем магазин
        driver.get("https://www.saucedemo.com/")

        # 2. Авторизация
        driver.find_element(By.ID, "user-name").send_keys("standard_user")
        driver.find_element(By.ID, "password").send_keys("secret_sauce")
        driver.find_element(By.ID, "login-button").click()

        # 3. Добавляем рюкзак в корзину
        wait.until(EC.element_to_be_clickable(
            (By.ID, "add-to-cart-sauce-labs-backpack")
        )).click()

        # 4. Открываем корзину
        wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, "shopping_cart_link")
        )).click()

        # Ждём открытия страницы корзины
        try:
            wait.until(EC.url_contains("cart.html"))
        except TimeoutException:
            print("URL при ошибке:", driver.current_url)
            print("Заголовок страницы:", driver.title)
            print(
                "Текст страницы:",
                driver.find_element(By.TAG_NAME, "body").text[:1500]
            )
            raise

        # 5. Проверяем товар в корзине
        product = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".cart_item .inventory_item_name")
        ))

        assert product.text == "Sauce Labs Backpack"

        # 6. Переходим к оформлению заказа
        wait.until(EC.element_to_be_clickable(
            (By.ID, "checkout")
        )).click()

        # 7. Проверяем оформление с пустыми полями
        try:
            wait.until(EC.visibility_of_element_located(
                (By.ID, "first-name")
            ))
        except TimeoutException:
            print("URL при ошибке:", driver.current_url)
            print("Заголовок страницы:", driver.title)
            print(
                "Текст страницы:",
                driver.find_element(By.TAG_NAME, "body").text[:1500]
            )
            raise

        driver.find_element(By.ID, "continue").click()

        # Проверяем сообщение об ошибке
        error = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, '[data-test="error"]')
        ))

        assert error.text == "Error: First Name is required"

        print("Проверка пустых полей пройдена!")

        # 8. Заполняем данные покупателя
        driver.find_element(By.ID, "first-name").send_keys("Garik")
        driver.find_element(By.ID, "last-name").send_keys("Test")
        driver.find_element(By.ID, "postal-code").send_keys("123456")

        # 9. Продолжаем оформление
        driver.find_element(By.ID, "continue").click()

        # 10. Завершаем заказ
        wait.until(EC.element_to_be_clickable(
            (By.ID, "finish")
        )).click()

        # 11. Проверяем успешную покупку
        result = wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, "complete-header")
        ))

        assert result.text == "Thank you for your order!"

        print("Тест пройден: покупка успешно оформлена!")

    finally:
        driver.quit()
