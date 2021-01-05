#!/usr/bin/with-contenv bashio

CONFIG_PATH=/data/options.json

export MAC="$(bashio::config 'mac')"
export CONFIG_PATH="$(bashio::config 'config_path')"
export DEBUG="$(bashio::config 'debug')"

if [[ ! -z "$(bashio::config 'deconz_ip')" ]]; then
    export DECONZ="$(bashio::config 'deconz_ip')"
fi

if [[ ! -z "$(bashio::config 'no-serve-https')" ]]; then
    export NO_SERVE_HTTPS="$(bashio::config 'no-serve-https')"
else
    export NO_SERVE_HTTPS="false"
fi

CONFIG_PATH=/data/config/diyhue

if [[ -d $CONFIG_PATH ]]; then
    echo "$CONFIG_PATH exists."
else
    mkdir -p $CONFIG_PATH
    echo "$CONFIG_PATH created."
fi


echo "Your Architecture is $BUILD_ARCHI"

if [ "$NO_SERVE_HTTPS" = "true" ] ; then
    echo "No serve HTTPS"
    python3 -u /opt/hue-emulator/HueEmulator3.py --docker --no-serve-https
else 
    echo "Serve HTTPS"
    python3 -u /opt/hue-emulator/HueEmulator3.py --docker
fi
