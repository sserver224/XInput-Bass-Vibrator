#Copyright (c) 2023-present sserver224.
from tendo import singleton
import sys
try:
    me = singleton.SingleInstance()
except:
    from tkinter import messagebox
    messagebox.showwarning('Warning','Bass Vibrator is already running')
    sys.exit()
import pyaudio
import numpy as np
from tkinter import *
from tkinter.ttk import *
import os
import pygame
import pystray
import ctypes, comtypes
from ctypes import wintypes
from pystray import MenuItem as item
from PIL import Image
from threading import Thread
from idlelib.tooltip import Hovertip
import time
FORMAT = pyaudio.paInt16# audio format
CHANNELS = 2 # mono audio
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
    for controller in root.joysticks.values():
        controller.stop_rumble()
    stream.stop_stream()
    stream.close()
    p.terminate()
    for controller in root.joysticks.values():
        controller.stop_rumble()
    pygame.joystick.quit()
    pygame.quit()
    sys.exit()
import struct
from scipy.signal import butter, lfilter
def audio_callback(in_data, frame_count, time_info, status):
    # Convert raw bytes to numpy array of 16-bit integers
    samples = np.frombuffer(in_data, dtype=np.int16).reshape(-1, 2)
    
    # Apply window function to reduce spectral leakage for each channel
    window = np.hamming(len(samples))
    samples = samples * window[:, np.newaxis]
    
    bass_loudness = ()
    
    for channel in samples.T:  # Transpose to iterate over channels
        # Compute power spectrum using FFT algorithm
        spectrum = np.abs(np.fft.fft(channel)) ** 2

        # Define frequency range of interest
        freq_range = (20, 120)  # Hz

        # Find indices corresponding to frequency range of interest
        f = np.fft.fftfreq(len(channel), 1 / RATE)
        idx = np.logical_and(f >= freq_range[0], f <= freq_range[1])

        # Apply indices to get bass spectrum for the channel
        bass_spectrum = spectrum[idx]

        # Calculate total energy in bass range for the channel
        bass_energy = np.sum(bass_spectrum)

        # Define normalization factor
        max_value = np.iinfo(np.int16).max  # maximum value of 16-bit integer

        # Normalize energy value to range of 0.0 to 1.0 for the channel
        bass_loudness_channel = bass_energy / (max_value * len(bass_spectrum))
        bass_loudness += (bass_loudness_channel,)
    for event in pygame.event.get():
        if event.type == pygame.JOYDEVICEADDED:
            joy = pygame.joystick.Joystick(event.device_index)
            tab=Frame(tabControl)
            root.tabs[joy.get_instance_id()]=tab
            Label(tab, text='Battery:').pack()
            statusLabel=Label(tab, text='Unknown', foreground='grey')
            statusLabel.pack()
            root.statuses[joy.get_instance_id()]=statusLabel
            Label(tab, text='Rumble Channel').pack()
            option=Combobox(tab, state='readonly', values=['Off', 'Left', 'Right', 'Stereo'])
            option.pack()
            checkbox=Checkbutton(tab, text='Disable Right Motor Rumble (Only when channel is set to Left or Right)')
            checkbox.state(['!alternate'])
            root.checkboxes[joy.get_instance_id()]=checkbox
            joy_name=joy.get_name()
            checkbox.pack()
            if joy_name=='Nintendo Switch Pro Controller':
                option.set('Stereo')
                checkbox.state(['disabled'])
                Hovertip(checkbox,'Due to the equal sizes of the haptic actuators and both of them having rumble gradients, right motor rumble is always enabled for Nintendo Switch Pro Controllers.')
            else:
                if joy_name=='PS4 Controller':
                    option.set('Stereo')
                else:
                    option.set('Off')
                Hovertip(checkbox,'Some controllers, like the DualShock 3, have a right motor that does not have a rumble gradient. If your controller has a right motor that does not have a rumble gradient, check the box.')
            root.options[joy.get_instance_id()]=option
            tabControl.add(tab, text=joy.get_name().replace("Controller", "C."))
            root.joysticks[joy.get_instance_id()] = joy
        if event.type == pygame.JOYDEVICEREMOVED:
            tabControl.forget(tuple(root.joysticks.keys()).index(event.instance_id))
            del root.joysticks[event.instance_id]
            del root.statuses[event.instance_id]
            del root.options[event.instance_id]
            del root.tabs[event.instance_id]
    low_bat_count=0
    crit_bat_count=0
    try:
        if (IAudioEndpointVolume.get_default().GetMasterVolumeLevelScalar()>0 and IAudioEndpointVolume.get_default().GetMute()==0):
            sound_on=True
        else:
            sound_on=False
    except Exception as e:
        sound_on=False
    for controller in root.joysticks.values():
        battery=controller.get_power_level()
        instance_id=controller.get_instance_id()
        try:
            if battery=='max':
                root.statuses[instance_id].config(text='Full', foreground='#00ff00')
            elif battery=='full':
                root.statuses[instance_id].config(text='High', foreground='#00ff00')
            elif battery=='medium':
                root.statuses[instance_id].config(text='Medium', foreground='orange')
            elif battery=='low':
                root.statuses[instance_id].config(text='Low', foreground='red')
                low_bat_count+=1
            elif battery=='empty':
                if time.time()%1>=0.5:
                    color='red'
                else:
                    color='grey'
                root.statuses[instance_id].config(text='Critical', foreground=color)
                crit_bat_count+=1
            elif battery=='wired':
                root.statuses[instance_id].config(text='Wired', foreground='#00ff00')
            else:
                root.statuses[instance_id].config(text='Unknown', foreground='grey')
        except:
            pass
        if sound_on:
            if (bass_loudness[0]/1919796895)>=float(noise_gate.get())*0.01:
                left_rumble=min((bass_loudness[0]/1919796895), 1.0)*vibSlider.get()
            else:
                left_rumble=0
            if (bass_loudness[1]/1919796895)>=float(noise_gate.get())*0.01:
                right_rumble=min((bass_loudness[1]/1919796895), 1.0)*vibSlider1.get()
            else:
                right_rumble=0
            vibBar['value']=left_rumble
            vibBar1['value']=right_rumble
            instance_id=controller.get_instance_id()
            if root.options[instance_id].get()=='Stereo':
                controller.rumble(left_rumble, right_rumble, 0)
            elif root.options[instance_id].get()=='Left':
                if root.checkboxes[instance_id].instate(['selected']):
                    controller.rumble(left_rumble, 0, 0)
                else:
                    controller.rumble(left_rumble, left_rumble, 0)
            elif root.options[instance_id].get()=='Right':
                if root.checkboxes[instance_id].instate(['selected']):
                    controller.rumble(right_rumble, 0, 0)
                else:
                    controller.rumble(right_rumble, right_rumble, 0)
        else:
            vibBar['value']=0
            vibBar1['value']=0
            controller.stop_rumble()
    if len(root.joysticks)>0:
        if crit_bat_count>0:
            try:
                controller_count.config(text=str(len(root.joysticks)), foreground=color)
            except:
                controller_count.config(text=str(len(root.joysticks)), foreground='red')
        elif low_bat_count>0:
            controller_count.config(text=str(len(root.joysticks)), foreground='red')
        else:
            controller_count.config(text=str(len(root.joysticks)), foreground='#00ff00')
    else:
        controller_count.config(text='0', foreground='grey')
        vibBar['value']=0
        vibBar1['value']=0
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
        from tkinter import messagebox
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
def disable_rumble_1():
    vibSlider.set(0)
def disable_rumble_2():
    vibSlider1.set(0)
def low_rumble_1():
    vibSlider.set(0.25)
def low_rumble_2():
    vibSlider1.set(0.25)
def med_rumble_1():
    vibSlider.set(0.5)
def med_rumble_2():
    vibSlider1.set(0.5)
def hi_rumble_1():
    vibSlider.set(0.75)
def hi_rumble_2():
    vibSlider1.set(0.75)
def max_rumble_1():
    vibSlider.set(1)
def max_rumble_2():
    vibSlider1.set(1)
def stop_all():
    for controller in root.joysticks.values():
        controller.stop_rumble()
pygame.init()
pygame.joystick.init()
root=Tk()
root.title('Bass Vibrator v0.2 (c) HapticWave Software (Beta)')
LEFT='left'
root.joysticks={}
root.tabs={}
root.rumble_status={}
root.options={}
root.statuses={}
root.checkboxes={}
root.socket_open=False
root.resizable(False, False)
Label(root, text='Bass Vibrator Settings').pack()
root.protocol('WM_DELETE_WINDOW', root.withdraw)
image = Image.open(get_resource_path('controller.ico'))
menu = (item('L Channel Rumble Off', disable_rumble_1), item('L Channel Rumble Low', low_rumble_1), item('L Channel Rumble Moderate', med_rumble_1), item('L Channel Rumble High', hi_rumble_1), item('L Channel Rumble Maximum', max_rumble_1), item('R Channel Rumble Off', disable_rumble_2), item('R Channel Rumble Low', low_rumble_2), item('R Channel Rumble Moderate', med_rumble_2), item('R Channel Rumble High', hi_rumble_2), item('R Channel Rumble Maximum', max_rumble_2), item('Send Rumble OFF to All Controllers', stop_all), item('Restore', root.deiconify), item('Exit', close))
icon = pystray.Icon("name", image, "Bass Vibrator", menu)
Thread(target=icon.run, daemon=True).start()
root.iconbitmap(get_resource_path('controller.ico'))
linkIn=Checkbutton(root, text='Link Intensity Sliders', state=DISABLED)
linkIn.pack()
linkIn.state(['!alternate'])
Hovertip(linkIn,'This has not been implemented yet')
frame4=Frame(root)
frame4.pack()
Label(frame4, text='Gate').pack(side=LEFT)
noise_gate=Spinbox(frame4, from_=0, to_=10, increment=0.1, state='readonly')
noise_gate.pack(side=LEFT, padx=5)
noise_gate.set('1.0')
Label(frame4, text='%').pack(side=LEFT)
stopButton=Button(root, text='Send Rumble OFF to All Controllers', command=stop_all)
stopButton.pack()
frame1=LabelFrame(root, text='Left Channel')
frame1.pack(anchor=NW)
vibBar=Progressbar(frame1, maximum=1, length=200)
vibBar.pack(side=LEFT, padx=5)
vibSlider=Scale(frame1, from_=0, to=1, length=200)
vibSlider.pack(side=LEFT, padx=5)
frame2=LabelFrame(root, text='Right Channel')
frame2.pack(anchor=NW)
vibBar1=Progressbar(frame2, maximum=1, length=200)
vibBar1.pack(side=LEFT, padx=5)
vibSlider1=Scale(frame2, from_=0, to=1, length=200)
vibSlider1.pack(side=LEFT, padx=5)
frame3=Frame(root)
frame3.pack(anchor=NW)
Label(frame3, text='Number of controllers connected:').pack(side=LEFT)
controller_count=Label(frame3, text='0', foreground='grey')
controller_count.pack(side=LEFT, padx=5)
Hovertip(controller_count, 'A red number indicates a low battery in one or more controllers')
Hovertip(vibSlider, 'L Channel vibration volume')
Hovertip(vibSlider1, 'R Channel vibration volume')
Hovertip(noise_gate, r'Minimum bass loudness in % before controllers begin vibrating')
Hovertip(vibBar, 'L Channel vibration meter')
Hovertip(vibBar1, 'R Channel vibration meter')
Hovertip(stopButton, 'Click to stop any stray vibrations')
tabControl=Notebook(root)
tabControl.pack(anchor=NW, expand=True)
stream = p.open(format=FORMAT,
                channels=2,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                stream_callback=audio_callback)
stream.start_stream()
root.mainloop()
