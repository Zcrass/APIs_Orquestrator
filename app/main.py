#!/usr/bin/env python

# Built-in modules
# import argparse
import json
import logging as lg
import sys

# Third-party modules

# Custom modules
from utils import EndpointReader, ProcessWatcher

### config file path
CONFIG_APIS_ORQUESTATOR = 'C:/development/testing/APIs_Orquestrator/archivoConfiguracion/conf_apis_orquestator.json'

def main():
    jobs = ProcessWatcher(**args['globals']['processwatcher'])
    for n, endpoint in enumerate(args['configs']['endpoints']):
        end = EndpointReader(**args['configs']['endpoints'][endpoint])
        jobs.add_proces(n, end)
    jobs.process_watcher()

if __name__ == '__main__':
    ### define logger
    lg.basicConfig(filename='APIS_Orquestrator.log', filemode='w',
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   level=lg.INFO)
    logger = lg.getLogger()
    stdout_handler = lg.StreamHandler(sys.stdout)
    logger.addHandler(stdout_handler)
    ### define arguments 
    # parser = argparse.ArgumentParser(prog = 'APIsOrquestrator',
    #                                 description = 'Get data from api and \
    #                                             send it to kafka topic')
    # parser.add_argument('-i', '--input', help='json configuration file',
    #                    required=True)
    args = json.load(open(CONFIG_APIS_ORQUESTATOR))
    ### running main app
    main()
    
