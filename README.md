== README ==

This plugin allows you to check jeedom from json-rpc API.

For the moment, this plugin checks :
* global status of jeedom
* state of plugins with daemons
* status of available plugin updates

=== usage ===
```
usage: check_jeedom [-h] [--name NAME] [--apikey APIKEY] [--host HOST]
                    [-w WARNING] [-c CRITICAL]
                    {status,plugin,update}
```

`--host` and `--apikey`are mandatory arguments to connect to jeedom host
`--name` is used to specify a plugin name to check this daemon

=== prerequisite ===
To work, it needs the following python modules :
* urllib2
* json
* argparse
* sys


