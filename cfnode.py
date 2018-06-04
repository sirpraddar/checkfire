from CheckFireNode.CFNApp import CFNApp
import configparser

if __name__ == '__main__':
    conf = configparser.ConfigParser()
    conf.read('node.conf')
    address = conf['Socket']['Address']
    port = conf['Socket']['Port']

    CFNApp.run(address,port,debug=True)