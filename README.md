# Upload micropython to ESP32
## Requirements
* Visual studio code
* Python
* Nodejs

## Flash micropython
To upload micropython to the ESP32 the board must first be flashed with the micropython firmware

### Install esptool
Install esptool with pip:
`pip install esptool`

### Download micropython binaries
Go to the micropython download page for esp32 ([link](https://micropython.org/download/?port=esp32)). And download the latest binary. The standard Espressif ESP32 binary seems to work well

### Erase and flash the board
1. Erase the ESP32 flash:
`python -m esptool --chip esp32 --port <COM-PORT> --baud 460800 erase_flash`
2. Flash micropython:
`python -m esptool --chip esp32 --port <COM-PORT> --baud 460800 write_flash -z 0x1000 micropython.bin`

#### Verify
To verify micropython has been sucessfully flashed, connect to the board over serial. If micropython was successfully flashed you should be presented with a python interpreter.

## Install Pymakr
_Node.js must be installed prior to installing Pymakr_
1. Click on the extensions tab in Visual studio code
2. Search for **Pymakr**
3. Install the Pymakr extension (_not the preview version_)
4. Verify the extension is installed by looking for the Pymakr logo in the sidebar

## Upload project with Pymakr
1. Open the _Pymakr_ tab and connect to the board
2. Switch back to the _Explorer_ tab
3. Right click the root project folder -> pymakr -> Upload to device (_opens dialoug_)
4. Select the board and file location
5. Once the code has uploaded, reset the board

## Troubleshooting
#### Pymakr not working
- Restarting visual studio code often fixes most issues with Pymakr
#### Pymakr waiting to upload code forever
- If code is already running on the board, it has to be stopped before uploading.
- To do this, connect to the board over serial and press CRTL+C until the interpreter shows
