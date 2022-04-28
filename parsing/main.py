import requests
import json
from parsing.api import RaribleApi
from parsing.utils import *
import traceback
import datetime

col1 = os.path.dirname(__file__) + "/output/collections1.txt"
items1 = os.path.dirname(__file__) + "/output/items1.txt"
act1 = os.path.dirname(__file__) + "/output/act1.txt"
SAVING_EVERY = 10

def difficult_process(api, logger, query, basic_dict = {}, buckets=1, SIZE=100, need_logs=False):
    all_collections = []
    prev_cont = ""
    i = 0
    while (i < buckets):
        logger.debug("Sending the query")
        dct = basic_dict.copy()
        dct["size"] = SIZE
        if (len(prev_cont) != 0): 
            dct["continuation"] = prev_cont

        collections = api.method(query, dct)
        if (need_logs):
            logger.debug(str(collections))
        all_collections.append(collections)
        if ("continuation" not in collections):
            break
        prev_cont = collections["continuation"]
        logger.debug(f"Local status: {i}")
        i += 1
    return all_collections     

def pretty_json(js):
    return json.dumps(js, ensure_ascii=False, indent=4)

def save_json(obj, filename):
    with open(filename, "w") as f:
        print(pretty_json(obj), file=f) 

def load_json(filename):
    with open(filename) as f:
        ret = json.load(f)
    return ret

def main(logger):
    api = RaribleApi(DELAY = 0.35, api_v = "") 

    # Parse popular NFTs
    try:
        items_temp = load_json(items1)
        logger.debug("Got items_temp from the file") 
    except Exception as ex:
        logger.debug(f"Error while getting items from the file: {ex}")  
        basic_dct = { 
            "blockchains": ["ETHEREUM"],
            "showDeleted": False 
        }
        # "lastUpdatedTo": int((datetime.datetime.now() - datetime.timedelta(days=14)).timestamp())
        units = difficult_process(api, logger, "items/all", basic_dct, buckets=10)
        items_temp = []
        for unit in units:
            items_temp += unit["items"]
        save_json(items_temp, items1) 
    logger.debug(f"Parsed {len(items_temp)} items")
    
    # Get their collections
    collections_ids = set()
    for item in items_temp:
        collections_ids.add(item["collection"])
    logger.debug(f"Got {len(collections_ids)} collections")    
 
    # Parse these collections
    try:
        collections = load_json(col1)
        logger.debug("Got collections from the file") 
    except Exception as ex:
        logger.debug(f"Error while getting collections from the file: {ex}")
        collections = []
        for i, col_id in enumerate(collections_ids):
            if (i % SAVING_EVERY == SAVING_EVERY - 1):
                logger.debug(f"Getting collection {i}: {col_id}")
            collections.append(api.method(f"collections/{col_id}"))
        save_json(collections, col1)
    logger.debug(f"Parsed {len(collections)} collections")
    
    # Get items for all of them
    for i, collection in enumerate(collections):
        logger.debug(f"Download items of collection: {i}")
        if ('parsed_items' in collection):
            continue
        basic_dct = {"collection": collection["id"]}
        units = difficult_process(api, logger, "items/byCollection", basic_dct, buckets=2)
        items = []
        for unit in units:
            items += unit["items"]
        collection["parsed_items"] = items
        if (i % SAVING_EVERY == SAVING_EVERY - 1):
            save_json(collections, col1) 
    save_json(collections, col1)

    # Count size of items:
    count_items = 0
    for collection in collections:
        count_items += len(collection["parsed_items"])
    logger.debug(f"Parsed: {count_items} items")

    # Loading act-s
    try:
        activities = load_json(act1)
        logger.debug("Got act-s from the file") 
    except Exception as ex:
        logger.debug(f"Error while getting act-s from the file: {ex}")
        activities = dict()

    # Get activities
    for i, collection in enumerate(collections):
        logger.debug(f"Download items statistics of collection: {i}")
        for item in collection["parsed_items"]:
            i_id = item["id"]
            if (i_id in activities):
                continue
            basic_dct = {"itemId": i_id, "type": ["SELL", "MINT"]}
            units = difficult_process(api, logger, "activities/byItem", basic_dct, buckets=2)
            acts = []
            for unit in units:
                acts += unit["activities"]
            activities[i_id] = acts
        save_json(activities, act1)

if __name__ == "__main__":
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = LoggerWrapper(logging.getLogger(toplevel))
    logger.warning("NFT logging enabled")
    try:
        main(logger)
    except Exception as ex:
        trace = ''.join(traceback.format_list(traceback.extract_tb(ex.__traceback__)))
        logger.error(f"\nTrace:\n{trace}\nError: {ex}")
    logger.warning("Finished!")
    
