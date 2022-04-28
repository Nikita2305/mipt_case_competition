import requests
import json
from parsing.utils import *
import traceback
import datetime
import random

col1 = os.path.dirname(__file__) + "/output/collections1.txt"
items1 = os.path.dirname(__file__) + "/output/items1.txt"
act1 = os.path.dirname(__file__) + "/output/act1.txt"
col2 = os.path.dirname(__file__) + "/output/collections2.txt"
items2 = os.path.dirname(__file__) + "/output/items2.txt"
act2 = os.path.dirname(__file__) + "/output/act2.txt"


def pretty_json(js):
    return json.dumps(js, ensure_ascii=False, indent=4)

def save_json(obj, filename):
    with open(filename, "w") as f:
        print(pretty_json(obj), file=f) 

def load_json(filename):
    with open(filename) as f:
        ret = json.load(f)
    return ret

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
def get_date(string):
    units = string.split("T")
    new_units = units[1].split(".")
    date = units[0]
    time = new_units[0]
    if (time[-1] == 'Z'):
        time = time[:-1]
    return datetime.datetime.strptime(date + " " + time, DATE_FORMAT) 

def get_first_sell_price(activities):
    for activity in activities:
        if (activity["@type"] == "SELL"):
            return float(activity["payment"]["value"])
    return None

def get_first_buyer(activities):
    for activity in activities:
        if (activity["@type"] == "SELL"):
            return activity["buyer"]
    return None

def count_sells(activities):
    size = 0
    for activity in activities:
        if (activity["@type"] == "SELL"):
            size += 1
    return size

def drop_prev_dates(activities, days_drop):
    edge_date = datetime.datetime.now() - datetime.timedelta(days=days_drop)
    nfts = list(activities.keys())
    for nft in nfts:
        new_acts = []
        old_acts = activities[nft]
        for act in old_acts:
            if (get_date(act["date"]) < edge_date):
                new_acts.append(act)
        activities[nft] = new_acts 
    return activities

def main(logger): 
    acts = load_json(act1)
    collections = load_json(col1)
    # Get current price
    for collection in collections:
        for item in collection["parsed_items"]:
            iid = item["id"]
            item["FUTURE_PRICE"] = get_first_sell_price(acts[iid]) 

    # Get previous price
    acts = drop_prev_dates(acts, 14) 
    week_ago_acts = acts.copy()
    week_ago_acts = drop_prev_dates(week_ago_acts, 30)
    for collection in collections:
        uniques = set()
        try:
            uniques.add(collection["owner"])
        except Exception as ex:
            colid = collection["id"]
            logger.debug(f"No owner, collection: {colid}")
        total_sold_once = 0
        total_deals = 0
        for item in collection["parsed_items"]:
            iid = item["id"]
            item["NOW_PRICE"] = get_first_sell_price(acts[iid])
            item["SOLD_ONCE"] = int(item["NOW_PRICE"] != None)
            item["WEEK_DEALS"] = count_sells(acts[iid]) - count_sells(week_ago_acts[iid])
            total_sold_once += item["SOLD_ONCE"]
            total_deals += item["WEEK_DEALS"]
            uniques.add(get_first_buyer(acts[iid]))
        try:
            uniques.remove(None)
        except Exception:
            pass
        for item in collection["parsed_items"]:
            item["COLLECTION_SOLD_ONCE"] = total_sold_once
            item["COLLECTION_WEEK_DEALS"] = total_deals
            item["COLLECTION_OWNERS"] = len(uniques) 

    final = []
    nft_keys = ["id", "FUTURE_PRICE", "NOW_PRICE", "SOLD_ONCE", "WEEK_DEALS", "COLLECTION_SOLD_ONCE", "COLLECTION_WEEK_DEALS", "COLLECTION_OWNERS"]
    for collection in collections:
        for item in collection["parsed_items"]:
            new_item = dict()
            new_item["col_id"] = collection["id"]
            for key in item:
                if key in nft_keys:
                    new_item[key] = item[key]
            final.append(new_item)
    save_json(final, col2) 
    return

if __name__ == "__main__":
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = LoggerWrapper(logging.getLogger(toplevel))
    try:
        main(logger)
    except Exception as ex:
        trace = ''.join(traceback.format_list(traceback.extract_tb(ex.__traceback__)))
        logger.debug(f"\nTrace:\n{trace}\nError: {ex}")
 
