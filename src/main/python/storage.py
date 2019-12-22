from music_pack import MusicPack

class Storage:
  __instance = None

  @staticmethod 
  def getInstance():
    """ Static access method. """
    if Storage.__instance == None:
      Storage()
    return Storage.__instance
  def __init__(self):
    """ Virtually private constructor. """
    if Storage.__instance != None:
      raise Exception("This class is a singleton!")

    Storage.__instance = self

    self.__music_packs = []

  def getMusicPacks(self):
    return self.__music_packs[:]

  def addMusicPack(self, mp):

    if not isinstance(mp, MusicPack):
      raise IOError('no valid music pack')

    self.__music_packs.append(mp)
