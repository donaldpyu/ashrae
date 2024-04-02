""" From the weather station long lat from the bigquery public data set, we find the ASHRAE weather stations that are
nearest to that location using Haversine formula.
"""

import csv
import random
import re
import time
import math

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import pandas as pd


ashrae_base_link = "https://ashrae-meteo.info/v2.0/"
service = Service()
chrome_options = webdriver.ChromeOptions()

weather_station_long_lat = [
    (174.75, -36.75),
    (151.25, -33.75),
    (151, -33.75),
    (151, -33.75),
    (150.75, -33.75),
    (150.75, -33.75),
    (145, -37.75),
    (144.75, -37.75),
    (144.75, -37.75),
    (140.25, 35.75),
    (140.25, 35.75),
    (140.25, 35.75),
    (140, 35.75),
    (140, 36),
    (139.75, 35.75),
    (135.5, 43.75),
    (135.25, 35),
    (135, 34.25),
    (133, 34.5),
    (127, 37.5),
    (127, 75.),
    (120.5, 24.25),
    (114.25, 22.25),
    (114.25, 22.5),
    (114.25, 22.25),
    (114, 22.25),
    (107.25, -6.5),
    (107, -6.25),
    (107, -6.25),
    (104, 1.5),
    (103.75, 1.25),
    (103.75, 1.25),
    (101.5, 3.25),
    (100.75, 13.5),
    (77.5, 28.5),
    (77.5, 28.5),
    (77.5, 28.5),
    (77.25, 28.75),
    (73, 19),
    (73, 19),
    (73, 19.25),
    (73, 19.25),
    (73, 19.25),
    (51.5, 25.25),
    (51.5, 25.25),
    (51.5, 25),
    (50, 26.5),
    (50, 26.25),
    (49.75, 26),
    (35, 32),
    (34.75, 32),
    (34.75, 32.25),
    (34.75, 32.25),
    (28.25, -26),
    (28.25, -26.25),
    (28.25, -26),
    (27, 60.5),
    (21, 52.25),
    (21, 52.25),
    (21, 52.25),
    (16.5, 60.25),
    (15.5, 60.5),
    (14.5, 48.25),
    (13.5, 52.25),
    (13.5, 52.25),
    (13.5, 52.25),
    (13.25, 52.25),
    (13.25, 52.5),
    (13.25, 52.5),
    (13.25, 52.25),
    (13.25, 52.5),
    (13.25, 52.25),
    (11, 59.75),
    (9.75, 55.5),
    (9.5, 59.25),
    (9.25, 45.5),
    (9.25, 55),
    (9.25, 45.5),
    (9, 50.25),
    (9, 50),
    (9, 45.5),
    (9, 50),
    (8.75, 50),
    (8.75, 50.25),
    (8.75, 50),
    (8.75, 50.25),
    (8.75, 5025),
    (8.5, 47.5),
    (8.5, 50),
    (8.5, 50),
    (8.5, 50.25),
    (8.5, 50.25),
    (8.5, 47.5),
    (8.5, 50.25),
    (8.25, 47.5),
    (7.75, 45),
    (7.75, 45),
    (7.5, 45),
    (7, 53.25),
    (6.75, 53.5),
    (6.5, 53.25),
    (6, 49.75),
    (5, 52.75),
    (5, 52.75),
    (4.5, 50.5),
    (4.25, 50.5),
    (3.75, 50.5),
    (2.75, 48.75),
    (2.75, 48.75),
    (2.75, 48.75),
    (2.75, 48.75),
    (2.25, 48.75),
    (2.25, 49),
    (2.25, 49),
    (2.25, 48.75),
    (2.25, 49),
    (2.25, 48.75),
    (2.25, 48.75),
    (0, 51.5),
    (0, 51.75),
    (-0.25, 51.25),
    (-0.5, 51.5),
    (-0.5, 51.5),
    (-0.75, 51.5),
    (-0.75, 51.5),
    (-3.25, 40.5),
    (-3.5, 40.5),
    (-3.75, 40.5),
    (-6.5, 53.25),
    (-46.75, -23.5),
    (-46.57, -23.5),
    (-47, -23),
    (-56, -34.75),
    (-70.75, -33.25),
    (-70.75, -33.25),
    (-70.75, -33.25),
    (-70.75, -33.5),
    (-73.5, 45.5),
    (-73.75, 45.5),
    (-74, 45.25),
    (-77.25, 37.25),
    (-77.5, 38.75),
    (-77.5, 39),
    (-77.5, 39),
    (-77.5, 39),
    (-77.5, 39),
    (-77.5, 39),
    (-77.5, 38.75),
    (-79.25, 43.75),
    (-79.5, 43.75),
    (-979.5, 43.5),
    (-80, 33),
    (-80.25, 33),
    (-80.5, 33.25),
    (-81.5, 36),
    (-82.75, 40),
    (-82.75, 39.75),
    (-83, 39.75),
    (-83, 40),
    (-84, 40.75),
    (-84.5, 33.75),
    (-84.5, 33.75),
    (-85, 41),
    (-85.75, 35),
    (-87.25, 36.5),
    (-91.75, 42),
    (-93.5, 42),
    (-94.5, 39.25),
    (-94.5, 39.25),
    (-95.25, 36.25),
    (-95.25, 36.25),
    (-95.75, 41.25),
    (-95.75, 41.25),
    (-96, 41.25),
    (-96.25, 41.25),
    (-96.75, 32.5),
    (-96.75, 40.75),
    (-96.75, 32.5),
    (-97, 32.5),
    (-97, 36.25),
    (-97.5, 30.5),
    (-100.25, 20.5),
    (-100.5, 20.5),
    (-111.75, 33.25),
    (-112, 33.25),
    (-112, 33.5),
    (-112, 40.25),
    (-112, 40.75),
    (-112, 40.5),
    (-112, 40.5),
    (-115, 36),
    (-115.25, 36),
    (-118.28, 33.75),
    (-118.25, 34),
    (-118.5, 34),
    (-119.5, 39.5),
    (-121.25, 45.75),
    (-121.25, 45.5),
    (-123, 45.5)
]

def random_wait():
    """ Generating random times between 1 and 4 seconds to sleep the program, so we're not spamming the website.

    :return:
        time.sleep(random.randint(1, 4)
    """
    wait_time = random.randint(1, 3)
    print(f"Waiting for {wait_time} seconds...")
    time.sleep(wait_time)
    print("Wait is now over")
    return


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
    total_start_time = time.time()

    # Initialize chrome drive and settings.
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 10)  # Wait for page to load, so we don't miss clicking anything.
    driver.get(ashrae_base_link + "places.php")  # So you don't have to render the map
    random_wait()

    # We only need 2021 data, so we click on the 2021 page to render the list of stations from that page.
    # Hard coded 2021 XPath, but eventually will gather the list of paths depending on values from the page when they
    # update the page to include more years or change the webpage. This is okay as of 2024-04-01.
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
        random_wait()
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
        random_wait()

    total_end_time = time.time()
    total_execution_time = total_end_time - total_start_time
    print(f"Total get_country_list execution time took {total_execution_time:.2f} seconds")
    print("List of href has been created!")
    print(f"Length of the href list: {len(country_href_list)}")

    return country_href_list


def get_href_long_lat(country_href_list, href_long_lat):

    # Regular expression pattern to match lat and lng from the url.
    pattern = r'lat=(-?\d+\.\d+)&lng=(-?\d+\.\d+)'

    for href in country_href_list:
        href_long_lat_init = {
            "href": href,
            "latitude": "",
            "longitude": ""
        }

        # Search for lat and lng using regex
        match = re.search(pattern, href)
        if match:
            print("Latitude and longitude found.")
            lat = match.group(1)
            lng = match.group(2)
            print("Latitude:", lat)
            print("Longitude:", lng)
            href_long_lat_init["latitude"] = lat
            href_long_lat_init["longitude"] = lng
        else:
            print("Latitude and longitude not found.")
        href_long_lat.append(href_long_lat_init)
    return href_long_lat


def haversine_distance(lat1, long1, lat2, long2):
    # Radius of Earth in kilometers.
    radius = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1_radian = math.radians(float(lat1))
    long1_radian = math.radians(float(long1))
    lat2_radian = math.radians(float(lat2))
    long2_radian = math.radians(float(long2))

    long_delta = long2_radian - long1_radian
    lat_delta = lat2_radian - lat1_radian
    a = math.sin(lat_delta / 2)**2 + math.cos(lat1_radian) * math.cos(lat2_radian) * math.sin(long_delta / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = radius * c
    return distance


def weather_station_compare_long_lat(bq_long_lat, ashrae_long_lat, combined_list):

    for bq_long, bq_lat in bq_long_lat:
        combined_list_init = {
            "bq_long": bq_long,
            "bq_lat": bq_lat,
            "ashrae_long": None,
            "ashrae_lat": None,
            "distance": None,
            "ashrae_href": ""
        }
        distances = []
        for ashrae in ashrae_long_lat:
            ashrae_long = ashrae["longitude"]
            ashrae_lat = ashrae["latitude"]
            distance = haversine_distance(bq_lat, bq_long, ashrae_lat, ashrae_long)
            ashrae["distance"] = distance
            distances.append(ashrae)
        sorted_distances = sorted(distances, key=lambda p: p["distance"], reverse=False)
        closest_ashrae_station = sorted_distances[0]

        combined_list_init["ashrae_long"] = float(closest_ashrae_station["longitude"])
        combined_list_init["ashrae_lat"] = float(closest_ashrae_station["latitude"])
        combined_list_init["distance"] = closest_ashrae_station["distance"]
        combined_list_init["ashrae_href"] = closest_ashrae_station["href"]
        combined_list.append(combined_list_init)
    return combined_list


def get_station_data(full_station_data, country_href_list):
    """ Starting here we get the climate station data

    :arg:
        full_station_data: empty list to be filled with ASHRAE station data
        country_href_list: the list of country href links to be iterated through the chromedriver.

    :return:
        full_station_data: a filled list of all the ASHRAE station data.
    """
    total_start_time = time.time()

    print("Length of how long the country_href_list to process: %s" % len(country_href_list))
    total_iterations = len(country_href_list) // 10 + (1 if len(country_href_list) % 10 != 0 else 0)
    print("Total number of iterations: %s" % total_iterations)

    for idx, i in enumerate(range(0, len(country_href_list), 10)):
        iteration_start_time = time.time()
        progress = (idx / total_iterations) * 100
        print(f"Progress of iteration in %: {progress:.2f}%")
        print(f"Progress of iteration in fractions: {idx} / {total_iterations}")

        group = country_href_list[i:i + 10]
        ashrae_link_group = [ashrae_base_link + value for value in group]
        print("ASHRAE Link Group: ")
        print(ashrae_link_group)

        # Re-open a driver to iterate the whole list of href to get the data
        second_driver = webdriver.Chrome(service=service, options=chrome_options)
        time.sleep(3)

        for link in ashrae_link_group:
            second_driver.execute_script("window.open(arguments[0], '_blank');", link)
            random_wait()
            # Close the empty tab, so it iterates through the opened ASHRAE pages.
        second_driver.close()

        for length in range(len(ashrae_link_group)):
            second_driver.switch_to.window(second_driver.window_handles[0])
            current_url = second_driver.current_url
            climate_page = second_driver.page_source
            climate_soup = BeautifulSoup(climate_page, "html.parser")

            print(f"We are executing on {current_url}")
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
            match = re.search(pattern, current_url)

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
                print("Getting dry and wet bulb values...")
                for row in rows:
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
                print("Drybulb values: %s" % dry_wet["drybulb"])
                print("Wetbulb values: %s" % dry_wet["wetbulb"])

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
                print("Final drybulb values: %s" % dry_wet["drybulb"])
                print("Final wetbulb values: %s" % dry_wet["wetbulb"])

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
                print("No table found for Extreme Annual Design Conditions for %s" % current_url)
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
            print(f"Appending {dry_wet_final["station_name"]} data onto full_station_data...")
            full_station_data.append(dry_wet_final)
            print(f"{dry_wet_final["station_name"]} data has been added to full_station_data.")
            second_driver.close()
            random_wait()

            iteration_end_time = time.time()
            iteration_execution_time = iteration_end_time - iteration_start_time
            print(f"{dry_wet_final["station_name"]} iteration execution time took {iteration_execution_time:.2f} seconds")
            print("###############################################################################################")

    total_end_time = time.time()
    total_execution_time = total_end_time - total_start_time
    print(f"Total get_station_data execution time took {total_execution_time:.2f} seconds")
    return full_station_data


def join_station_data(bq_data, ashrae_data):
    """ Joining both data to get the BQ forecast long/lat with the ASHRAE long/lat.

    :param bq_data: Should be combined_list.
        Fields:
        {
            "bq_long": float,
            "bq_lat": float,
            "ashrae_long": float,
            "ashrae_lat": float,
            "distance": float,
            "ashrae_href": string
        }
    :param ashrae_data: Should be full_station_data or full_station_data.csv.
        Fields:
        {
            "station_name": string,
            "latitude": float,
            "longitude": float,
            "drybulb": [string, float],
            "wetbulb": [string, float]
        }
    :return: A joined pandas DataFrame.
    """
    df1 = pd.read_csv(ashrae_data)
    unique_df1 = df1.drop_duplicates(subset=["station_name"])
    df2 = pd.DataFrame(bq_data)
    joined_df = pd.merge(df2, unique_df1, left_on=["ashrae_long", "ashrae_lat"], right_on=["longitude", "latitude"])
    joined_df.to_csv(joined_df, index=False)
    return joined_df


def ashrae_to_csv(full_station_data):
    """Writing ASHRAE data to a csv file.

    :arg:
        full_station_data: The list of ASHRAE station data to write into a .csv file

    :return:
        .csv file of the ASHRAE station data
    """
    total_start_time = time.time()
    fieldnames = full_station_data[0].keys()
    csv_file_path = "full_station_data.csv"

    print("Writing CSV...")
    with open(csv_file_path, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in full_station_data:
            writer.writerow(row)

    total_end_time = time.time()
    total_execution_time = total_end_time - total_start_time
    print(f"Total ashrae_to_csv execution time took {total_execution_time:.2f} seconds")
    print(f"CSV file '{csv_file_path}' has been created.")
    return


def main():
    main_start_time = time.time()

    # Get country links.
    empty_country_href_list = []
    country_href_list = get_country_list(empty_country_href_list)

    # Get long/lats of weather stations.
    href_long_lat = []
    get_href_long_lat(country_href_list, href_long_lat)

    # Get Haversine distance from weather station and ASHRAE and find closest distance.
    combined_list = []
    non_none_href_long_lat = [x for x in href_long_lat if x["latitude"] != "" or x["longitude"] != ""]
    weather_station_compare_long_lat(weather_station_long_lat, non_none_href_long_lat, combined_list)

    # Get data from ASHRAE.
    full_station_data = []
    combined_list_links = [links["ashrae_href"] for links in combined_list]
    get_station_data(full_station_data, combined_list_links)

    # Join ASHRAE data onto weather stations and export data.
    join_station_data(bq_data=combined_list, ashrae_data=full_station_data)
    ashrae_to_csv(full_station_data)

    main_end_time = time.time()
    main_execution_time = main_end_time - main_start_time
    print(f"Total main program took {main_execution_time:.2f}")
    print("Full program has been completed!")


if __name__ == '__main__':
    main()


# weather_station_long_lat = [
#     (-73.75, 45.5),
#     (-95.75, 41.25),
#     (-118.5, 34),
#     (-111.75, 33.25),
#     (-79.5, 43.75),
#     (-77.5, 39),
#     (-112, 40.25),
#     (-100.5, 20.5),
#     (-115, 36),
#     (-112, 33.5),
#     (-80, 33),
#     (-96.75, 40.75),
#     (-94.5, 39.25),
#     (-97.5, 30.5),
#     (-77.25, 37.25),
#     (-112, 40.5),
#     (-77.5, 39),
#     (-97, 36.25),
#     (-95.25, 36.25),
#     (-85, 41),
#     (-82.75, 39.75),
#     (-84.5, 33.75),
#     (-112, 40.5),
#     (-84, 40.75),
#     (-77.5, 38.75),
#     (-73.5, 45.5),
#     (-94.5, 39.25),
#     (-79.25, 43.75),
#     (-97, 32.5),
#     (-85.75, 35),
#     (-121.25, 45.75),
#     (-96, 41.25),
#     (-118.25, 33.75),
#     (-77.5, 39),
#     (-84.5, 33.75),
#     (-112, 40.75),
#     (-81.5, 36),
#     (-97.5, 30.5),
#     (-96.25, 41.25),
#     (-93.5, 42),
#     (-80.5, 33.25),
#     (-87.25, 36.5),
#     (-74, 45.25),
#     (-100.25, 20.25),
#     (-96.75, 32.5),
#     (-96.75, 32.5),
#     (-79.5, 43.5),
#     (-83, 39.75),
#     (-95.25, 36.25),
#     (-80.25, 33),
#     (-77.5, 39),
#     (-119.5, 39.5),
#     (-115.25, 36),
#     (-77.5, 39),
#     (-119.5, 39.5),
#     (-115.25, 36),
#     (-77.5, 39),
#     (-119.5, 39.5),
#     (-115.25, 36),
#     (-77.5, 39),
#     (-95.75, 41.25),
#     (-91.75, 42),
#     (-83, 40),
#     (-77.5, 38.75),
#     (-123, 45.5),
#     (-82.75, 40),
#     (-112, 33.25),
#     (-121.25, 45.5),
#     (-118.25, 34),
# ]