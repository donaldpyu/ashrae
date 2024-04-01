import re
import time
import csv

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

ashrae_base_link = "https://ashrae-meteo.info/v2.0/"
service = Service()
chrome_options = webdriver.ChromeOptions()


def get_country_list(country_href_list):
    """
    Starting here we get 2021 continents -> countries -> links to each station for climate data by navigating ASHRAE
    website using Selenium and using BeautifulSoup4 to extract the values from the webpage after clicking on
    their interactive buttons.

    :arg:
        country_href_list: Empty list to append all the country href links per continent onto.

    :return:
        country_href_list: A list of all the country href links per continent in 2021.
    """

    # Initialize chrome drive and settings.
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 10)  # Wait for page to load, so we don't miss clicking anything.
    driver.get(ashrae_base_link + "places.php")  # So you don't have to render the map
    time.sleep(3)

    # We only need 2021 data, so we click on the 2021 page to render the list of stations from that page.
    xpath_button_2021 = '// *[ @ id = "radio"] / label[4] / span[1]'
    button_2021 = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_button_2021)))
    print("Clicking on 2021...")
    button_2021.click()

    continent_page = driver.page_source
    soup = BeautifulSoup(continent_page, "html.parser")

    # Parsing out the stations and the links for the station
    station_li_tags = soup.find("body").find("ul")
    station_li_href_list = []
    # This will get you the list of stations links to append after the ashrae link.
    print("Getting list of station links...")
    for ul in station_li_tags.find_all("ul"):
        for li in ul.find_all("li"):
            a_tag = li.find("a")
            if a_tag and "href" in a_tag.attrs:
                href = a_tag["href"]
                # Only need the links to the stations
                if "places.php" in href:
                    print(href)
                    station_li_href_list.append(ashrae_base_link + href)
    print("List of links for each stations done.")
    print(f"Number of stations pulled: {len(station_li_href_list)}")

    # Now we open a new tab for each of the links we have
    print("Opening new tabs for each link...")
    for link in station_li_href_list:
        driver.execute_script("window.open(arguments[0], '_blank');", link)
    # Close the first tab because we don't need it anymore.
    driver.switch_to.window(driver.window_handles[0])
    driver.close()

    # Get the list of countries per continent.
    print("Getting list of countries per continent...")
    for i in range(len(station_li_href_list)):
        driver.switch_to.window(driver.window_handles[0])
        # You should be on the first tab after you close the initial page.
        station_page = driver.page_source
        station_soup = BeautifulSoup(station_page, "html.parser")
        country_a_tags = station_soup.find_all("a")
        for a in country_a_tags:
            print("Getting href links from the station page...")
            href = a["href"]
            if "index.php?lat=" in href:
                print(href)
                country_href_list.append(href)
        driver.close()
    print("List of href has been created!")
    print(f"Length of the href list: {len(country_href_list)}")
    return country_href_list


def get_station_data(full_station_data, country_href_list):
    """ Starting here we get the climate station data

    :arg:
        full_station_data: empty list to be filled with ASHRAE station data
        country_href_list: the list of country href links to be iterated through the chromedriver.

    :return:
        full_station_data: a filled list of all the ASHRAE station data.
    """

    # We want to have groups of 10 links at a time, so we don't open 9000 tabs.
    for i in range(0, len(country_href_list), 10):
        group = country_href_list[i:i + 10]
        ashrae_link_group = [ashrae_base_link + value for value in group]
        print("ASHRAE Link Group: ")
        print(ashrae_link_group)
        print("Status of range and link group...")
        print(range(0, len(country_href_list), 10))

        # Re-open a driver to iterate the whole list of href to get the data
        second_driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(second_driver, 10)
        time.sleep(3)

        for link in ashrae_link_group:
            second_driver.execute_script("window.open(arguments[0], '_blank');", link)
        # Close the empty tab, so it iterates through the opened ASHRAE pages.
        second_driver.close()

        for link in ashrae_link_group:
            print(f"We are executing on {link}")
            dry_wet = {
                "station_name": "",
                "latitude": "",
                "longitude": "",
                "drybulb": [],
                "wetbulb": []
            }

            # Regular expression pattern to match lat and lng from the url.
            pattern = r'lat=(-?\d+\.\d+)&lng=(-?\d+\.\d+)'

            # Search for lat and lng using regex
            match = re.search(pattern, link)

            if match:
                print("Latitude and longitude found.")
                lat = match.group(1)
                lng = match.group(2)
                print("Latitude:", lat)
                print("Longitude:", lng)
                dry_wet["latitude"] = lat
                dry_wet["longitude"] = lng
            else:
                print("Latitude and longitude not found.")

            second_driver.switch_to.window(second_driver.window_handles[0])
            climate_page = second_driver.page_source
            climate_soup = BeautifulSoup(climate_page, "html.parser")

            # Need to write an exception, if it's missing, then pass to the next link.
            # if balloon_tag:

            # Get station name. It's next to the balloon icon. And baloon is misspelled intentionally.
            balloon_tag = climate_soup.find("div", class_="baloon_icon")
            if balloon_tag:
                print("Balloon tag found, looking for station name")
                b_tag = balloon_tag.find_next_sibling("b")
                if b_tag:
                    station_name = b_tag.get_text(strip=True)
                    print(f"Station name found: {station_name}")
                    dry_wet["station_name"] = station_name
                else:
                    print("No station name found")
            else:
                print("No baloon_icon with station name found")
                dry_wet["station_name"] = "No station name found"

            # Get the entire table of data from Extreme Annual Design Conditions
            td_elements = climate_soup.find_all("td", string="Extreme Annual Design Conditions")

            if len(td_elements) > 0:
                print("Extreme Annual Design Conditions table has been found.")
                # Initialize the variable to store the found tbody element
                tbody_element = None
                # If any td element is found, go to its parent tbody
                if td_elements:
                    tbody_element = td_elements[0].find_parent('tbody')
                    print("Parent tbody found: ")
                    print(tbody_element)
                else:
                    print("Element not found.")

                # The table has a header tbody, and the tbody with all the data. The next tbody has everything.
                next_tbody_element = tbody_element.find_next_sibling('tbody')
                rows = next_tbody_element.find_all('tr')

                # Now we want to get the dry and wet bulb values of n-Year Return Period Values of Extreme Temperature.
                for row in rows:
                    print("Getting dry and wet bulb values...")
                    td_tags = row.find_all('td', class_='brd7')  # The values are within this row
                    if td_tags:
                        for td_tag in td_tags:
                            next_td_tags = td_tag.find_next_siblings('td')
                            values = [td.b.get_text() for td in next_td_tags if td.b is not None]  # Values are bolded.
                            if "DB" in td_tag.get_text():
                                dry_wet["drybulb"].extend(values)
                            elif "WB" in td_tag.get_text():
                                dry_wet["wetbulb"].extend(values)
                print("All Dry and wet bulb values added to full_station_data")

                # Only need n=5, 10, 20, 50 year max, so delete first 4
                print("Cleaning up dry and wet bulb values...")
                print("Getting only n=5, 10, 20, 50 year maxes for n-Year Return Period Values of Extreme Temperature")
                print("Removing first 4 values of Extreme Annual Temperatures...")
                dry_wet["drybulb"] = dry_wet["drybulb"][4:]
                dry_wet["wetbulb"] = dry_wet["wetbulb"][4:]
                print("Removed Extreme Annual Temperatures.")

                # Delete every other value starting from the first value in 'drybulb' and 'wetbulb' lists
                # because we only need Max values.
                print("Removing Min values of n-Year Return Period Values of Extreme Temperature...")
                dry_wet["drybulb"] = dry_wet["drybulb"][1::2]
                dry_wet["wetbulb"] = dry_wet["wetbulb"][1::2]
                print("Min values removed.")

                # Then add which values are 5, 10, 20, and 50 years. Starting with 5 years in the list.
                print("Adding labels to the Max values of n-Year Return Period Values of Extreme Temperature...")
                years = ["n5years", "n10years", "n20years", "n50years"]
                dry_wet_final = {
                    "station_name": dry_wet["station_name"],
                    "latitude": dry_wet["latitude"],
                    "longitude": dry_wet["longitude"]
                    }

                for key, values in dry_wet.items():
                    if key in ["drybulb", "wetbulb"]:
                        dry_wet_final[key] = [(years[i], value) for i, value in enumerate(values)]
                print("Labels added for max values of n-Year Return Period Values of Extreme Temperature!")
            else:
                print("No table found for Extreme Annual Design Conditions for %s" % link)
                print("Filling with empty data")
                years = ["n5years", "n10years", "n20years", "n50years"]
                dry_wet_final = {
                    "station_name": dry_wet["station_name"],
                    "latitude": dry_wet["latitude"],
                    "longitude": dry_wet["longitude"]
                    }
                for key in ["drybulb", "wetbulb"]:
                    dry_wet_final[key] = [(years[i], "N/A") for i in range(len(years))]
                print("N/A values added to the dry and wet bulb field.")
            print(f"Appending {dry_wet_final["staion_name"]} data onto full_station_data...")
            full_station_data.append(dry_wet_final)
            print(f"{dry_wet_final["staion_name"]} data has been added to full_station_data.")
            second_driver.close()
    return full_station_data


def ashrae_to_csv(full_station_data):
    """Writing ASHRAE data to a csv file.

    :arg:
        full_station_data: The list of ASHRAE station data to write into a .csv file

    :return:
        .csv file of the ASHRAE station data
    """

    fieldnames = full_station_data[0].keys()
    csv_file_path = "full_station_data.csv"

    print("Writing CSV...")
    with open(csv_file_path, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in full_station_data:
            writer.writerow(row)
    print(f"CSV file '{csv_file_path}' has been created.")
    return


def main():
    full_station_data = []
    # empty_country_href_list = []
    # country_href_list = get_country_list(empty_country_href_list)
    test_country_href_list = [
        # These link has empty data.
        "https://ashrae-meteo.info/v2.0/index.php?lat=47.127&lng=9.518&place=%27%27&wmo=69900",
        "https://ashrae-meteo.info/v2.0/index.php?lat=49.627&lng=6.212&place=%27%27&wmo=65900",
        # Has data.
        "https://ashrae-meteo.info/v2.0/index.php?lat=42.183&lng=26.567&place=%27%27&wmo=156420",  # Elhovo, Bulgaria
        "https://ashrae-meteo.info/v2.0/index.php?lat=41.650&lng=25.383&place=%27%27&wmo=157300",  # Kardzhali, Bulgaria
        "https://ashrae-meteo.info/v2.0/index.php?lat=43.348&lng=17.794&place=%27%27&wmo=146480",  # Mostar, Bosnia
        "https://ashrae-meteo.info/v2.0/index.php?lat=44.476&lng=23.113&place=%27%27&wmo=154120",  # Barles, Romania
        "https://ashrae-meteo.info/v2.0/index.php?lat=46.536&lng=23.310&place=%27%27&wmo=151630",  # Baisoara, Romania
        "https://ashrae-meteo.info/v2.0/index.php?lat=39.806&lng=116.469&place=%27%27&wmo=545110",  # Beijing, China
        "https://ashrae-meteo.info/v2.0/index.php?lat=29.576&lng=106.461&place=%27%27&wmo=575160",  # Chongqing, China
        "https://ashrae-meteo.info/v2.0/index.php?lat=22.309&lng=113.922&place=%27%27&wmo=450070",  # HK, Hong Kong
        "https://ashrae-meteo.info/v2.0/index.php?lat=25.033&lng=121.515&place=%27%27&wmo=466920"  # Taipei, Taiwan
    ]
    get_station_data(full_station_data, test_country_href_list)  # country_href_list)
    ashrae_to_csv(full_station_data)


if __name__ == '__main__':
    main()
