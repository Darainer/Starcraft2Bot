
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer,PlayerType
import setup_sc2_bot
from setup_sc2_bot import DrRoboticus


run_game(maps.get("AbyssalReefLE") ,
  [Bot(Race.Protoss, DrRoboticus())], realtime=False)