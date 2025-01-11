import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Инициализация драйвера
driver = webdriver.Chrome()

# Открываем URL
driver.get("https://www.tbank.ru/invest/pulse/profile/BorNing/operations/")

print("Авторизуйтесь на странице... У вас есть 35 секунд.")
time.sleep(35)  # Время на авторизацию


# Функция для очистки текста
def clean_text(text):
    return text.replace("\n", "").strip()


# Функция для получения данных о сделке
def get_trade_data():
    try:
        # Находим все элементы акций (по селектору строки)
        stock_elements = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "tr[data-qa-file='ProfileOperationItem']")
            )
        )

        if stock_elements:
            first_stock = stock_elements[0]  # Берем первую (верхнюю) акцию на странице

            # Извлекаем данные из строки таблицы
            name = clean_text(first_stock.find_element(By.CSS_SELECTOR, ".pulse-profileoperationspage__e0aWkD").text)
            paper_type = clean_text(first_stock.find_element(By.CSS_SELECTOR, ".pulse-profileoperationspage__f0aWkD").text)

            # Кликаем на строку с первой акцией
            first_stock.click()

            # Ждем появления всплывающего окна
            popup = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".pulse-profileoperationspage__c3ehoN")
                )
            )

            # Извлекаем обязательные данные из всплывающего окна
            operation_type = clean_text(popup.find_element(By.CSS_SELECTOR, ".pulse-profileoperationspage__g3ehoN").text)
            operation_price = clean_text(popup.find_element(By.CSS_SELECTOR, ".pulse-profileoperationspage__h3ehoN").text)

            # Проверяем наличие необязательного поля
            try:
                operation_change = clean_text(
                    popup.find_element(By.CSS_SELECTOR, ".pulse-profileoperationspage__i3ehoN").text
                )
            except:
                operation_change = "Открытие сделки"

            # Возвращаем все данные
            return name, paper_type, operation_type, operation_price, operation_change

        else:
            return None

    except Exception as e:
        print(f"Ошибка при извлечении данных о сделке: {e}")
        return None


# Функция для записи данных в файл
def save_data_to_file(data):
    with open("operations_data.txt", "a", encoding="utf-8") as file:
        file.write(
            f"Название бумаги: {data[0]}, Тип бумаги: {data[1]}, "
            f"Тип операции: {data[2]}, Цена: {data[3]}, Действие: {data[4]}\n"
        )
    print(f"Данные сохранены: {data}")


# Основной цикл программы
try:
    last_data = None  # Переменная для хранения последних обработанных данных

    while True:  # Бесконечный цикл, который будет работать до тех пор, пока пользователь не остановит программу
        driver.refresh()

        # Получаем данные о сделке
        current_data = get_trade_data()

        if current_data:
            if current_data != last_data:  # Проверяем, что данные не дублируются
                save_data_to_file(current_data)
                last_data = current_data
            else:
                print("Программа сработала, но новых сделок не найдено.")
        else:
            print("Не удалось получить данные о сделке.")

        # Небольшая задержка перед следующей итерацией
        time.sleep(10)

except KeyboardInterrupt:
    print("Программа завершена пользователем.")
finally:
    driver.quit()
