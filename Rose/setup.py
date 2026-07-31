from setuptools import setup

APP = ['gui.py']
OPTIONS = {
    'argv_emulation': False,
    'packages': [
        'customtkinter', 'PIL', 'sounddevice', '_sounddevice_data',
        'soundfile', '_soundfile_data', 'pyttsx3',
        'core', 'plugins', 'commands', 'ai', 'vision',
    ],
    'includes': ['tkinter', 'pyttsx3.drivers', 'pyttsx3.drivers.nsss'],
    'excludes': ['PyInstaller', 'py2app'],
    'plist': {
        'CFBundleName': 'Rose',
        'CFBundleDisplayName': 'Rose',
        'CFBundleIdentifier': 'com.vincenttrinh.rose',
        'CFBundleVersion': '1.0.0',
        'NSMicrophoneUsageDescription': 'Rose needs microphone access to hear your voice commands.',
        'NSAppleEventsUsageDescription': 'Rose needs automation access to control apps like Calendar, Messages, and Contacts.',
    },
}

DATA_FILES = [
    ('config', ['config/settings.json']),
    ('default_config', ['config/apps.json', 'config/search_sites.json']),
]

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)