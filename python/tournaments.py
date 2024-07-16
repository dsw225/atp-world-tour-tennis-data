
# # # # # # # # #
#               #
#   FUNCTIONS   #
#               #
# # # # # # # # #

from scraping import *
from bs4 import BeautifulSoup
import aiohttp
import aiofiles
import asyncio
import signal


async def main():
    global proxy_url
    global auth
    proxy_url, auth = await read_proxies("proxies/smartproxy.csv")

    start_year = input('Enter start year: ')
    end_year = input('Enter end year: ')
    mw = input('Enter Tournament Type: ')


    tourney_data = []
    for h in range(int(start_year), int(end_year) + 1):
        year = str(h)
        new_data = await tournament_links(year, mw)
        tourney_data.extend(new_data)

    print(tourney_data)



async def tournament_links(year, mw):
    prefix_mapping = {
        'm': 'atpgs', 'c': 'ch', 'mi': 'fu'
    }
    prefix = prefix_mapping.get(mw, '')

    link_suffix = f"&tournamentType={prefix}" if prefix else ''

    # Setup
    year_url = f"http://www.atptour.com/en/scores/results-archive?year={year}{link_suffix}"  # ATP Games

    # HTML tree
    connector = aiohttp.TCPConnector(use_dns_cache=False, force_close=True)
    async with aiohttp.ClientSession(trust_env=True, connector=connector) as session:
        data_text = await fetch(session, year_url, proxy_url, auth)
        if not data_text:
            print("No data returned.")
            return
        else:
            print(f"Year: {year} data gathered.")

    soup = BeautifulSoup(data_text, 'html.parser')

    data = soup.find('div', class_ = 'tournament-list')

    result_links = []

    ul_tournaments = data.find_all('ul', attrs={'class': 'events'})

    for ul in ul_tournaments:
        a_element = ul.find('a', string="Results", href=True)
        if a_element:
            result_links.append(f"https://www.atptour.com{a_element.get('href')}")

    return result_links


# # # # # # # # # # #
#                   #
#   MAIN ROUTINE    #
#                   #
# # # # # # # # # # #

# def handle_keyboard_interrupt(signal, frame):
#     global exit_program
#     exit_program = True

if __name__ == "__main__":
    # signal.signal(signal.SIGINT, handle_keyboard_interrupt)
    asyncio.run(main())



