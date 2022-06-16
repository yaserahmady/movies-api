from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = FastAPI()


@app.get("/")
def index():
    output = {}
    for i in range(10):
        output[i] = f"Ciao amico numero {i}"

    return output


@app.get("/movies")
def movies_endpoint():
    return get_uci_movies()


def get_uci_movies():
    url = (
        "https://www.ucicinemas.it/cinema/lombardia/bergamo/uci-cinemas-curno-bergamo/"
    )
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    showtimes = {}

    dom_days = soup.find_all("div", class_="showtimes__movie")

    for day in dom_days:

        cinema_date = datetime.strptime(day["id"], "movie_%d%m%y")
        key = cinema_date.strftime("%Y-%m-%d")
        showtimes[key] = []

        dom_showtimes = day.find_all("div", class_="showtimes__show")
        for m in dom_showtimes:
            movie = {}
            movie["name"] = m.find("span", class_="movie-name").text.strip()

            movie["orari"] = []
            for li in m.find("ul", class_="showtimes__movie__shows").find_all("li"):
                movie["orari"].append(li.text.strip())

            movie["notes"] = {
                "original_version": False,
                "3d": False,
                "adult_content": False,
                "vm14": False,
            }

            notes = m.find("span", class_="showtimes__movie__notes")
            if notes:
                movie["notes"]["original_version"] = (
                    True if notes.get("data-content") else False
                )
                movie["notes"]["3d"] = (
                    True
                    if notes.find(
                        "img",
                        {
                            "src": "https://www.ucicinemas.it/stage/static/movie/prop/3d.png"
                        },
                    )
                    else False
                )
                movie["notes"]["adult_content"] = (
                    True
                    if notes.find(
                        "img",
                        {"src": "https://www.ucicinemas.it/static/movie/prop/ca.png"},
                    )
                    else False
                )
                movie["notes"]["vm14"] = (
                    True
                    if notes.find(
                        "img",
                        {"src": "https://www.ucicinemas.it/static/movie/prop/vm14.png"},
                    )
                    else False
                )

            showtimes[key].append(movie)

    return showtimes
