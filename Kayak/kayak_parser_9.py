

class KayakScraper:  # class in order to have .error attribute

    def __init__(self, html: str, route: str, url: str, departing_date: str) -> None:
        self.data = None  # after initializing: pd.DataFrame
        self.error = None  # after initializing: "DROPDOWNS MISSINg" or "RECAPTCHA" or False
        self.kayak_scraper(html, route, url, departing_date)

    def kayak_scraper(self, html: str, flight_route: str, kayak_url: str, flight_date: str) -> None:

        soup = BeautifulSoup(html, "lxml")
        dropdowns = soup.find_all("div", {"class": "multibook-dropdown"})
        if len(dropdowns) == 0:  # if dropdowns fails
            if "real KAYAK user" in html:
                self.error = "RECAPTCHA"
                print(self.error)
            else:
                self.error = "DROPDOWNS MISSING"
                print(self.error)

        else:
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

                prices.append(ticket_price)
                website = website.split("View Deal")[0]
                websites.append(website)

            arrival = [arr.text for arr in soup.find_all("span", {"class": "arrival-time base-time"})]
            departure = [depart.text for depart in soup.find_all("span", {"class": "depart-time base-time"})]

            carrier = [carr.text.strip() for carr in soup.find_all("div", {"class": "bottom"})]
            while '' in carrier:
                carrier.remove('')
            carrier = carrier[0::2]  # removes even position carriers because they are empty str

            is_best_flight = [False for _ in dropdowns]
            is_best_flight[0] = True  # first flight should be the best one: IMPLEMENT CHECK????

            data = {"arrival": arrival, "carrier": carrier, "departure": departure, 
                    "is_best_flight": is_best_flight,"price": prices, "website": websites}

            self.data = pd.DataFrame(data)

            self.data["flight_date"] = flight_date
            self.data["route"] = flight_route
            self.data["url"] = kayak_url

            today = str(date.today())
            now_time = str(datetime.now().time())[:-7]
            self.data["retrieved_at"] = now_time
            self.data["retrieved_on"] = today


def kayak_requester_range(start_range: int, end_range: int, flight_route: str) -> None:
    # param start_range: int (e.g.: 0), end_range: int (e.g.: 160), flight_route: str (e.g.: "LAX-ATL")

    with requests.session() as s:
        for num in range(start_range, end_range):
            tgt_date = date.today() + timedelta(num)
            url = f"https://www.kayak.com/flights/{flight_route}/{tgt_date}?sort=bestflight_a&fs=stops=0"
            resp = s.get(url, headers=headers)
            scraped = KayakScraper(resp.text, flight_route, url, str(tgt_date))
            df = pd.concat([starting_df, scraped.data], ignore_index=True, sort=False)
            write_csv(df, "db.csv")
            print("DATA SAVED:", str(datetime.now().time())[:-7])

            if scraped.error is "RECAPTCHA":
                print("ABORTING")
                print(num)
                break
            elif scraped.error is "DROPDOWNS MISSING":
                print("Url requested AGAIN")

    print("-" * 30)
    print("END")


if __name__ == "__main__":

    st = input("Insert starting date:")
    e = input("Insert final date (excluded):")
    kayak_requester_range(int(st), int(e), "LAX-ATL")