const { _android: android } = require('playwright');
const { spawn } = require('child_process');

const PAUSE_INTERVAL = 2000;

function delay(ms) {
  return new Promise( resolve => setTimeout(resolve, ms) );
}

(async () => {
  // Connect to the device.
  const [device] = await android.devices();
  console.log(`Model: ${device.model()}`);
  console.log(`Serial: ${device.serial()}`);
  
  // Take screenshot of the whole device.
  await device.screenshot({ path: 'device.png' });

  for (let i=1; i<4; i++) {

  const ts = spawn('tshark',
           ['-i', 'Local Area Connection* 2', '-w', 'android_trace' + i + '.pcapng', '-f', 'src host 192.168.137.36 and udp port 1194']
          );

  {
    // --------------------- chrome Browser -----------------------

    // Launch Chrome browser.
    await device.shell('am force-stop com.android.chrome');
    const context = await device.launchBrowser();

    // Use BrowserContext as usual.
    const page = await context.newPage();
    await page.goto('https://www.uhasselt.be');
    console.log(await page.evaluate(() => window.location.href));
    
    await page.click('xpath=//a[@href="/UH/nl/InfoVoor/studenten-en-doctorandi.html"]');
    await delay(PAUSE_INTERVAL);
    
    await page.click('xpath=//a[@href="/"] >> visible=true');
    await delay(PAUSE_INTERVAL);

    await page.click('//a[@href="/UH/nl/InfoVoor/InfoVoor-Sollicitanten.html"]');
    await delay(PAUSE_INTERVAL);

    await context.close();
  }

  ts.kill();
  }

  // Close the device.
  await device.close();
})();