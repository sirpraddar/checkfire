from CheckFireNode.CFNApp import CFNApp, CONF_FILE
import configparser

if __name__ == '__main__':
    conf = configparser.ConfigParser()
    conf.read(CONF_FILE)
    address = conf['Socket']['Address']
    port = conf['Socket']['Port']

    CFNApp.run(address,port,debug=True)