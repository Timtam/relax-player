import os
import os.path

from Bass4Py.BASS import BASS
from Bass4Py.constants import STREAM

class MusicPackException(Exception):
  pass

class MusicPack:

  def __init__(self, name, parent_dir):
    self.__name = name
    self.__parent_dir = parent_dir
    self.__current_track = {
      'hour': -1,
      'obj': None,
      'volume': 100,
    }
    self.__device = None
    self.__tracks = dict()
    self.__playing = False

    self._load_pack()

  def _load_pack(self):

    if not os.path.exists(self.getDirectory()) or not os.path.isdir(self.getDirectory()):
      raise MusicPackException('path doesn\'t exist or is no directory')

    am_dir = os.path.join(self.getDirectory(), 'am')
    pm_dir = os.path.join(self.getDirectory(), 'pm')

    if not os.path.exists(am_dir) or not os.path.isdir(am_dir):
      raise MusicPackException('no am folder found within music pack')

    if not os.path.exists(pm_dir) or not os.path.isdir(pm_dir):
      raise MusicPackException('no pm folder found within music pack')

    am_tracks = os.listdir(am_dir)

    for t in am_tracks:
      file, ext = os.path.splitext(t)

      i = int(file)
      
      if i == 12:
        i = 0
      
      self.__tracks[i] = os.path.join(am_dir, t)
      
    pm_tracks = os.listdir(pm_dir)

    for t in pm_tracks:
      file, ext = os.path.splitext(t)

      i = int(file)
      
      if i != 12:
        i += 12
      
      self.__tracks[i] = os.path.join(pm_dir, t)

  def getDirectory(self):
    return os.path.join(self.__parent_dir, self.__name)

  def play(self):
    if self.__playing:
      return
    
    self.__playing = True

    if self.__device is None:
      bass = BASS()
      self.__device = bass.GetOutputDevice(-1)
    
    if self.__current_track['hour'] >= 0:
      hour = self.__current_track['hour']
      
      if self.__current_track['obj'] is not None:
        self.__current_track['obj'].Stop()
        self.__current_track['obj'] = None
      
      self.__current_track['hour'] = -1
      
      self.setHour(hour)

  def stop(self):
    self.__current_track['hour'] = -1
    
    if self.__current_track['obj'] is not None:
      self.__current_track['obj'].Stop()
      self.__current_track['obj'] = None

  def setHour(self, hour):

    if self.__current_track['hour'] == hour:
      return
    
    self.__current_track['hour'] = hour
    
    if self.__current_track['obj'] is not None:
      self.__current_track['obj'].Stop()
      self.__current_track['obj'].Free()
      self.__current_track['obj'] = None
    
    track = self.__tracks.get(hour, None)

    if track:
      self.__current_track['obj'] = self.__device.CreateStreamFromFile(track, STREAM.LOOP)
      self.__current_track['obj'].Volume.Set(self.__current_track['volume']/100)
      self.__current_track['obj'].Play(True)

  def setVolume(self, volume):
  
    self.__current_track['volume'] = volume
    
    if self.__current_track['obj'] is not None:
      self.__current_track['obj'].Volume.Set(volume/100)
