import os
import os.path

from Bass4Py.BASS import BASS
from Bass4Py.constants import STREAM
from Bass4Py.BASS.syncs import Slide

from weather import WEATHER_STATE_CLEAR, WEATHER_STATE_RAIN, WEATHER_STATE_SNOW

STATE_STOPPED = 0
STATE_PLAYING = 1
STATE_FADING = 2

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
    self.__tracks = {
      WEATHER_STATE_CLEAR: dict(),
      WEATHER_STATE_RAIN: dict(),
      WEATHER_STATE_SNOW: dict(),
    }
    self.__weather_state = WEATHER_STATE_CLEAR
    self.__state = STATE_STOPPED
    self.__sync = None

    self._load_pack()

  def _load_subpack(self, state):

    indicator = None
    
    if state == WEATHER_STATE_CLEAR:
      indicator = 'clear'
    elif state == WEATHER_STATE_RAIN:
      indicator = 'rain'
    elif state == WEATHER_STATE_SNOW:
      indicator = 'snow'
    
    if indicator is None:
      raise MusicPackException('invalid weather state: {state}'.format(state = state))

    state_dir = os.path.join(self.getDirectory(), indicator)

    if not os.path.exists(state_dir) or not os.path.isdir(state_dir):
      return

    am_dir = os.path.join(state_dir, 'am')
    pm_dir = os.path.join(state_dir, 'pm')

    if os.path.exists(am_dir) and os.path.isdir(am_dir):

      am_tracks = os.listdir(am_dir)

      for t in am_tracks:
        file, ext = os.path.splitext(t)

        i = int(file)
      
        if i == 12:
          i = 0
      
        self.__tracks[state][i] = os.path.join(am_dir, t)
      
    if os.path.exists(pm_dir) and os.path.isdir(pm_dir):

      pm_tracks = os.listdir(pm_dir)

      for t in pm_tracks:
        file, ext = os.path.splitext(t)

        i = int(file)
      
        if i != 12:
          i += 12
      
        self.__tracks[state][i] = os.path.join(pm_dir, t)

  def _load_pack(self):

    if not os.path.exists(self.getDirectory()) or not os.path.isdir(self.getDirectory()):
      raise MusicPackException('path doesn\'t exist or is no directory')

    self._load_subpack(WEATHER_STATE_CLEAR)
    self._load_subpack(WEATHER_STATE_RAIN)
    self._load_subpack(WEATHER_STATE_SNOW)

    if (len(self.__tracks[WEATHER_STATE_CLEAR]) + len(self.__tracks[WEATHER_STATE_RAIN]) + len(self.__tracks[WEATHER_STATE_SNOW])) == 0:
      raise MusicPackException('no tracks found for music pack {name}'.format(name = self.__name))

  def _get_track(self, hour = None, state = None):
  
    if hour is None:
      hour = self.__current_track['hour']
      
    if state is None:
      state = self.__weather_state

    if not state in self.__tracks:
      raise MusicPackException('unknown weather state')
    
    track = self.__tracks[state].get(hour, None)
    
    if not track and state != WEATHER_STATE_CLEAR:
      track = self.__tracks[WEATHER_STATE_CLEAR].get(hour, None)
    
    return track

  def getDirectory(self):
    return os.path.join(self.__parent_dir, self.__name)

  def play(self):
    if self.__state != STATE_STOPPED:
      return
    
    self.__state = STATE_PLAYING

    if self.__device is None:
      bass = BASS()
      self.__device = bass.GetOutputDevice(-1)
    
    if self.__current_track['hour'] >= 0:
      hour = self.__current_track['hour']
      
      self.setHour(-1)
      
      self.setHour(hour)

  def stop(self, stream_only = False):
    if self.__current_track['obj'] is not None:
      self.__current_track['obj'].Stop()
      self.__current_track['obj'].Free()
      self.__current_track['obj'] = None
      self.__sync = None

    if not stream_only:
      self.__current_track['hour'] = -1
      self.__state = STATE_STOPPED
      self.__weather_state = WEATHER_STATE_CLEAR

  def _set_track(self, track):

    if track and not self.__current_track['obj'] is None and self.__current_track['obj'].Name == track:
      return

    if track:

      def setNewTrack(*args, **kwargs):
        self.stop(True)

        self.__current_track['obj'] = self.__device.CreateStreamFromFile(track, STREAM.LOOP)
        self.__current_track['obj'].Volume.Set(self.__current_track['volume']/100)
        self.__current_track['obj'].Play(True)
        self.__state = STATE_PLAYING
        self.__sync = None

      if self.__current_track['obj'] is not None:
        sync = Slide()
        sync.Onetime = True
        sync.Callback = setNewTrack
        self.__current_track['obj'].SetSync(sync)
        self.__sync = sync
        
        self.__state = STATE_FADING
        self.__current_track['obj'].Volume.Slide(0, 2000)

      else:
        setNewTrack()

    else:
      self.stop()

  def setHour(self, hour):

    if self.__current_track['hour'] == hour:
      return
    
    self.__current_track['hour'] = hour
    
    if hour == -1:
      self.stop()
      return

    track = self._get_track(hour, self.__weather_state)

    self._set_track(track)

  def setVolume(self, volume):
  
    self.__current_track['volume'] = volume
    
    if self.__state == STATE_FADING:
      return

    if self.__current_track['obj'] is not None:
      self.__current_track['obj'].Volume.Set(volume/100)

  def setWeatherState(self, state):
  
    if state == self.__weather_state:
      return

    if state not in self.__tracks:
      raise MusicPackException('invalid weather state')
    
    self.__weather_state = state
    
    if not self.__current_track['obj'] is None:

      track = self._get_track()
    
      self._set_track(track)