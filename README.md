# Logerizer

## a TCP proxy for [logstash](http://logstash.net "Logstash: open source log management")

_copyright 2014, Paul Stevens, paul@nfg.nl, GPLv3_


Cleans up syslogs, where multi-line messages are split-up by syslog and each
line is prepended seprately by the same timestamp and process identifier.

The proxy collect such split-up messages into one message with one single
timestamp and process identifier, and passes it on to the destination -
[logstash](http://logstash.net "Logstash: open source log management") in this
case.

This package requires *python >= 3.4.0*.

Run `make` to do a buildout. This results in two callables; `bin/log_proxy` and
`bin/tcp_sink`.

The first one is the actual proxy, the sink is for testing purposes: it spits
out anything send to it over tcp on stdout.

##tcp_sink

usage: tcp_sink [-h] [--listen LISTEN]

Sink tcp data

optional arguments:
  -h, --help       show this help message and exit
  --listen LISTEN

##log_proxy

usage: log_proxy [-h] [--listen LISTEN] [--sendto SENDTO]

Cleanup syslog messages

optional arguments:
  -h, --help       show this help message and exit
  --listen LISTEN
  --sendto SENDTO


---
