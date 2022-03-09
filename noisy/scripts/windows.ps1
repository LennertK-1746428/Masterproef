# Browsers
$chrome = "chrome"
$firefox = "firefox"
$edge = "edge"
$browsers = $edge #$chrome, $firefox #, $edge

# Timeout (s)
$timeout = 3600

# Paths
$script_path = 'G:\My Drive\Informatica\Master\Masterproef\Code\Repository\noisy\noisy.py'
$config_path = 'G:\My Drive\Informatica\Master\Masterproef\Code\Repository\noisy\config.json'
$output_path = 'C:\Users\lenne\Documents\VPN_dataset'
$drivers_path = 'G:\My Drive\Informatica\Master\Masterproef\Code\Repository\webcrawlers\windows\webdrivers'

Foreach ($b in $browsers) 
{

echo "=========================="
echo "$b Browsing"
echo "=========================="

python $script_path --config $config_path --timeout $timeout --browser $b --os windows --interface WiFi --traffic browsing --output_dir $output_path --drivers_dir $drivers_path | Out-Null

echo "=========================="
echo "$b Streaming Twitch"
echo "=========================="

python $script_path --config $config_path --timeout $timeout --browser $b --os windows --interface WiFi --traffic streaming_twitch --output_dir $output_path --drivers_dir $drivers_path | Out-Null

echo "=========================="
echo "$b Streaming YouTube"
echo "=========================="

python $script_path --config $config_path --timeout $timeout --browser $b --os windows --interface WiFi --traffic streaming_youtube --output_dir $output_path --drivers_dir $drivers_path | Out-Null

}

python $script_path --config $config_path --timeout $timeout --browser firefox --os windows --interface WiFi --traffic streaming_youtube --output_dir $output_path --drivers_dir $drivers_path | Out-Null

# Read-Host -Prompt "Done.. Press Enter to exit"