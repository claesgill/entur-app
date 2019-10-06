from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime
from time import sleep
import os

# Colors
DEFAULT = "\033[0m"
W_RED   = "\033[41m"
W_GREEN = "\033[42m"

class Bus:
    """Bus object takes a name and a route number as arguments"""
    def __init__(self, name, route_number):
        self.name = (W_GREEN + route_number + " " + name).ljust(38) + DEFAULT
        self.departure_times = []

    def add_departure_time(self, unix_minutes):
        self.departure_times.append(unix_minutes)

    def get_departure_times(self):
        times = ""
        for time in self.departure_times:
            if time == 0:
                t = W_RED + "Nå" + DEFAULT
            else:    
                t = W_RED + str(time) + " min" + DEFAULT
            times += t.ljust(18)
        return times

    def __str__(self):
        return "self.name"

def clear_screen():
    """Clear the terminal screen"""
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def graphQL_request():
    """POST request via graphQL"""
    _transport = RequestsHTTPTransport(
        url='https://api.entur.io/journey-planner/v2/graphql/',
        use_json=True,
        headers={'ET-Client-Name': "claesgill.com - entur-app",}
    )

    client = Client(
        transport=_transport,
        fetch_schema_from_transport=True,
    )
    query = gql("""
    {
    stopPlace(id: "NSR:StopPlace:6374") {
        id
        name
        estimatedCalls(timeRange: 72100, numberOfDepartures: 20) {
        realtime
        aimedArrivalTime
        aimedDepartureTime
        expectedArrivalTime
        expectedDepartureTime
        actualArrivalTime
        actualDepartureTime
        date
        forBoarding
        forAlighting
        destinationDisplay {
            frontText
        }
        quay {
            id
        }
        serviceJourney {
            journeyPattern {
            line {
                id
                name
                transportMode
            }
            }
        }
        }
    }
    }
    """)

    return client.execute(query)

if __name__ == "__main__":
    # For every 5 seconds
    while(True):
        data = graphQL_request()

        galgeberg = Bus("Galgeberg", "20")
        skoeyen = Bus("Skøyen", "20")
        for element in data["stopPlace"]["estimatedCalls"]:
            bus_name = element["destinationDisplay"]["frontText"]
            aimed_arrival = datetime.strptime(element["aimedArrivalTime"], "%Y-%m-%dT%H:%M:%S+0200")
            expected_arrival = datetime.strptime(element["expectedArrivalTime"], "%Y-%m-%dT%H:%M:%S+0200")
            expected_arrival_unix = datetime.strptime(element["expectedArrivalTime"], "%Y-%m-%dT%H:%M:%S+0200").timestamp()
            if bus_name == "Galgeberg": 
                galgeberg.add_departure_time(int((expected_arrival_unix - datetime.now().timestamp()) / 60))
            if bus_name == "Skøyen":
                skoeyen.add_departure_time(int((expected_arrival_unix - datetime.now().timestamp()) / 60))

        clear_screen()
        print("{}\n".format(galgeberg.name), end="\r")
        print("{}".format(galgeberg.get_departure_times()), end="\r")
        print()
        print("{}\n".format(skoeyen.name), end="\r")
        print("{}".format(skoeyen.get_departure_times()), end="\r")
        print()
        sleep(5)    