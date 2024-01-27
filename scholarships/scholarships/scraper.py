import requests
import urllib
from bs4 import BeautifulSoup
import csv
import re

""" TODO

Split the Award Name into three groups
pull scholarship ID from the URL we get
Export to CSV
Do an initial pass over them to cut out irrelevant results
Update with Scholarship details.

Set it up to use a simple config file.
"""

class WebsiteScraper:
    def __init__(self, url):
        self.url = url
        self.data = []

    def scrape_table(self, table_selector, headers_selector, payload=None):
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.144'}
        params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote)
        response = requests.get(self.url, params=params, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            table = soup.find_all('table', {'class': 'cos-table-responsive'})[0]
            theaders = [header.text.strip() for header in table.select(headers_selector)]
            rows = table.select('tbody tr')  # Adjust this selector based on your HTML structure

            for row in rows:
                row_data = {}
                columns = row.select('td')  # Adjust this selector based on your HTML structure
                for i in range(len(theaders)):
                    if i == 0:
                        cell_data = columns[0].find_all('div')[0].find_all('div')
                        for j in range(len(cell_data)):
                            if j == 0:
                                scholarshipID = cell_data[0].find_all('a')[0]['href'].rsplit('=')[-1]
                                awardName = cell_data[0].text.strip()
                                orgNameList = cell_data[1].text.strip().split(':')
                                purposeList = cell_data[3].text.strip().split(':')
                                row_data['scholarshipID'] = scholarshipID
                                row_data['scholarshipDetailURL'] = f'https://www.careeronestop.org/toolkit/training/find-scholarships-detail.aspx?scholarshipId={scholarshipID}'
                                row_data['Award Name'] = awardName
                                row_data[orgNameList[0]] = orgNameList[1].strip()
                                row_data[purposeList[0]] = purposeList[1].strip()
                    else:
                        row_data[theaders[i]] = columns[i].text.strip()

                self.data.append(row_data)

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
url_to_scrape = 'https://www.careeronestop.org/toolkit/training/find-scholarships.aspx'
scraper = WebsiteScraper(url_to_scrape)
params = {'keyword':'architecture engineering construction', 'curPage':'2','pagesize':'500', 'studyLevelFilter': 'Bachelor\'s Degree'}  # Add your parameters
selector = '#Body #divCenter #wrapper #Form1 #divSitetcm24-37659-64.BootstrapCOSHomePageSiteTemplate #content-column.responseContent #scholarshipTableConent' # .col-sm-12 col-md-12 .cos-table-responsive'
scraper.scrape_table(selector, 'thead tr th', params)  # Adjust selectors accordingly
result = scraper.get_data()
scraper.save_to_csv(f"./scraped_data{params['curPage']}.csv")  # Adjust the path as needed