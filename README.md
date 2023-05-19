# XInput-Bass-Vibrator
A program that vibrates XInput devices based on bass output from the default audio output

Up to 4 controllers are supported.

This offers the functionality of acousto-haptic vests and gloves, but at a much lower price.

[Buy me a coffee](https://www.buymeacoffee.com/sserver224)

# NOTE:
The included VB-Cable must be installed along with a split audio output program (eg OBS+Audio Monitor). 

To use the included OBS + Audio Monitor for splitting:

1. Desktop Audio Settings Cog > Filters... > Audio Monitor.
2. Name can be anything you want.
3. On the newly created filter, select the VB Cable as your monitor output.

Launch the app. Then, go to Windows Settings then System > Sound > Volume mixer > Bass Vibrator (expand) then select CABLE Output as the input device for that app. Relaunch the app for the settings to take effect.

Ignore any antivirus warnings, as my program is recently released, which can cause antiviruses to give a warning or even remove the file.

The audio splitting program must be running for the program to work.

If the controller(s) do not vibrate during heavy bass, see if the vibration meter (to the left of the intensity slider) is showing anything. If it is not bouncing around or is very low in value, check if your audio splitting program is running and sending audio from the default audio output to the VB Cable. If it is, try using your media player's equalizer (if using VLC or another Windows media player), an equalizer browser extension (if playing games or music or watching videos online), or [Equalizer APO](https://sourceforge.net/projects/equalizerapo/) + [Peace](https://sourceforge.net/projects/peace-equalizer-apo-extension/) (any other case or if none of these work) to boost the bass.

If there is latency in the vibrations when using wired headphones/speakers, try playing audio through a Bluetooth audio device to "lag" the sound a bit so it syncs up with the vibrations.

OBS (with necessary plugins): https://drive.google.com/file/d/1II3nyKbAy5YOEfShlgLsGeU040QMhkKW/view?usp=sharing

Controllers with precise haptics, such as the Joy-Con, Nintendo Switch Pro Controller, or the DualSense (PS5 controller) are recommended.

Turn off right motor rumble if the right motor on the controller seems like to be an on/off motor and does not use a gradient. One example of a controller like this is the DualShock 3.

# BUGS:

Response curve may be too strict

Adding more controllers may decrease responsiveness and/or increase latency

# How to pair controllers from popular consoles to your PC

To connect an Xbox controller to your Windows PC, pair/connect it like you do for any Bluetooth device.

To connect a Nintendo Switch, DualShock 4, or DualSense controller to your Windows PC, pair it like an Xbox Controller and use [DS4Windows](https://github.com/Ryochan7/DS4Windows/releases/tag/v3.2.10).

To connect a DualShock 3 controller to your Windows PC using BthPS3 and DSHidMini (preferred option, works wired and wireless), see below:

Full and updated instructions here: https://vigem.org/projects/DsHidMini/. 

1. First, turn on Bluetooth.

2. BthPS3: Download and install these bluetooth drivers (follow instructions therein) https://github.com/ViGEm/BthPS3/releases. If you get an error, make sure that your bluetooth is on before launching the installer. See the FAQ at the DsHidMini page if you still have errors (https://vigem.org/projects/DsHidMini)

3. DsHidMini: Download this: https://github.com/ViGEm/DsHidMini/releases. Extract all files from the zip file, and save them in a folder that you'll remember. You'll use this whenever you need to set up a new DS3 controller.

4. In the DsHidMini files, go to the x64 folder (for 64 bit PCs) or x86 folder (for 32 bit), subfolder "dshidmini" and right-click on each setup information file (dshidmini.inf and igfilter.inf) and select "install".

First-time controller connection and setup

5. Now, to get the controllers detected wirelessly, launch DSHMC.exe (as Admin), which is among the files extracted from the DsHidMini zip.

6. Plug your PS3 controller via a USB cable. The controller should now appear listed in the program (left-hand pane), indicating that it has been detected.

7. Select the controller on the left-hand side list to display details and options, and under "HID device mode", select XInput. This is crucial so it can be recognized by my program.

8. Remove the USB cable and press the PS button to connect wirelessly. You may need to restart your computer once or twice for the connection to work.

Note: When using this method the program will read the controller's battery as 'Critical' because it does not output battery information.

Alternatively, you can use [SCPToolkit](https://github.com/nefarius/ScpToolkit/releases) to connect your DualShock 3 using a USB cable. To wirelessly use the controller you must use a Bluetooth dongle and install its driver. 
