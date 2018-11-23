from client import *

def main(barcode, status):
    """
    :barcode: String
    :status: String
    """

    conf_path = os.path.abspath(Constants.config_file())
    config = get_config(conf_path, Constants.config_sections())
    conn = db_connect(config['host'], config['user'], config['password'], 
            config['database'], config['query_timeout'], 
            config['login_timeout'])

    config['status'] = status
    cursor = conn.cursor()
    logger.info('== Starting Test ==')
    state = query_status(barcode, config, cursor)
    logger.info('query: {} -> {}'.format(barcode, state))
    record_status(barcode, config, cursor)
    conn.commit()
    state = query_status(barcode, config, cursor)
    logger.info('query: {} -> {}'.format(barcode, state))
    logger.info('== Test Completed ==')


if __name__ == "__main__":
    if len(sys.argv) is not 3:
        print("invalid usage")
        print('python test.py barcode status')
        print('python test.py 1612-1 "Dvm Ediyor"')
        sys.exit(1)
    main(str(sys.argv[1]), str(sys.argv[2]))
