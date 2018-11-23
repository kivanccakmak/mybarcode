from client import *

def main(barcode):
    """
    :barcode: String
    """

    conf_path = os.path.abspath(Constants.config_file())
    config = get_config(conf_path, Constants.config_sections())
    conn = db_connect(config['host'], config['user'], config['password'], 
            config['database'], config['query_timeout'], 
            config['login_timeout'])

    cursor = conn.cursor()
    logger.info('== Starting Query Test ==')
    state = query_status(barcode, config, cursor)
    logger.info('query: {} -> {}'.format(barcode, state))
    print('query: {} -> {}'.format(barcode, state))
    conn.close()
    logger.info('== Test Query Completed ==')

if __name__ == "__main__":
    status = None
    if len(sys.argv) != 2:
        print("invalid usage")
        print('python query.py barcode')
        sys.exit(1)

    barcode = sys.argv[1]
    main(barcode)
