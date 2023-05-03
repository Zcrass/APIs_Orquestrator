#!/usr/bin/env python

import argparse
import json
import logging as lg
import sys

from utils import EndpointReader
from utils import ProcessWatcher

def main():
    jobs = ProcessWatcher(**args['processwatcher'])
    for n, endpoint in enumerate(args['endpoints']):
        end = EndpointReader(**endpoint)
        jobs.add_proces(n, end)
    jobs.process_watcher()

if __name__ == '__main__':
    ### define logger
    lg.basicConfig(filename='APIS_Orquestrator.log', filemode='w',
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=lg.INFO)
    logger = lg.getLogger()
    stdout_handler = lg.StreamHandler(sys.stdout)
    logger.addHandler(stdout_handler)
    ### define arguments 
    parser = argparse.ArgumentParser(prog = 'APIsOrquestrator',
                                    description = 'Get data from api and send it to kafka topic')
    parser.add_argument('-i', '--input', help='json configuration file', required=True)
    args = json.load(open(parser.parse_args().input))
    ### running main app
    main()
    
