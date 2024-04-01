# Пробный сервис через консоль
import requests
from bs4 import BeautifulSoup


def find_concert_info_by_name(concert_name):
    url = "https://ticketon.kz/concerts"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        concert_blocks = soup.find_all("div", class_="list-item block--bordered")

        for block in concert_blocks:
            title = block.find("span", class_="list-item__event").text.strip()
            if concert_name.lower() in title.lower():
                date = block.find("time").text.strip()
                location = block.find("a", class_="list-item__place").text.strip()
                print("Название концерта:", title)
                print("Дата концерта:", date)
                print("Место проведения:", location)
                print("=" * 50)


concert_name = input("Введите название концерта: ")
find_concert_info_by_name(concert_name)