from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup

def test_my_very_first_test():


"""
Starting here we get 2021 continents -> countries -> links to each station for climate data by navigating ashrae website
using Selenium and using BeautifulSoup4 to extract the values from the webpage after clicking on their interactive
buttons.
"""


ashrae_base_link = "https://ashrae-meteo.info/v2.0/"

service = Service()
chrome_options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 10) # Wait for page to load so we don't miss clicking anything.
driver.get(ashrae_base_link + "places.php") # So you don't have to render the map
time.sleep(3)

# We only need 2021 data, so we click on the 2021 page to render the list of stations from that page.
xpath_button_2021 = '// *[ @ id = "radio"] / label[4] / span[1]'
button_2021 = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_button_2021)))
button_2021.click()

continent_page = driver.page_source
soup = BeautifulSoup(continent_page, 'html.parser')

# Parsing out the stations and the links for the station
station_li_tags = soup.find("body").find("ul")
station_li_href_list = []
# This will get you the list of stations links to append after the ashrae link.
for ul in station_li_tags.find_all('ul'):
    for li in ul.find_all('li'):
        a_tag = li.find('a')
        if a_tag and 'href' in a_tag.attrs:
            href = a_tag['href']
            # Only need the links to the stations
            if "places.php" in href:
                print(href)
                station_li_href_list.append(ashrae_base_link + href)

# Now we open a new tab for each of the links we have
for link in station_li_href_list:
    driver.execute_script("window.open(arguments[0], '_blank');", link)
# Close the first tab because we don't need it any more.
driver.switch_to.window(driver.window_handles[0])
driver.close()

# Get the list of countries per continent.
country_href_list = []
for i in range(len(station_li_href_list)):
    driver.switch_to.window(driver.window_handles[0])
    # You should be on the first tab after you close the intial page.
    station_page = driver.page_source
    station_soup = BeautifulSoup(station_page, 'html.parser')
    country_a_tags = station_soup.find_all("a")
    for a in country_a_tags:
        href = a['href']
        if 'index.php?lat=' in href:
            print(href)
            country_href_list.append(href)
    driver.close()


"""
Starting here we get the climate station data
"""

handbook_links = [
    "https://ashrae-meteo.info/v2.0/index.php?lat=-21.201&lng=-159.813&place=%27%27&wmo=918430",
    "https://ashrae-meteo.info/v2.0/index.php?lat=-21.917&lng=-157.950&place=%27%27&wmo=918480",
    "https://ashrae-meteo.info/v2.0/index.php?lat=-20.137&lng=-157.344&place=%27%27&wmo=918400",
    "https://ashrae-meteo.info/v2.0/index.php?lat=-10.915&lng=-165.839&place=%27%27&wmo=918110",
    "https://ashrae-meteo.info/v2.0/index.php?lat=-14.331&lng=-170.714&place=%27%27&wmo=917650",
    "https://ashrae-meteo.info/v2.0/index.php?lat=20.900&lng=-156.429&place=%27%27&wmo=911900"
]
# re-open a driver to iterate the whole list of href to get the data
second_driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driversecond_driver, 10)
time.sleep(3)

# Prob the best way to do this is like 10 at a time
full_station_data = []

# for href in country_href_list:
#     driver.get(ashrae_base_link + href)

for index, link in enumerate(handbook_links):
    if index == 0:
        second_driver = driver.get(link)
    else:
        second_driver.execute_script("window.open(arguments[0], '_blank');", link)
    climate_page = second_driver.page_source
    climate_soup = BeautifulSoup(climate_page, 'html.parser')

    dry_wet = {
        "station_name": "",
        "drybulb": [],
        "wetbulb": []
       }

    # Get station name
    balloon_tag = climate_soup.find('div', class_='baloon_icon')
    if balloon_tag:
        b_tag = balloon_tag.find_next_sibling('b')
        if b_tag:
            station_name = b_tag.get_text(strip=True)
            print(station_name)
            dry_wet["station_name"] = station_name
        else:
            print("No station name found")
    else:
        print("No baloon_icon with station name found")

    # Get the table of data
    td_elements = climate_soup.find_all('td', text='Extreme Annual Design Conditions')

    # Initialize the variable to store the found tbody element
    tbody_element = None
    # If any td element is found, navigate to its parent tbody
    if td_elements:
        tbody_element = td_elements[0].find_parent('tbody')
    # Print the text content of the found tbody element
    if tbody_element:
        print(tbody_element)
    else:
        print("Element not found.")

    next_tbody_element = tbody_element.find_next_sibling('tbody')
    rows = next_tbody_element.find_all('tr')

    for row in rows:
        td_tags = row.find_all('td', class_='brd7')
        if td_tags:
            for td_tag in td_tags:
                following_td_tags = td_tag.find_next_siblings('td')
                values = [td.b.get_text() for td in following_td_tags if td.b is not None]
                if "DB" in td_tag.get_text():
                    dry_wet["drybulb"].extend(values)
                elif "WB" in td_tag.get_text():
                    dry_wet["wetbulb"].extend(values)

    # Only need n=5, 10, 20, 50 year max, so delete first 4
    dry_wet["drybulb"] = dry_wet["drybulb"][4:]
    dry_wet["wetbulb"] = dry_wet["wetbulb"][4:]
    # Delete every other value starting from the first value in 'drybulb' and 'wetbulb' lists because we only need Max values
    dry_wet["drybulb"] = dry_wet["drybulb"][1::2]
    dry_wet["wetbulb"] = dry_wet["wetbulb"][1::2]
