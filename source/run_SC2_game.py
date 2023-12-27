
from sc2 import maps
from sc2.player import Bot, Computer
from sc2.main import run_game
from sc2.data import Race, Difficulty
# from sc2.bot_ai import BotAI
from setup_sc2_bot import DrRoboticus
from ThreeBaseVoidRay import ThreebaseVoidrayBot

run_game(
  maps.get("AbyssalReefLE"),
  [Bot(Race.Protoss, DrRoboticus()),
  Computer(Race.Protoss, Difficulty.Hard)],
  realtime=False
)
