def load_json():
    logging.info('Loading config from: ' + configpath)
    with open(configpath, 'r') as configfile:
        config = json.load(configfile)
    logging.info('Config loaded')

class Config:
    __init__(self):
        pass

