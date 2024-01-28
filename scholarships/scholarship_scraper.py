import requests
import urllib
from bs4 import BeautifulSoup
from itertools import chain
import csv
import re
import time
from pathlib import Path

""" TODO

Split the Award Name into three groups
pull scholarship ID from the URL we get
Export to CSV
Do an initial pass over them to cut out irrelevant results
Update with Scholarship details.

Set it up to use a simple config file.
"""


class ScholarshipScraper:
    def __init__(self, url):
        self.url = url
        self.data = []

    def scrape_table(self, headers_selector, payload=None):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.144"
            }
            params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote)
            response = requests.get(self.url, params=params, headers=headers)
            table_data = {}
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                table = soup.find_all("table", {"class": "cos-table-detail"})[0]
                table_data["scholarshipId"] = payload["scholarshipId"]
                theaders = [
                    header.text.strip() for header in table.select(headers_selector)
                ]
                table_data["ScholarshipName"] = theaders[0]
                rows = table.select(
                    "tbody tr"
                )  # Adjust this selector based on your HTML structure

                for row in rows:
                    columns = row.select(
                        "td"
                    )  # Adjust this selector based on your HTML structure
                    if columns[0].text.strip() == "Organization":
                        cell_data = columns[1].find_all("div")
                        table_data[columns[0].text.strip()] = cell_data[0].text.strip()
                        table_data["Address"] = cell_data[1].get_text(separator=", ")
                    else:
                        table_data[columns[0].text.strip()] = columns[1].text.strip()
            else:
                print(f"SID {payload['scholarshipId']} :: Bad Response: {response.status_code}")
                table_data["scholarshipId"] = payload["scholarshipId"]
                table_data["responseCode"] = response.status_code
            self.data.append(table_data)
        except Exception as e:
            table_data["scholarshipId"] = payload["scholarshipId"]
            table_data["Error Type"] = type(e).__name__
            table_data["Error Message"] = str(e)
            self.data.append(table_data)

    def save_to_csv(self, filename):
        if self.data:
            self.standardize_keys()
            keys = self.data[0].keys()
            with open(filename, "w", newline="") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=keys)
                writer.writeheader()
                writer.writerows(self.data)

    def get_data(self):
        return self.data

    def standardize_keys(self):
        unique_keys = self.UniqueKeys(self.data)
        # Update each dictionary with missing keys using a dictionary comprehension
        for d in self.data:
            d.update({key: None for key in unique_keys if key not in d})

    @staticmethod
    def string_to_dict(input_string):
        # Define a pattern to extract key-value pairs
        pattern = re.compile(r"([^:]+):\s*([^:]+)")

        # Find all matches in the input string
        matches = re.findall(pattern, input_string)

        # Create a dictionary from the matches
        result_dict = dict(matches)

        return result_dict

    @staticmethod
    def UniqueKeys(arr):
        res = list(set(chain.from_iterable(sub.keys() for sub in arr)))
        return res


# Example usage with parameters:

datadir = "~/Data/scholarships"
infile_csv = f"{datadir}/http202Ids.csv"
outfile_csv = f"{datadir}/scholarshipInfo_202s.csv"

infile_str = Path(infile_csv).expanduser().as_posix()
outfile_str = Path(outfile_csv).expanduser().as_posix()

print(infile_str)
print(outfile_str)

url_to_scrape = (
    "https://www.careeronestop.org/toolkit/training/find-scholarships-detail.aspx"
)
scraper = ScholarshipScraper(url_to_scrape)
infile = open(infile_str, "r")
scholarship_ids = [id[0] for id in csv.reader(infile)]
for index, sch_id in enumerate(scholarship_ids):
    if index != 0:
        print(f"starting {index} :: {sch_id}")
        params = {"scholarshipId": sch_id}  # Add your parameters
        scraper.scrape_table("thead tr th", params)  # Adjust selectors accordingly
        # time.sleep(2)  # 2-second delay so we don't hammer the server and get bounced
result = scraper.get_data()
scraper.save_to_csv(outfile_str)  # Adjust the path as needed
