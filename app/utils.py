# Built-in modules
import json
import logging as lg
from multiprocessing import Process
import time

# Third-party modules
import pandas as pd 
from kafka import KafkaProducer
import requests

# Custom modules


logger = lg.getLogger(__name__)
class EndpointReader():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.data = pd.DataFrame()

    def receive_data(self):
        '''
        Function to try to Connect to an API and get data. 
        In case is unable to conect stores a predefined exception data.
        '''
        try:
            data = json.loads(requests.get(self.inputs['api_url']).text)
            data = pd.json_normalize(data['results'])
            data = data[self.inputs['api_value_names']]
        except:
            logger.warning(f'Connection to {self.inputs["api_name"]} failed...')
            data = pd.DataFrame(self.inputs['api_except_values'])
        ### data transformation using custom functions if needed
        if self.api_function_name != 'None':
            f = getattr(TranformingFunctions, self.api_function_name)
            data = f(data)
        data['execution date'] = time.strftime("%a, %d %b %Y %H:%M:%S +0000",
                                               time.gmtime())
        return(data)
    
    def send_data(self):
        '''
        Function to send data into a kafka topic
        '''
        logger.info(f'submiting data from {self.inputs["api_name"]} \
                      to kafka topic {self.outputs["kafka_topic_name"]}')
        try:
            producer = KafkaProducer(bootstrap_servers=[self.outputs['kafka_url']],
                            value_serializer=lambda x: json.dumps(x)
                                                           .encode('utf-8'))
            producer.send(self.outputs['kafka_topic_name'],
                            value=self.data.to_dict(orient='records'))
        except:
            logger.warning(f'Unable to submit data from {self.inputs["api_name"]} \
                           into {self.outputs["kafka_topic_name"]}')
            return False
        else:
            logger.info(f'{self.data.shape[0]} rows of data from \
                          {self.inputs["api_name"]} deposited into \
                          {self.outputs["kafka_topic_name"]} succesfully!')
            return True
  
    def generate_data(self):
        '''
        Main function to obtain data from an API, concatenate to a dataframe
        and send it to a kafka topic.
        '''
        logger.info(f'Starting {self.inputs["api_name"]} service...')
        submittime = starttime = time.time()
        ### starting service
        while True:
            time.sleep(self.inputs['api_get_frecuency'])
            ### get data from API and concat to previous
            self.data = pd.concat([self.data, self.receive_data()])
            if time.time() - submittime >= self.outputs['kafka_submit_frecuency']:
                logger.info(f'submiting data from {self.inputs["api_name"]} \
                              to kafka topic {self.outputs["kafka_topic_name"]}...')
                ### try to submit data into kafka
                if self.send_data():
                    self.data = pd.DataFrame()
                else:
                    logger.info(f'keeping data until next upload')
                submittime = time.time()
            ### check if reached maximum running time
            if (time.time() - starttime) >= self.service_max_length:
                logger.info(f'max_length ({self.service_max_length} secs) \
                              reached. Stoping service {self.inputs["api_name"]}')
                break

class ProcessWatcher:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.processes = {}

    def add_proces(self, n, endpoint):
        '''
        Function to add an endpointreader as a new process at 
        the n position in the watcher
        '''
        attempt = 0 
        while attempt < self.api_max_reads_attemps:
            attempt += 1
            try:
                p = Process(target=endpoint.generate_data)
                p.name = endpoint.inputs['api_name']
                p.start()
                self.processes[n] = (p, endpoint)
            except:
                logger.warning(f'Starting attempt {attempt} of endpoint \
                                 {endpoint.inputs["api_name"]} failed.')
                if attempt < self.api_max_reads_attemps:
                    logger.info(f'Retry in {self.restar_sleep_time} sec...')
                    time.sleep(self.restar_sleep_time)
                else:
                    logger.error(f'ERROR: endpoint {endpoint.inputs["api_name"]} failed \
                                   to start! skipping...')
            else:
                logger.info(f'Process {p.name} started succesfully!')
                break
        

    def process_watcher(self):  
        starttime = time.time()
        while len(self.processes) > 0:
            if time.time() - starttime > self.watcher_max_uptime:
                logger.info(f'Maximum uptime ({self.watcher_max_uptime}) \
                              reached. Finishing services')
                for n in list(self.processes.keys()):
                    p, endpoint = self.processes[n]
                    p.terminate()
                break
            for n in list(self.processes.keys()):
                p, endpoint = self.processes[n]
                time.sleep(self.watcher_sleep_time)
                if p.is_alive():
                    pass
                else:
                    if p.exitcode == 0:
                        logger.info(f'process {p.name} finished succesfully.')
                        del self.processes[n]
                    else:
                        self.process_restart(p, n, endpoint)

    def process_restart(self, p, n, endpoint):                
        logger.warning('process finished abnormally. \
                                        Restarting...')
        attempt = 0 
        while attempt < self.max_reads_attemps:
            attempt += 1 
            try:
                self.processes[n] = self.add_proces(endpoint)
            except:
                logger.warning(f'Restart attempt number \
                                    {attempt+1} failed. retry  in \
                                    {self.restar_sleep_time} sec...')
                if attempt < self.max_reads_attemps:
                    logger.info(f'Retry in \
                                    {self.restar_sleep_time} sec...')
                    time.sleep(self.restar_sleep_time)
                else:
                    logger.error(f'ERROR: service {p.name} \
                                    failed to restart! skipping...')
                    del self.processes[n]
            else:
                logger.info(f'Service {p.name} \
                                restarted succesfully!')
                break

class TranformingFunctions:

    def transforming_function_1(data):
        '''
        Example transforming function:
        Calculate age based on dob and current date
        '''
        from datetime import datetime
        import numpy as np
        import math
        if data['dob'][0] == 'No Data':
            data['dob.age'] = 'No Data'
        else:
            data['dob.age'] = math.floor((datetime.now() 
                                          - pd.to_datetime(data['dob'][0])) \
                                          / np.timedelta64(1, 'Y'))
        return data
