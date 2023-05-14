import pyaudio
import numpy as np
from tkinter import *
from tkinter.ttk import *
import os, sys
from XInput import *
import pystray
import ctypes, comtypes
from ctypes import wintypes
from pystray import MenuItem as item
from PIL import Image
from threading import Thread
from idlelib.tooltip import Hovertip
import time
import socket
import re
FORMAT = pyaudio.paInt16# audio format
CHANNELS = 1 # mono audio
RATE=44100
CHUNK=1024
def get_resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
def close():
    try:
        root.destroy()
    except:
        pass
    for i in range(4):
        set_vibration(i, 0, 0)
    stream.stop_stream()
    stream.close()
    p.terminate()
    for i in range(4):
        set_vibration(i, 0, 0)
    sys.exit()
import struct
from scipy.signal import butter, lfilter
def is_valid_ipv4(ip):
    """Validates IPv4 addresses.
    """
    pattern = re.compile(r"""
        ^
        (?:
          # Dotted variants:
          (?:
            # Decimal 1-255 (no leading 0's)
            [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
          |
            0x0*[0-9a-f]{1,2}  # Hexadecimal 0x0 - 0xFF (possible leading 0's)
          |
            0+[1-3]?[0-7]{0,2} # Octal 0 - 0377 (possible leading 0's)
          )
          (?:                  # Repeat 0-3 times, separated by a dot
            \.
            (?:
              [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
            |
              0x0*[0-9a-f]{1,2}
            |
              0+[1-3]?[0-7]{0,2}
            )
          ){0,3}
        |
          0x0*[0-9a-f]{1,8}    # Hexadecimal notation, 0x0 - 0xffffffff
        |
          0+[0-3]?[0-7]{0,10}  # Octal notation, 0 - 037777777777
        |
          # Decimal notation, 1-4294967295:
          429496729[0-5]|42949672[0-8]\d|4294967[01]\d\d|429496[0-6]\d{3}|
          42949[0-5]\d{4}|4294[0-8]\d{5}|429[0-3]\d{6}|42[0-8]\d{7}|
          4[01]\d{8}|[1-3]\d{0,9}|[4-9]\d{0,8}
        )
        $
    """, re.VERBOSE | re.IGNORECASE)
    return pattern.match(ip) is not None
def audio_callback(in_data, frame_count, time_info, status):
    # Convert raw bytes to numpy array of 16-bit integers
    samples = np.frombuffer(in_data, dtype=np.int16)
    
    # Apply window function to reduce spectral leakage
    window = np.hamming(len(samples))
    samples = samples * window
    
    # Compute power spectrum using FFT algorithm
    spectrum = np.abs(np.fft.fft(samples))**2
    
    # Define frequency range of interest
    freq_range = (20, 120)  # Hz
    
    # Find indices corresponding to frequency range of interest
    f = np.fft.fftfreq(len(samples), 1/RATE)
    idx = np.logical_and(f >= freq_range[0], f <= freq_range[1])
    bass_spectrum = spectrum[idx]
    
    # Calculate total energy in bass range
    bass_energy = np.sum(bass_spectrum)
    
    # Define normalization factor
    max_value = np.iinfo(np.int16).max  # maximum value of 16-bit integer
    
    # Normalize energy value to range of 0.0 to 1.0
    bass_loudness = bass_energy / (max_value * len(bass_spectrum))
    # Print the loudness value
    if get_connected()[0]:
        if get_battery_information(0)[1]=='EMPTY':
            if time.time()%1>0.5:
                statusLabel.configure(text='Battery Critical', foreground='grey')
            else:
                statusLabel.configure(text='Battery Critical', foreground='red')
        elif get_battery_information(0)[1]=='LOW':
            statusLabel.configure(text='Battery Low', foreground='orange')
        else:
            statusLabel.configure(text='Connected', foreground='#00ff00')
        try:
            if IAudioEndpointVolume.get_default().GetMasterVolumeLevelScalar()>0 and IAudioEndpointVolume.get_default().GetMute()==0:
                vibBar['value']=min((bass_loudness/1919796895), 1.0)*vibSlider.get()
                set_vibration(0, min(float(bass_loudness/1919796895), 1.0)*vibSlider.get(), min(float(bass_loudness/1919796895)*int(rMotorEnable.instate(['selected'])), 1.0)*vibSlider.get())
            else:
                vibBar['value']=0
                set_vibration(0, 0, 0)
        except:
            vibBar['value']=0
            set_vibration(0, 0, 0)
    else:
        vibBar['value']=0
        statusLabel.configure(text='Not Connected', foreground='grey')
    if get_connected()[1]:
        if get_battery_information(1)[1]=='EMPTY':
            if time.time()%1>0.5:
                status1Label.configure(text='Battery Critical', foreground='grey')
            else:
                status1Label.configure(text='Battery Critical', foreground='red')
        elif get_battery_information(1)[1]=='LOW':
            status1Label.configure(text='Battery Low', foreground='orange')
        else:
            status1Label.configure(text='Connected', foreground='#00ff00')
        try:
            if IAudioEndpointVolume.get_default().GetMasterVolumeLevelScalar()>0 and IAudioEndpointVolume.get_default().GetMute()==0:
                vibBar1['value']=min((bass_loudness/1919796895), 1.0)*vibSlider1.get()
                set_vibration(1, min(float(bass_loudness/1919796895), 1.0)*vibSlider1.get(), min(float(bass_loudness/1919796895)*int(rMotorEnable1.instate(['selected'])), 1.0)*vibSlider1.get())
            else:
                vibBar1['value']=0
                set_vibration(1, 0, 0)
        except:
            vibBar1['value']=0
            set_vibration(1, 0, 0)
    else:
        vibBar1['value']=0
        status1Label.configure(text='Not Connected', foreground='grey')
    if get_connected()[2]:
        if get_battery_information(2)[1]=='EMPTY':
            if time.time()%1>0.5:
                status2Label.configure(text='Battery Critical', foreground='grey')
            else:
                status2Label.configure(text='Battery Critical', foreground='red')
        elif get_battery_information(2)[1]=='LOW':
            status2Label.configure(text='Battery Low', foreground='orange')
        else:
            status2Label.configure(text='Connected', foreground='#00ff00')
        try:
            if IAudioEndpointVolume.get_default().GetMasterVolumeLevelScalar()>0 and IAudioEndpointVolume.get_default().GetMute()==0:
                vibBar2['value']=min((bass_loudness/1919796895), 1.0)*vibSlider2.get()
                set_vibration(2, min(float(bass_loudness/1919796895), 1.0)*vibSlider2.get(), min(float(bass_loudness/1919796895)*int(rMotorEnable2.instate(['selected'])), 1.0)*vibSlider2.get())
            else:
                vibBar2['value']=0
                set_vibration(2, 0, 0)
        except:
            vibBar2['value']=0
            set_vibration(2, 0, 0)
    else:
        vibBar2['value']=0
        status2Label.configure(text='Not Connected', foreground='grey')
    if get_connected()[3]:
        if get_battery_information(3)[1]=='EMPTY':
            if time.time()%1>0.5:
                status3Label.configure(text='Battery Critical', foreground='grey')
            else:
                status3Label.configure(text='Battery Critical', foreground='red')
        elif get_battery_information(3)[1]=='LOW':
            status3Label.configure(text='Battery Low', foreground='orange')
        else:
            status3Label.configure(text='Connected', foreground='#00ff00')
        try:
            if IAudioEndpointVolume.get_default().GetMasterVolumeLevelScalar()>0 and IAudioEndpointVolume.get_default().GetMute()==0:
                vibBar3['value']=min((bass_loudness/1919796895), 1.0)*vibSlider3.get()
                set_vibration(3, min(float(bass_loudness/1919796895), 1.0)*vibSlider3.get(), min(float(bass_loudness/1919796895)*int(rMotorEnable3.instate(['selected'])), 1.0)*vibSlider3.get())
            else:
                vibBar3['value']=0
                set_vibration(3, 0, 0)
        except:
            vibBar3['value']=0
            set_vibration(3, 0, 0)
    else:
        vibBar3['value']=0
        status3Label.configure(text='Not Connected', foreground='grey')
    if root.socket_open:
        try:
            if IAudioEndpointVolume.get_default().GetMasterVolumeLevelScalar()>0 and IAudioEndpointVolume.get_default().GetMute()==0:
                vibBar4['value']=min((bass_loudness/1919796895), 1.0)*vibSlider4.get()
                sock.sendto(str(min((bass_loudness/1919796895), 1.0)*vibSlider3.get()).encode(), (addrEntry.get(),8556))    
            else:
                vibBar4['value']=0
                sock.sendto('0.0'.encode(), (addrEntry.get(),8556))
        except:
            vibBar4['value']=0
    else:
        vibBar4['value']=0
    return (None, pyaudio.paContinue)


# Create an instance of the PyAudio object
p = pyaudio.PyAudio()
n=0
while True:
    try:
        if p.get_device_info_by_index(n)["name"]=='CABLE Output (VB-Audio Virtual Cable)':
            try:
                os.system('SoundVolumeView.exe /SetAppDefault "VB-Audio Virtual Cable\Device\CABLE Output\Capture" 1 '+str(os.getpid()))
            except OSError:
                messagebox.showwarning('Loopback Device Found', 'Setting VB-Cable failed. Select the VB Cable by going to Settings>Sound>Volume mixer>Decibel Meter and select CABLE Output as input device')
            break
        else:
            n+=1
    except OSError:
        messagebox.showerror('No Loopback Device found', 'There is no Virtual Cable installed on this machine. This app will now close.')
        appclosed=True
        os._exit(1)
# Create a stream object with the audio callback function
MMDeviceApiLib = comtypes.GUID(
    '{2FDAAFA3-7523-4F66-9957-9D5E7FE698F6}')
IID_IMMDevice = comtypes.GUID(
    '{D666063F-1587-4E43-81F1-B948E807363F}')
IID_IMMDeviceCollection = comtypes.GUID(
    '{0BD7A1BE-7A1A-44DB-8397-CC5392387B5E}')
IID_IMMDeviceEnumerator = comtypes.GUID(
    '{A95664D2-9614-4F35-A746-DE8DB63617E6}')
IID_IAudioEndpointVolume = comtypes.GUID(
    '{5CDF2C82-841E-4546-9722-0CF74078229A}')
CLSID_MMDeviceEnumerator = comtypes.GUID(
    '{BCDE0395-E52F-467C-8E3D-C4579291692E}')

# EDataFlow
eRender = 0 # audio rendering stream
eCapture = 1 # audio capture stream
eAll = 2 # audio rendering or capture stream
# ERole
eConsole = 0 # games, system sounds, and voice commands
eMultimedia = 1 # music, movies, narration
eCommunications = 2 # voice communications

LPCGUID = REFIID = ctypes.POINTER(comtypes.GUID)
LPFLOAT = ctypes.POINTER(ctypes.c_float)
LPDWORD = ctypes.POINTER(wintypes.DWORD)
LPUINT = ctypes.POINTER(wintypes.UINT)
LPBOOL = ctypes.POINTER(wintypes.BOOL)
PIUnknown = ctypes.POINTER(comtypes.IUnknown)
class IMMDevice(comtypes.IUnknown):
    _iid_ = IID_IMMDevice
    _methods_ = (
        comtypes.COMMETHOD([], ctypes.HRESULT, 'Activate',
            (['in'], REFIID, 'iid'),
            (['in'], wintypes.DWORD, 'dwClsCtx'),
            (['in'], LPDWORD, 'pActivationParams', None),
            (['out','retval'], ctypes.POINTER(PIUnknown), 'ppInterface')),
        comtypes.STDMETHOD(ctypes.HRESULT, 'OpenPropertyStore', []),
        comtypes.STDMETHOD(ctypes.HRESULT, 'GetId', []),
        comtypes.STDMETHOD(ctypes.HRESULT, 'GetState', []))

PIMMDevice = ctypes.POINTER(IMMDevice)

class IMMDeviceCollection(comtypes.IUnknown):
    _iid_ = IID_IMMDeviceCollection

PIMMDeviceCollection = ctypes.POINTER(IMMDeviceCollection)

class IMMDeviceEnumerator(comtypes.IUnknown):
    _iid_ = IID_IMMDeviceEnumerator
    _methods_ = (
        comtypes.COMMETHOD([], ctypes.HRESULT, 'EnumAudioEndpoints',
            (['in'], wintypes.DWORD, 'dataFlow'),
            (['in'], wintypes.DWORD, 'dwStateMask'),
            (['out','retval'], ctypes.POINTER(PIMMDeviceCollection),
             'ppDevices')),
        comtypes.COMMETHOD([], ctypes.HRESULT, 'GetDefaultAudioEndpoint',
            (['in'], wintypes.DWORD, 'dataFlow'),
            (['in'], wintypes.DWORD, 'role'),
            (['out','retval'], ctypes.POINTER(PIMMDevice), 'ppDevices')))
    @classmethod
    def get_default(cls, dataFlow, role):
        enumerator = comtypes.CoCreateInstance(
            CLSID_MMDeviceEnumerator, cls, comtypes.CLSCTX_INPROC_SERVER)
        return enumerator.GetDefaultAudioEndpoint(dataFlow, role)

class IAudioEndpointVolume(comtypes.IUnknown):
    _iid_ = IID_IAudioEndpointVolume
    _methods_ = (
        comtypes.STDMETHOD(ctypes.HRESULT, 'RegisterControlChangeNotify', []),
        comtypes.STDMETHOD(ctypes.HRESULT, 'UnregisterControlChangeNotify', []),
        comtypes.COMMETHOD([], ctypes.HRESULT, 'GetChannelCount',
            (['out', 'retval'], LPUINT, 'pnChannelCount')),
        comtypes.COMMETHOD([], ctypes.HRESULT, 'SetMasterVolumeLevel',
            (['in'], ctypes.c_float, 'fLevelDB'),
            (['in'], LPCGUID, 'pguidEventContext', None)),
        comtypes.COMMETHOD([], ctypes.HRESULT, 'SetMasterVolumeLevelScalar',
            (['in'], ctypes.c_float, 'fLevel'),
            (['in'], LPCGUID, 'pguidEventContext', None)),
        comtypes.COMMETHOD([], ctypes.HRESULT, 'GetMasterVolumeLevel',
            (['out','retval'], LPFLOAT, 'pfLevelDB')),
        comtypes.COMMETHOD([], ctypes.HRESULT, 'GetMasterVolumeLevelScalar',
            (['out','retval'], LPFLOAT, 'pfLevel')),
        comtypes.COMMETHOD([], ctypes.HRESULT, 'SetChannelVolumeLevel',
            (['in'], wintypes.UINT, 'nChannel'),
            (['in'], ctypes.c_float, 'fLevelDB'),
            (['in'], LPCGUID, 'pguidEventContext', None)),
        comtypes.COMMETHOD([], ctypes.HRESULT, 'SetChannelVolumeLevelScalar',
            (['in'], wintypes.UINT, 'nChannel'),
            (['in'], ctypes.c_float, 'fLevel'),
            (['in'], LPCGUID, 'pguidEventContext', None)),
        comtypes.COMMETHOD([], ctypes.HRESULT, 'GetChannelVolumeLevel',
            (['in'], wintypes.UINT, 'nChannel'),
            (['out','retval'], LPFLOAT, 'pfLevelDB')),
        comtypes.COMMETHOD([], ctypes.HRESULT, 'GetChannelVolumeLevelScalar',
            (['in'], wintypes.UINT, 'nChannel'),
            (['out','retval'], LPFLOAT, 'pfLevel')),
        comtypes.COMMETHOD([], ctypes.HRESULT, 'SetMute',
            (['in'], wintypes.BOOL, 'bMute'),
            (['in'], LPCGUID, 'pguidEventContext', None)),
        comtypes.COMMETHOD([], ctypes.HRESULT, 'GetMute',
            (['out','retval'], LPBOOL, 'pbMute')),
        comtypes.COMMETHOD([], ctypes.HRESULT, 'GetVolumeStepInfo',
            (['out','retval'], LPUINT, 'pnStep'),
            (['out','retval'], LPUINT, 'pnStepCount')),
        comtypes.COMMETHOD([], ctypes.HRESULT, 'VolumeStepUp',
            (['in'], LPCGUID, 'pguidEventContext', None)),
        comtypes.COMMETHOD([], ctypes.HRESULT, 'VolumeStepDown',
            (['in'], LPCGUID, 'pguidEventContext', None)),
        comtypes.COMMETHOD([], ctypes.HRESULT, 'QueryHardwareSupport',
            (['out','retval'], LPDWORD, 'pdwHardwareSupportMask')),
        comtypes.COMMETHOD([], ctypes.HRESULT, 'GetVolumeRange',
            (['out','retval'], LPFLOAT, 'pfLevelMinDB'),
            (['out','retval'], LPFLOAT, 'pfLevelMaxDB'),
            (['out','retval'], LPFLOAT, 'pfVolumeIncrementDB')))
    @classmethod
    def get_default(cls):
        endpoint = IMMDeviceEnumerator.get_default(eRender, eMultimedia)
        interface = endpoint.Activate(cls._iid_, comtypes.CLSCTX_INPROC_SERVER)
        return ctypes.cast(interface, ctypes.POINTER(cls))
def start_stop():
    if not root.socket_open:
        if is_valid_ipv4(addrEntry.get()):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            except:
                return
            else:
                root.socket_open=True
                addrEntry.config(state=DISABLED)
                startButton.config(text='Stop')
    else:
        try:
            sock.close()
        except:
            pass
        addrEntry.config(state=NORMAL)
        startButton.config(text='Start')
root=Tk()
root.title('Bass Vibrator')
LEFT='left'
root.socket_open=False
root.resizable(False, False)
Label(root, text='Bass Vibrator Settings').pack()
root.protocol('WM_DELETE_WINDOW', root.withdraw)
image = Image.open(get_resource_path('snd.ico'))
menu = (item('Restore', root.deiconify), item('Exit', close))
icon = pystray.Icon("name", image, "Bass Vibrator", menu)
Thread(target=icon.run, daemon=True).start()
root.iconbitmap(get_resource_path('snd.ico'))
linkIn=Checkbutton(root, text='Link Intensity Sliders', state=DISABLED)
linkIn.pack()
linkIn.state(['!alternate'])
Hovertip(linkIn,'This has not been implemented yet')
frame1=LabelFrame(root, text='Controller 1')
frame1.pack(anchor=NW)
Label(frame1, text='Status:').pack(side=LEFT)
statusLabel=Label(frame1, text='Not Connected', foreground='grey', width=15)
statusLabel.pack(side=LEFT, padx=5)
vibBar=Progressbar(frame1, maximum=1, length=200)
vibBar.pack(side=LEFT, padx=5)
vibSlider=Scale(frame1, from_=0, to=1, length=200)
vibSlider.pack(side=LEFT, padx=5)
rMotorEnable=Checkbutton(frame1, text='Right Motor Rumble')
rMotorEnable.pack(side=LEFT, padx=5)
rMotorEnable.state(['!alternate', 'selected'])
Hovertip(rMotorEnable,'Some controllers, like the DualShock 3, have a right motor that does not have a rumble gradient. If your controller has a right motor that does not have a rumble gradient, uncheck the box.')
frame2=LabelFrame(root, text='Controller 2')
frame2.pack(anchor=NW)
Label(frame2, text='Status:').pack(side=LEFT)
status1Label=Label(frame2, text='Not Connected', foreground='grey', width=15)
status1Label.pack(side=LEFT, padx=5)
vibBar1=Progressbar(frame2, maximum=1, length=200)
vibBar1.pack(side=LEFT, padx=5)
vibSlider1=Scale(frame2, from_=0, to=1, length=200)
vibSlider1.pack(side=LEFT, padx=5)
rMotorEnable1=Checkbutton(frame2, text='Right Motor Rumble')
rMotorEnable1.pack(side=LEFT, padx=5)
rMotorEnable1.state(['!alternate', 'selected'])
Hovertip(rMotorEnable1,'Some controllers, like the DualShock 3, have a right motor that does not have a rumble gradient. If your controller has a right motor that does not have a rumble gradient, uncheck the box.')
frame3=LabelFrame(root, text='Controller 3')
frame3.pack(anchor=NW)
Label(frame3, text='Status:').pack(side=LEFT)
status2Label=Label(frame3, text='Not Connected', foreground='grey', width=15)
status2Label.pack(side=LEFT, padx=5)
vibBar2=Progressbar(frame3, maximum=1, length=200)
vibBar2.pack(side=LEFT, padx=5)
vibSlider2=Scale(frame3, from_=0, to=1, length=200)
vibSlider2.pack(side=LEFT, padx=5)
rMotorEnable2=Checkbutton(frame3, text='Right Motor Rumble')
rMotorEnable2.pack(side=LEFT, padx=5)
rMotorEnable2.state(['!alternate', 'selected'])
Hovertip(rMotorEnable2,'Some controllers, like the DualShock 3, have a right motor that does not have a rumble gradient. If your controller has a right motor that does not have a rumble gradient, uncheck the box.')
frame4=LabelFrame(root, text='Controller 4')
frame4.pack(anchor=NW)
Label(frame4, text='Status:').pack(side=LEFT)
status3Label=Label(frame4, text='Not Connected', foreground='grey', width=15)
status3Label.pack(side=LEFT, padx=5)
vibBar3=Progressbar(frame4, maximum=1, length=200)
vibBar3.pack(side=LEFT, padx=5)
vibSlider3=Scale(frame4, from_=0, to=1, length=200)
vibSlider3.pack(side=LEFT, padx=5)
rMotorEnable3=Checkbutton(frame4, text='Right Motor Rumble')
rMotorEnable3.pack(side=LEFT, padx=5)
rMotorEnable3.state(['!alternate', 'selected'])
Hovertip(rMotorEnable3,'Some controllers, like the DualShock 3, have a right motor that does not have a rumble gradient. If your controller has a right motor that does not have a rumble gradient, uncheck the box.')
frame5=LabelFrame(root, text='UDP Socket Output')
frame5.pack(anchor=NW)
addrEntry=Entry(frame5)
addrEntry.pack(side=LEFT)
vibBar4=Progressbar(frame5, maximum=1, length=200)
vibBar4.pack(side=LEFT, padx=5)
vibSlider4=Scale(frame5, from_=0, to=1, length=200)
vibSlider4.pack(side=LEFT, padx=5)
startButton=Button(frame5, text='Start', command=start_stop)
startButton.pack(side=LEFT, padx=5)
Hovertip(vibSlider, 'Controller 1 vibration volume')
Hovertip(vibSlider1, 'Controller 2 vibration volume')
Hovertip(vibSlider2, 'Controller 3 vibration volume')
Hovertip(vibSlider3, 'Controller 4 vibration volume')
Hovertip(vibSlider4, 'UDP remote vibration volume')
Hovertip(vibBar, 'Controller 1 vibration meter')
Hovertip(vibBar1, 'Controller 2 vibration meter')
Hovertip(vibBar2, 'Controller 3 vibration meter')
Hovertip(vibBar3, 'Controller 4 vibration meter')
Hovertip(vibBar4, 'UDP remote vibration meter')
Hovertip(addrEntry, 'Enter the IP address of the device running the remote rumble app')
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                stream_callback=audio_callback)
stream.start_stream()
root.mainloop()
