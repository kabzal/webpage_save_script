import re
import os
import requests
from bs4 import BeautifulSoup

# Преобразуем ссылку на гугл-таблицу в ссылку на html-таблицу
def modify_url(initial_url):
    # Проверяем два варианта написания ссылок
    try:
        regex = r"https://docs.google.com/spreadsheets/d/([^/]+)/edit\?gid=\d+#gid=(\d+)"
        find_parts = re.findall(regex, initial_url)
        part_of_url = find_parts[0][0]
        page_num = find_parts[0][1]
    except IndexError:
        regex = r"https://docs.google.com/spreadsheets/d/([^/]+)/edit#gid=(\d+)"
        find_parts = re.findall(regex, initial_url)
        part_of_url = find_parts[0][0]
        page_num = find_parts[0][1]

    new_url = f"https://docs.google.com/spreadsheets/u/0/d/{part_of_url}/gviz/tq?tqx=out:html&tq&gid={page_num}"
    return new_url


# Обрабатываем и сохраняем веб-страницу
def save_webpage(url, table_name):
    response = requests.get(url)
    response.raise_for_status()  # Проверка успешности запроса

    # Преобразуем содержимое страницы в BeautifulSoup объект
    soup = BeautifulSoup(response.content, 'html.parser')

    # Дальнейший блок кода до row.decompose() нужен,
    # чтобы удалить пустую строку на втором и последующих листах таблицы

    # Найти тег table на странице
    table = soup.find('table')
    if table:
        # Найти все строки в таблице
        rows = table.find_all('tr')

        for row in rows:
            # Проверить, имеет ли строка стиль заголовка и пустые ячейки
            if row.get('style') == "font-weight: bold; background-color: #aaa;":
                cells = row.find_all('td')
                if all(cell.get_text(strip=True) == '' for cell in cells):
                    row.decompose()  # Удалить строку из таблицы

    # Получаем название страницы
    title = soup.title.string if soup.title else 'untitled'
    # Удаляем недопустимые символы для имени файла
    title = re.sub(r'[\\/*?:"<>|]', "_", title)

    # Формируем имя файла
    filename = f"{table_name}_{title}.html"
    save_path = os.path.join('.', filename)

    # Получаем HTML-код страницы
    html_content = soup.prettify()

    # Сохраняем HTML-код в файл
    with open(save_path, 'w', encoding='utf-8') as file:
        file.write(html_content)

    print(f"Веб-страница сохранена по пути: {save_path}")


# Читаем файл urls.txt и сохраняем веб-страницы по перечисленным ссылкам
with open("urls.txt", "r", encoding="utf-8") as source:
    urls = [i.strip().split() for i in source.readlines()]
    for url in urls:
        new_url = modify_url(url[1])
        table_name = url[0]
        # Сохранение страницы
        save_webpage(new_url, table_name)
