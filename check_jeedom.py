#!/usr/bin/python
import urllib2
import json
import argparse
import sys

#Handler for json-rpc API
class handler:
    parameters = {
          "jsonrpc" : "2.0",
          "method" : "ping",
          "params" : {},
          "id" : "0" }

    headers = { 'Content-Type': 'application/json' }

    def __init__(self, ip, apikey):
        self.ip = ip
        self.parameters["params"]["apikey"] = apikey


    def ping(self):
        self.parameters["method"] = "ping"
        return self.send()

    def send(self):
        data = json.dumps(self.parameters)
        url = "http://%s/core/api/jeeApi.php"% ( self.ip )
        req = urllib2.Request(url, data, self.headers)
        response = urllib2.urlopen(req)
        fulljson = response.read()
        myjson = json.loads(fulljson)
        return  myjson["result"]

    def method(self, method):
        self.parameters["method"] = method
        return self.send()


parser = argparse.ArgumentParser(prog='check_jeedom')
parser.add_argument('type', choices=['status','plugin','update'], help='Type of check, should be status or plugin')
parser.add_argument('--name', help='name of plugin')
parser.add_argument('--apikey', help='jeedom api key')
parser.add_argument('--host', help='jeedom host IP address')
parser.add_argument('-w', '--warning', default=0, help='percent of failed plugins above which we trigger warning')
parser.add_argument('-c', '--critical', default=0, help='percent of failed plugins above which we trigger alert')

args=parser.parse_args()

api = handler(args.host, args.apikey)                  

import pprint, json                                                             

if args.type == 'update':
    plugins_update = []
    result = api.method("update::all")
    for plugin in result:
        if plugin['status'] == 'update':
            plugins_update.append(plugin['name'])

    if len(plugins_update) > 0:
        print("WARNING: %d plugins to update | %s" % (len(plugins_update), plugins_update))
        sys.exit(1)

    print "OK: eveything is up to date"
    sys.exit(0)

if args.type == 'status':
    result = api.method("jeedom::isOk")

    if result:
        print("OK: Jeedom is ok")
        sys.exit(0)
    else:
        print("Critical : Global problem on jeedom")
        sys.exit(2)

if args.type == 'plugin':
    plugins_list = []
    plugins_state = { 'ok': [], 'nok': [] }
    if args.name is None:
        plugins = api.method("plugin::listPlugin")
        for plugin in plugins:
            if plugin['hasOwnDeamon']:
                plugins_list.append(plugin['id'])
    else:
        plugins_list.append(args.name)

    for plugin in plugins_list:
        api.parameters['params']['plugin_id'] = plugin
        fulljson = api.method("plugin::deamonInfo")
        plugins_state[fulljson['state']].append(plugin)

    nb_failed = len(plugins_state['nok'])
    nb_ok = len(plugins_state['ok'])
    nb_all = nb_failed+nb_ok

    if nb_ok == 0:
        print("Critical: No plugins with daemon ok are running")
        sys.exit(2)
    else:
        failed_percent = float(nb_failed)/float(nb_all) * 100.0
        if failed_percent > float(args.critical):
            print("Critical: %d/%d plugins down %s" % (nb_failed, nb_all, plugins_state['nok']))
            sys.exit(2)

        if failed_percent > float(args.warning):
            print("Warning: %d/%d plugins down" % (nb_failed, nb_all))
            sys.exit(1)

        print("OK: %d/%d plugins down" % (nb_failed, nb_all))
        sys.exit(0)

