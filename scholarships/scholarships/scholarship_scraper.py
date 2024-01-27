import requests
import urllib
from bs4 import BeautifulSoup
import csv
import re
import json
from pprint import pprint as ppr

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
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.144'}
        params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote)
        response = requests.get(self.url, params=params, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            table = soup.find_all('table', {'class': 'cos-table-detail'})[0]

            table_data = {}
            theaders = [header.text.strip() for header in table.select(headers_selector)]
            table_data['ScholarshipName'] = theaders[0]
            rows = table.select('tbody tr')  # Adjust this selector based on your HTML structure

            for row in rows:
                columns = row.select('td')  # Adjust this selector based on your HTML structure
                table_data[columns[0].text.strip()] = columns[1].text.strip()

            self.data.append(table_data)

    def save_to_csv(self, filename):
        if self.data:
            keys = self.data[0].keys()
            with open(filename, 'w', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=keys)
                writer.writeheader()
                writer.writerows(self.data)

    def get_data(self):
        return self.data

    @staticmethod
    def string_to_dict(input_string):
        # Define a pattern to extract key-value pairs
        pattern = re.compile(r'([^:]+):\s*([^:]+)')

        # Find all matches in the input string
        matches = re.findall(pattern, input_string)

        # Create a dictionary from the matches
        result_dict = dict(matches)

        return result_dict

# Example usage with parameters:
url_to_scrape = 'https://www.careeronestop.org/toolkit/training/find-scholarships-detail.aspx'
scraper = ScholarshipScraper(url_to_scrape)
infile = open('scholarshipIDs.csv', 'r')
scholarship_ids = [id[0] for id in csv.reader(infile)]
for sch_id in scholarship_ids:
    print(f'starting: {sch_id}')
    params = {'scholarshipId': sch_id}  # Add your parameters
    scraper.scrape_table('thead tr th', params)  # Adjust selectors accordingly
result = scraper.get_data()
#ppr(result)
fname = 'scholarshipInfo.json'
with open(fname, "w") as outfile:
    json.dump(result,outfile)
#scraper.save_to_csv(f"./scholarshipInfo.csv")  # Adjust the path as needed


# get unique keys
from itertools import chain

def UniqueKeys(arr):
    res = list(set(chain.from_iterable(sub.keys() for sub in arr)))
    return res