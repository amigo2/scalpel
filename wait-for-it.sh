#!/usr/bin/env bash
# wait-for-it.sh
# Use this script to test if a given TCP host/port are available

TIMEOUT=30
QUIET=0

echoerr() { if [ "$QUIET" -ne 1 ]; then echo "$@" 1>&2; fi }

usage() {
    echo "Usage: $0 host:port [-t timeout] [-- command args]"
    exit 1
}

if [ $# -lt 1 ]; then
    usage
fi

hostport=$1
shift
IFS=: read host port <<< "$hostport"
if [ -z "$host" ] || [ -z "$port" ]; then
    echoerr "Error: you need to provide a valid host:port"
    usage
fi

while ! nc -z "$host" "$port"; do
    >&2 echo "Waiting for $host:$port..."
    sleep 1
    ((TIMEOUT--))
    if [ "$TIMEOUT" -le 0 ]; then
        >&2 echo "Timeout waiting for $host:$port"
        exit 1
    fi
done

if [ $# -gt 0 ]; then
    exec "$@"
fi
