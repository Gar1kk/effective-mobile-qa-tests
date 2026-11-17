
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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
        wait.until(EC.url_contains("cart.html"))

        # 5. Проверяем, что рюкзак в корзине
        product = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".cart_item .inventory_item_name")
        ))
        assert product.text == "Sauce Labs Backpack"

        # 6. Начинаем оформление заказа
        wait.until(EC.element_to_be_clickable(
            (By.ID, "checkout")
        )).click()

        # 7. Заполняем данные покупателя
        wait.until(EC.visibility_of_element_located(
            (By.ID, "first-name")
        )).send_keys("Garik")

        driver.find_element(By.ID, "last-name").send_keys("Test")
        driver.find_element(By.ID, "postal-code").send_keys("123456")

        # 8. Продолжаем оформление
        driver.find_element(By.ID, "continue").click()

        # 9. Завершаем заказ
        wait.until(EC.element_to_be_clickable(
            (By.ID, "finish")
        )).click()

        # 10. Проверяем успешную покупку
        result = wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, "complete-header")
        ))

        assert result.text == "Thank you for your order!"

        print("Тест пройден: покупка успешно оформлена!")

    finally:
        driver.quit()
