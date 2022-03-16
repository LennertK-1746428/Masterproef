#!/bin/bash

# Browsers
chrome="chrome"
firefox="firefox"
#edge="edge"
browsers=( "$chrome" "$firefox" ) #"$edge" )

# Timeout (s)
timeout=3600

# Paths
script_path='/home/lennert/Documents/Masterproef/Repository/noisy/noisy.py'
config_path='/home/lennert/Documents/Masterproef/Repository/noisy/config.json'
output_path='/home/lennert/Documents/Masterproef/VPN_dataset'
drivers_path='/home/lennert/Documents/Masterproef/Repository/webcrawlers/linux/webdrivers'

for b in "${browsers[@]}"
do

    echo "=========================="
    echo "$b Browsing"
    echo "=========================="

    python3 $script_path --config $config_path --timeout $timeout --browser $b --os linux --interface wlp0s20f3 --traffic browsing --output_dir $output_path --drivers_dir $drivers_path

    echo "=========================="
    echo "$b Streaming Twitch"
    echo "=========================="

    python3 $script_path --config $config_path --timeout $timeout --browser $b --os linux --interface wlp0s20f3 --traffic streaming_twitch --output_dir $output_path --drivers_dir $drivers_path

    echo "=========================="
    echo "$b Streaming YouTube"
    echo "=========================="

    python3 $script_path --config $config_path --timeout $timeout --browser $b --os linux --interface wlp0s20f3 --traffic streaming_youtube --output_dir $output_path --drivers_dir $drivers_path

done