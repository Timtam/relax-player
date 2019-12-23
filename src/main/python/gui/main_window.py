import datetime
import os
import os.path

from Bass4Py.BASS import BASS
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QComboBox, QLabel, QSlider
from config import MUSIC_PACKS_FOLDER
from music_pack import MusicPack, MusicPackException
from storage import Storage
from weather import getLocation, getCurrentWeatherState

class MainWindow(QWidget):

  def __init__(self, application_context):
    QWidget.__init__(self)

    self.application_context = application_context
    self.current_pack = {
      'index': 0, # index in combo box
      'obj': None, # pack object
    }
    self.location = None
    self.setWindowTitle('RelaxPlayer')

    self.layout = QHBoxLayout()

    self.pack_selector_label = QLabel('Select music pack', self)
    self.layout.addWidget(self.pack_selector_label)

    self.pack_selector = QComboBox(self)
    self.pack_selector.setEditable(False)
    self.pack_selector.activated.connect(self.changeMusicPack)
    self.layout.addWidget(self.pack_selector)
    self.pack_selector_label.setBuddy(self.pack_selector)

    self.volume_control_label = QLabel('Volume', self)
    self.layout.addWidget(self.volume_control_label)
    
    self.volume_control = QSlider(self)
    self.volume_control.setMinimum(0)
    self.volume_control.setMaximum(100)
    self.volume_control.setSingleStep(1)
    self.volume_control.setPageStep(10)
    self.volume_control.setValue(75)
    self.volume_control.valueChanged.connect(self.volumeChanged)
    self.layout.addWidget(self.volume_control)
    self.volume_control_label.setBuddy(self.volume_control)

    self.setLayout(self.layout)

    initialization_timer = QTimer(self)
    initialization_timer.setSingleShot(True)
    initialization_timer.timeout.connect(self.initialize)
    initialization_timer.start(100)
  
    self.update_music_pack_timer = QTimer(self)
    self.update_music_pack_timer.timeout.connect(self.updateMusicPack)
    self.update_music_pack_timer.start(1000)

    self.update_weather_information_timer = QTimer(self)
    self.update_weather_information_timer.timeout.connect(self.updateWeatherInformation)
    self.update_weather_information_timer.start(6000)

  def initialize(self):

    bass = BASS()
    
    device = bass.GetOutputDevice(-1)
    device.Init(44100, 0, -1)

    self.indexMusicPacks()

  def indexMusicPacks(self):

    self.pack_selector.addItem('(No music pack)')

    resource_folders = self.application_context._resource_locator._dirs
    store = Storage.getInstance()

    for r in resource_folders:

      packs_dir = os.path.join(r, MUSIC_PACKS_FOLDER)

      if not os.path.exists(packs_dir) or not os.path.isdir(packs_dir):
        continue
      
      packs = os.listdir(packs_dir)
      
      for p in packs:
        if not os.path.isdir(os.path.join(packs_dir, p)):
          continue

        try:
          pack = MusicPack(p, packs_dir)
          store.addMusicPack(pack)
          self.pack_selector.addItem(p)
        except MusicPackException as e:
          print(str(e))

  def changeMusicPack(self, *args, **kwargs):
    index = self.pack_selector.currentIndex()
    self.setMusicPack(index)
  
  # index is combo box index
  def setMusicPack(self, index):
    if self.pack_selector.currentIndex() != index:
      self.pack_selector.setCurrentIndex(index)

    self.current_pack['index'] = index
    
    if self.current_pack['obj'] is not None:
      self.current_pack['obj'].stop()

    if index > 0:
      store = Storage.getInstance()
      
      packs = store.getMusicPacks()
      
      pack = packs[index - 1]
      self.current_pack['obj'] = pack

      pack.play()
      pack.setVolume(self.volume_control.value())
    else:
      self.current_pack['obj'] = None

  def updateMusicPack(self):
    if self.current_pack['obj'] is not None:
      self.current_pack['obj'].setHour(datetime.datetime.now().hour)

  def volumeChanged(self, *args, **kwargs):
    volume = self.volume_control.value()
    
    if self.current_pack['obj'] is not None:
      self.current_pack['obj'].setVolume(volume)

  def updateWeatherInformation(self):
    
    if self.location is None:
      self.location = getLocation()

    if self.location is not None:
      getCurrentWeatherState(*self.location)
