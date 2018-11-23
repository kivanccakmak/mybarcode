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

    if status != None:
	config['status'] = status

    cursor = conn.cursor()
    logger.info('== Starting Record Test ==')
    record_status(barcode, config, cursor)
    print('query: {} -> {}'.format(barcode, status))
    conn.commit()
    conn.close()
    logger.info('== Test Record Completed ==')

if __name__ == "__main__":
    status = None
    if len(sys.argv) != 3 and len(sys.argv) != 2:
        print("invalid usage")
        print('python record.py barcode status')
        print('python record.py 1612-1 "Dvm Ediyor"')
        print('#to use existing status in config.ini')
        print('python record.py 1612-1')
        sys.exit(1)

    barcode = sys.argv[1]
    if len(sys.argv) == 3:
        status = sys.argv[2]

    main(barcode, status)
