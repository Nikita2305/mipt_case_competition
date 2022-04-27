import requests
import json
from parsing.api import RaribleApi
from parsing.utils import *
import traceback

col1 = os.path.dirname(__file__) + "/output/collections1.txt"
SAVING_EVERY = 10

def difficult_process(api, logger, query, basic_dict = {}, buckets=1, need_logs=False):
    total_collections = 1e18
    all_collections = []
    prev_cont = ""
    SIZE = 100
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
        total_collections = collections["total"]
        logger.debug(f"Local status: {i}")
        # logger.debug(f"Data: {total_collections}")
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
    raise RuntimeError("Wassup")
    api = RaribleApi(DELAY = 1) 
 
    try:
        collections = load_json(col1)
        logger.debug("Got collections from the file") 
    except Exception as ex:
        logger.debug(f"Error while getting collections from the file: {ex}")
        units = difficult_process(api, logger, "collections/all", buckets=10)
        collections = []
        for unit in units:
            collections += unit["collections"] 
        save_json(collections, col1)
    
    logger.debug(f"Parsed {len(collections)} collections")
    
    for i, collection in enumerate(collections):
        logger.debug(f"Status: {i}")
        if ('parsed_items' in collection):
            continue
        basic_dct = {"collection": collection["id"]}
        units = difficult_process(api, logger, "items/byCollection", basic_dct, buckets=10)
        items = []
        for unit in units:
            items += unit["items"]
        collection["parsed_items"] = items
        if (i % SAVING_EVERY == SAVING_EVERY - 1):
            save_json(collections, col1) 
      

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
    
