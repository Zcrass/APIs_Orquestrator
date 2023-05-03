# APIS Orquestator example

A simple program to handle endpoints data.

## Process
This program reads data from one o several endpoints in JSON format. Then each set of data can be proccesed if required and finally send it to a kafka topic.
If connection to the endpoint fails a set of exception values can be stored. While if connection to kafka fails, data is retained until next sumbmission.
Each endpoint is independent and runs in parallel processes. Aditionally this programs monitor the status of each process and in case of the failure of one it can restart it.

### Input
Input consist on data produced by one o several endpoints APIs in JSON format.
### Output
Output is a JSON table with a series of predefined fields.

## Content
This program includes the following files:
- app/main.py: correspond to the main program. Requires an argument -i (input) which indicates the path to the json config file
- app/utils.py: classes and functions used by the main program
- configure_APIS_Orquestator.json: configuration file
- requeriments.txt: list of dependencies required
- readme.md: this file


## Configuration
Configuration is made by a JSON file with two main fields: endpoints and processwatcher.

```json
{
    "endpoints": {
    },

    "processwatcher": {
    }
}
```
The endpoints field contain a list of endpoints from which its goin to receive the data:

```json
"endpoints":[
        {
            "api_name":"randomuser_00",
            "api_url":"https://randomuser.me/api/",
            "api_value_names":["name.first", "dob.age"],
            "api_except_values":{"name.first":["No Data"], "dob.age":["No Data"]},
            "api_get_frecuency":1,
            "api_function_name":"None",
            "kafka_topic_name":"randomuser_00", 
            "kafka_url":"localhost:9092",
            "kafka_submit_frecuency":5,
            "service_max_length":15
        },
        {
            "api_name":"randomuser_01",
            "api_url":"https://randomuser.me/api/1.1",
            "api_value_names":["name.first", "dob"],
            "api_except_values":{"name.first":["No Data"], "dob":["No Data"]},
            "api_get_frecuency":2,
            "api_function_name":"transforming_function_1",
            "kafka_topic_name":"randomuser_01", 
            "kafka_url":"localhost:9092",
            "kafka_submit_frecuency":5,
            "service_max_length":600
        }
    ]
```
Each of the endpoints in the list contains a series of values for their configuration:
- "api_name": endpoint name
- "api_url": endpoint url to get data
- "api_value_names": value names to get data from
- "api_except_values": values to asing in case of a connection error 
- "api_get_frecuency": frecuency to contact the endpoint in seconds
- "api_function_name": function to use to process data collected. If "None" then data is saved as received from the endpoint
- "kafka_topic_name": kafka topic name to deposit the output from this endpoint 
- "kafka_url": kafka topic url
- "kafka_submit_frecuency": frecuency to submit data into the kafka topic
- "service_max_length": max uptime of this endpoint

By its part, the field "processwatcher" contains parameters to monitor the processes.

```json
"processwatcher":{    
        "watcher_max_uptime":20,
        "watcher_sleep_time":1,
        "max_restar_attempts":5,
        "restar_sleep_time":1
    }
```
- "watcher_max_uptime": max uptime to keep all the processes running in seconds
- "watcher_sleep_time": wait time to monitor the processes in seconds
- "max_restar_attempts": max attemps to start/restart a process
- "restar_sleep_time": wait time between start/restart attempts


