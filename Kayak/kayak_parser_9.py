# Source: https://github.com/ElLorans/kayak_scraper/blob/master/kayak_scraper.py

import re
from datetime import date, timedelta, datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup


# verify that db.csv is in folder
try:
    with open("db.csv") as data_file:
        pass

except FileNotFoundError:
    print("db.csv NOT PRESENT.\nGenerating db.csv .")
    empty_dictionary = {'arrival': list(), 'carrier': list(), 'departure': list(), 'flight_date': list(),
                        'is_best_flight': list(), 'price': list(), 'route': list(), 'website': list(), 'url': list(),
                        'retrieved_on': list(), 'retrieved_at': list()}
    empty_df = pd.DataFrame(empty_dictionary)
    empty_df.to_csv("db.csv")


def write_csv(dataframe, csv_name):
    try:
        dataframe.to_csv(csv_name, index=False)

    except PermissionError:
        print(csv_name, "IS OPEN!! Close the file and confirm")
        confirmation = input(f"Have you closed {csv_name}?")
        if confirmation.lower == "yes":
            write_csv(dataframe, csv_name)


class KayakScraper:  # class in order to have .error attribute

    def __init__(self, html: str, route: str, url: str, departing_date: str) -> None:
        """
        Scrape Kayak best flight page and update self.data (Calls kayak_scraper method).
        :param html: str (html format)
        :param route: str (e.g.: "LAX-ATL")
        :param url: str
        :param departing_date: str
        :return: None
        """
        self.data = None  # after initializing: pd.DataFrame
        self.error = None  # after initializing: "DROPDOWNS MISSINg" or "RECAPTCHA" or False
        self.kayak_scraper(html, route, url, departing_date)

    def kayak_scraper(self, html: str, flight_route: str, kayak_url: str, flight_date: str) -> None:
        """
        Scrape Kayak best flight page and update self.data (Called by __init__ method).
        :param html: str (html format)
        :param flight_route: str (e.g.: "LAX-ATL")
        :param kayak_url: str
        :param flight_date: str
        :return: None
        """
        today = str(date.today())
        now_time = str(datetime.now().time())[:-7]

        print("Parsing html")
        soup = BeautifulSoup(html, "lxml")
        dropdowns = soup.find_all("div", {"class": "multibook-dropdown"})
        print("Html parsed")

        if len(dropdowns) == 0:  # if dropdowns fails
            # write file to see error page (only last error will be saved)

            if "real KAYAK user" in html:
                self.error = "RECAPTCHA"
                print(self.error)

            else:
                self.error = "DROPDOWNS MISSING"
                print(self.error)

                with open("no_dropdowns.html", "w", encoding="utf-8") as file:
                    file.write(html)

            print(self.error)
            error = [self.error]
            data = {"arrival": error, "carrier": error, "departure": error, "flight_date": flight_date,
                    "is_best_flight": error, "price": error, "route": [flight_route], "website": error,
                    "url": [kayak_url], "retrieved_on": [today], "retrieved_at": [now_time]}

            self.data = pd.DataFrame(data)

        else:  # if len(dropdowns) > 0:             # (as intended)
            self.error = False
            prices = list()
            websites = list()
            for dropdown in dropdowns:
                pretty = dropdown.text.strip("\n").replace(" Economy", "").strip("Vedi offerta") \
                    .replace("View Deal", "").replace("Basic", "").replace("Cabina principale", "") \
                    .replace("Main Cabin", "").strip().replace("\n", "")

                # set ticket_price and web
                if "$" in dropdown.text:  # $ IS BEFORE PRICE AND CARRIER
                    match = re.compile("[^\W\d]").search(pretty)  # find first letter in string
                    # first char is currency, so from second to letter is price
                    ticket_price = pretty[1:match.start()]
                    website = pretty[match.start():].split("Book")[0]

                elif "€" in dropdown.text:  # € IS BETWEEN PRICE AND CARRIER
                    ticket_price = pretty.split("€")[0].strip()
                    website = pretty.split("€")[1].split("Book")[0]

                else:
                    ticket_price = "No price"
                    website = pretty.replace("Info", "").split("Book")[0]
                    # print("NO PRICE FOUND:", dropdown.text.replace("\n", ""))    # ONLY SOUTHWEST PRICES ARE NOT FOUND
                # ticket_price and web have been set

                prices.append(ticket_price)
                website = website.split("View Deal")[0]
                websites.append(website)

            arrival = [arr.text for arr in soup.find_all("span", {"class": "arrival-time base-time"})]

            carrier = [carr.text.strip() for carr in soup.find_all("div", {"class": "bottom"})]
            while '' in carrier:
                carrier.remove('')
            carrier = carrier[0::2]  # removes even position carriers because they are empty str

            departure = [depart.text for depart in soup.find_all("span", {"class": "depart-time base-time"})]

            is_best_flight = [False for _ in dropdowns]
            is_best_flight[0] = True  # first flight should be the best one: IMPLEMENT CHECK????

            data = {"arrival": arrival, "carrier": carrier, "departure": departure, "is_best_flight": is_best_flight,
                    "price": prices, "website": websites}

            self.data = pd.DataFrame(data)

            self.data["flight_date"] = flight_date
            self.data["route"] = flight_route
            self.data["url"] = kayak_url
            self.data["retrieved_at"] = now_time
            self.data["retrieved_on"] = today


def kayak_requester_range(start_range: int, end_range: int, flight_route: str) -> None:
    """
    Create db.csv file for flights departing every day from start_range to end_range excluded.
    :param start_range: int (e.g.: 0)
    :param end_range: int (e.g.: 160)
    :param flight_route: str (e.g.: "LAX-ATL")
    :return: None
    """

    # Cookie must be updated every 52 days ca. .
    # Last Cookie: 23 Jan 2020 . On 17 Jan 2020 previous cookie (26 Nov 2019) stopped working
    headers = {
        "Host": "www.kayak.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
        # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "TE": "Trailers",
        "Accept": "*/*",
        "Referer": "https://www.kayak.com",
        "Content-type": "application/x-www-form-urlencoded",
        "Origin": "https://www.kayak.com",

        # cookie retrieved METHOD POST DOMAIN www.kayak.com FILE collector. Shouldn't it be under GET??
        "Cookie": 'vid=1ed3f1e2-1001-11ea-9d54-0242ac12000c; vid=1ed3f1e2-1001-11ea-9d54-0242ac12000c; '
                  'xp-session-seg=xp20; Apache=JAFJAB1D8Ddhww$Jbk538w-AAABbnn3YNw-98-YclfRQ; '
                  'kayak=Jv1vDB_C2TAPMt2$Fzna; kayak.mc'
                  '=Adb2nXsU9zQyjBymb6rKZk5jtrx1pzhfVQCnsEMLyfa3UabrS_crZxLmahh1xpukY7sQ46OeysLYSgsmL9u5UEmsLI0yWKhNhx'
                  'a0xAh85mqBaGiFaqDg0xpm-SSz4Vj8nFLm47wl_SjunwXpU3VzjN-D0Vh5jYrt7Mc-uVqDzxzsqDf9UnPz4Cohi1zu3VfnHnM0R6'
                  'ArZPhpjPpkSUe53l_KjHdqM0plm8K90YP-POnse4xCg-M1jO_-m8dUhBoMCHgAoHmBgLBqewRNLFo_rYV8B-9uWI5mQ5OlZ-LrU'
                  'CuoNfZB1Jms2EH7yR9zarTqS0zFHlSLmaHcNa8kkUOLe3ertvlrDM6HYoLob7lvZBfG4l8pvFpo8-kHfub5ufCzOo6HpqqYtgs1k'
                  'hbg_CzpGncxGtNAO91taSgzCCctdqonJW0g9xpwY-5umG2MydC_1h-z3HYGWuG2oQEgiVcYlytncQYl5gbMtZfvncTPZLzjQqsO'
                  '-jIdY2zJSQRwN-UtRR9cL1XsNr0AY7hryLTMxvk; _pxhd=""; p1.med.sc=17; _pxvid=1ed3f1e2-1001-11ea-9d54-0242'
                  'ac12000c; _gcl_au=1.1.777878553.1574740783; _ga=GA1.2.109955462.1574740783; _up=1.2.1950175204.15747'
                  '40784; G_ENABLED_IDPS=google; __gads=ID=22dffd3207285d34:T=1574740790:S=ALNI_Mb4b-OLfcBGBRp4DiGjBqsV'
                  '82WR7w; _gd_moveFromP13nTopContent="guidesbanner"; intent_media_prefs=; kykprf=274; cluster=5; p1.me'
                  'd.sid=H-51sGEXOweTrHBUZBTvxeL-YJ_zj1rrA5PhwASxyRiewanF_Zt_6qCOwegMT4jdw; kmkid=ApLYTE2rbbsgYyeXpP9Me'
                  'TU; NSC_q5-tqbslmf-cmvf=ffffffff0989bdf345525d5f4f58455e445a4a422a59; NSC_q5-lbqj-cmvf=ffffffff0989b'
                  '94345525d5f4f58455e445a4a42299c; _pxff_tm=1; _gid=GA1.2.1704400075.1579773435; _gat=1; _gat_UA422091'
                  '8541=1; _gat_UA4220918542=1; _px3=31d2768d83a8167dfeb29a51904cd657551c94caff79bf4def58f26aa1aca4fb:1'
                  'VzBo+ZO8UM8SWW8ztSfGF12yODUZSDDkCxfPaTsnSsB0flQEd3VacQb2KqZsxhOtPyM8Olw8bF2BwLzeBG0Ew==:1000:VIQ9ZG0'
                  'BcTgB2s15r+PCVXpx6LQJZA9sfCRetRwUGAOYZ/AZZqOU5cIOiiCex8dd0Ypr2JsdCOS8O6OXtMLXeL'
                  '/T7vzrX3cZSrO9SFMzpy3y7Gfnrt6soaPssxCsSD4Q6ZUXpWvWnwUbCscPHvv3+Ke7vUexzJGFN4lw0z3vqYw=; '
                  'hiddenParamsLAX-ATL%2F2020-01-23=page_origin%3DF..FD..M0%26src%3D%26searchingagain%3D%26c2s%3D'
                  '%26po%3D%26personality%3D%26provider%3D%26pageType%3DFD%26id%3DDR2E '
    }

    with requests.session() as s:
        for num in range(start_range, end_range):

            print("READING DATA")
            try:
                starting_df = pd.read_csv("db.csv")
                print("DATA READ")
            except FileNotFoundError:
                print("ERROR: db.csv NOT FOUND")
                column_names = ["arrival", "carrier", "departure", "is_best_flight", "price", "website", "flight_date",
                                "route", "url", "retrieved_at", "retrieved_on"]
                starting_df = pd.DataFrame(columns=column_names)  # empty df
                print("db.csv CREATED")
                write_csv(starting_df, "db.csv")

            tgt_date = date.today() + timedelta(num)
            # get direct flights for route on date
            url = f"https://www.kayak.com/flights/{flight_route}/{tgt_date}?sort=bestflight_a&fs=stops=0"
            headers["Referer"] = url  # update referer header for cookies. Unclear if needed
            print("\n" + url)
            resp = s.get(url, headers=headers)

            scraped = KayakScraper(resp.text, flight_route, url, str(tgt_date))

            df = pd.concat([starting_df, scraped.data], ignore_index=True, sort=False)

            print("SAVING DATA", str(datetime.now().time())[:-7])
            write_csv(df, "db.csv")
            print("DATA SAVED:", str(datetime.now().time())[:-7])

            if scraped.error is "RECAPTCHA":
                print("ABORTING")
                print(num)
                break
            elif scraped.error is "DROPDOWNS MISSING":      # APPARENTLY THIS IS NOT WORKING
                resp = s.get(url, headers=headers)
                print("Url requested AGAIN")

                scraped = KayakScraper(resp.text, flight_route, url, str(tgt_date))

                df = pd.concat([starting_df, scraped.data], ignore_index=True, sort=False)

                print("SAVING DATA", str(datetime.now().time())[:-7])
                write_csv(df, "db.csv")
                print("DATA SAVED:", str(datetime.now().time())[:-7])

    print("-" * 30)
    print("END")


if __name__ == "__main__":
    # with open("kayakked.html", encoding="utf-8") as f:
    #     t = f.read()
    # d = KayakScraper(t, "LAX-ATL", "www.test", "14-07-20")
    # d.data.to_csv("t.csv")

    st = input("Insert starting date:")
    e = input("Insert final date (excluded):")
    kayak_requester_range(int(st), int(e), "LAX-ATL")