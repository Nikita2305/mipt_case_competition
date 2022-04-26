import requests
import json
from parsing.api import RaribleApi
from parsing.utils import *

def print_pretty_json(js):
    return json.dumps(js, ensure_ascii=False, indent=4)

def main():
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = LoggerWrapper(logging.getLogger(toplevel))
    logger.debug("NFT logging enabled")
    
    api = RaribleApi(DELAY = 1) 

    total_collections = 1e5
    all_collections = []
    prev_cont = ""
    SIZE = 100
    while (len(all_collections) < total_collections):
        logger.debug("Sending the query")
        if (len(prev_cont) == 0):
            collections = api.method("collections/all", {
                "size": SIZE
            })
        else:
            collections = api.method("collections/all", {
                "size": SIZE,
                "continuation": prev_cont
            })
        print_pretty_json(collections)
        all_collections += collections["collections"]
        prev_cont = collections["continuation"]
        total_collections = collections["total"]
        logger.debug(f"Total: {len(all_collections)}")
        logger.debug(f"Data: {total_collections}")
    """   
    for i, collection in enumerate(collections):
        logger.debug(f"Status: {i}")
        items = api.method("items/byCollection", {
            "collection": collection["id"], 
            "size": 1
        })
    """
    logger.debug("Finished!")
      

if __name__ == "__main__":
    main()  
