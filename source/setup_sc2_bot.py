from enum import Enum

from sc2.bot_ai import BotAI
from sc2.units import Units
import sc2.unit
from sc2.unit import Unit
from sc2.constants import AbilityId, UpgradeId, UnitTypeId

PROBE = UnitTypeId.PROBE
ZEALOT = UnitTypeId.ZEALOT
STALKER = UnitTypeId.STALKER
COLOSSUS = UnitTypeId.COLOSSUS
OBSERVER = UnitTypeId.OBSERVER
IMMORTAL = UnitTypeId.IMMORTAL
PHOENIX = UnitTypeId.PHOENIX
NEXUS = UnitTypeId.NEXUS
GATEWAY = UnitTypeId.GATEWAY
PYLON = UnitTypeId.PYLON
ASSIMILATOR = UnitTypeId.ASSIMILATOR
CYBERNETICSCORE = UnitTypeId.CYBERNETICSCORE
ROBOTICSBAY = UnitTypeId.ROBOTICSBAY
ROBOTICSFACILITY = UnitTypeId.ROBOTICSFACILITY
FORGE = UnitTypeId.FORGE
STARGATE = UnitTypeId.STARGATE




class Developmentstatus(Enum):
    STARTUP = 1
    RESOURCEGATHERING = 2
    BUILDDEFENSIVE_FORCE = 3
    BUILD_OFFENSIVE_ARMY = 4
    EXPANSION_RESEARCH = 5
    ATTACK = 6
    REBUILD = 7


# this method got deleted from the new package. would be better to have it in Unit, but i dont want to change the package
def target_selectable(myUnit: Unit, target: Unit) -> bool:
    if myUnit.can_attack_air and target.is_flying:
        return True
    elif myUnit.can_attack_ground and not target.is_flying:
        return True
    else:
        return False


class DrRoboticus(BotAI):   # the botAi class contains a lot of the methods we want to use
    def __init__(self):
        sc2.bot_ai.BotAI.__init__(self)  #this seems necessary to define the doctor and inherit the parent class methods
        self.opponent_id: int = None
        self.development_status = 1
        self.last_expansion_time = 0
        self.TIME_STARTUP = 60
        self.TIME_BUILDUP = 500
        self.time_for_defences = 1230

    async def on_step(self, iteration):  # sp we basically run all these when our bot is called
        #what to do every step

        await self.checkdevelopmentStatus()
        await self.distribute_workers()
        await self.build_workers()
        await self.build_ASSYMILATOR()
        await self.build_pylons()
        await self.build_gateway()
        await self.build_army()
        await self.build_advanced_structures()
        await self.command_army()
        await self.expand()
        await self.research()

    async def checkdevelopmentStatus(self):
        if (self.time > self.TIME_STARTUP) & (self.time < self.TIME_BUILDUP):
            self.development_status = 2

    async def expand(self):
        ok_expand_rebuild = False
        enemy_approaching = False
        for nexus in self.units(NEXUS):
            if len(self.known_enemy_units.closer_than(20, nexus)) > 0:
                enemy_approaching = True

        if not enemy_approaching and self.can_afford(NEXUS) and not self.already_pending(NEXUS):
            ok_expand_rebuild = True

        if ok_expand_rebuild:
            if self.units(NEXUS).amount <= 2:
                await self.expand_now()
                print("Expanding")

            if self.units(NEXUS).amount == 2 and self.units(COLOSSUS).amount >= 15:
                await self.expand_now()
                print("Expanding")


    async def build_workers(self):
        for nexus in self.structures(NEXUS).ready.idle:
            if self.can_afford_feed_unit(PROBE):
                #somehow only build if we need some (16 per nexus
                if (self.units(PROBE).amount / self.structures(NEXUS).amount) <16:
                    self.do(nexus.train(PROBE))
                    print("training probe")

    async def build_pylons(self):
        if self.supply_left < 8 and not self.already_pending(PYLON):
            nexuses = self.structures(NEXUS).ready
            if nexuses.exists:
                if self.can_afford(PYLON):  # method to check that we have enough resources
                    await self.build(PYLON, nexuses.first, 20)
                    # worker = self.select_build_worker(nexuses.first)
                    # if worker is not None:
                    #     if not self.already_pending(PYLON):
                    #         self.do(worker.build(PYLON, nexuses.first.position, 20)) #check we arent already building

    async def build_ASSYMILATOR(self):
        for nexus in self.structures(NEXUS).ready:
            vaspenes = self.vespene_geyser.closer_than(15.0, nexus) 
            for vaspene in vaspenes:
                if self.gas_buildings.closer_than(1.0, vaspene.position):
                    break
                if self.already_pending(ASSIMILATOR):
                    break
                if not self.can_afford(ASSIMILATOR):
                    break
                worker = self.select_build_worker(vaspene.position)
                if worker is None:
                    break
                if not self.structures(ASSIMILATOR).closer_than(1.0,vaspene).exists:
                    self.do(worker.build(ASSIMILATOR,vaspene))
                    print("Building Assymilator")

    async def build_gateway(self):
        nexuses = self.structures(NEXUS).ready
        if nexuses.exists:
            if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
                if not self.structures(GATEWAY).closer_than(30.0, self.structures(NEXUS).first).exists:
                    self.build(GATEWAY, self.structures(PYLON).furthest_to(self.structures(NEXUS).first), 20)
                    # self.do(worker.build(GATEWAY, homenexus.position))

    async def build_army(self):
        for gateway in self.structures(GATEWAY).ready.idle:
            if self.can_feed(ZEALOT):
                if self.units(ZEALOT).amount < 10 and self.can_afford(ZEALOT) and not self.structures(CYBERNETICSCORE).exists:
                    if not self.structures(CYBERNETICSCORE).ready:
                        self.do(gateway.train(ZEALOT))
                        print("training ZEALOT")
            if self.structures(CYBERNETICSCORE).ready:
                if self.can_feed(STALKER) and self.units(STALKER).amount < 25 and self.can_afford(STALKER):
                    self.do(gateway.train(STALKER))
                    print("training stalker")
        if self.structures(ROBOTICSFACILITY).ready:
            for Roboticsfacility in self.structures(ROBOTICSFACILITY).ready.idle:
                if self.units(ROBOTICSBAY).ready and self.structures(CYBERNETICSCORE).ready:
                    if self.can_feed(COLOSSUS) and self.can_afford(COLOSSUS)and self.units(COLOSSUS).amount < 20:
                        self.do(Roboticsfacility.train(COLOSSUS))
                        print("training COLOSSUS")
                    elif not self.structures(CYBERNETICSCORE).ready and self.can_afford_feed_unit(OBSERVER) and self.units(OBSERVER).amount < 2:
                        self.do(Roboticsfacility.train(OBSERVER))

                elif self.can_feed(IMMORTAL) and self.can_afford(IMMORTAL)and self.units(IMMORTAL).amount < 15:
                    self.do(Roboticsfacility.train(IMMORTAL))

        if self.units(STARGATE).exists:
            for stargate in self.units(STARGATE).ready.idle:
                if self.can_feed(PHOENIX) and self.can_afford(PHOENIX)and self.units(PHOENIX).amount < 5:
                    self.do(stargate.train(PHOENIX))


    async def build_advanced_structures(self):
        nexuses = self.structures(NEXUS).ready
        if nexuses.exists:
            if self.structures(GATEWAY).exists and self.structures(GATEWAY).ready:
                if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                    if not self.structures(CYBERNETICSCORE).exists:
                        await self.build(CYBERNETICSCORE, self.find_next_building_location(), 20)
            if self.structures(GATEWAY).exists and self.structures(CYBERNETICSCORE).exists and self.structures(CYBERNETICSCORE).ready:
                if self.can_afford(ROBOTICSFACILITY) and not self.already_pending(ROBOTICSFACILITY):
                    if not self.structures(ROBOTICSFACILITY).amount >= 2:
                        await self.build(ROBOTICSFACILITY, self.find_next_building_location(), 20)
            if self.structures(ROBOTICSFACILITY).exists and self.structures(CYBERNETICSCORE).exists:
                if self.can_afford(STARGATE) and not self.already_pending(STARGATE):
                    if not self.structures(STARGATE).exists:
                        await self.build(STARGATE, self.find_next_building_location(), 20)
            if self.structures(ROBOTICSFACILITY).exists and self.structures(CYBERNETICSCORE).exists:
                if self.can_afford(ROBOTICSBAY) and not self.already_pending(ROBOTICSBAY):
                    if not self.units(ROBOTICSBAY).exists:
                        await self.build(ROBOTICSBAY, self.find_next_building_location(), 20)
            if not self.structures(FORGE).exists and not self.already_pending(FORGE):
                await self.build(FORGE, self.find_next_building_location(), 20)


    async def simple_command_army(self):
        print('alternative')
        #attack closest unit to you



    async def command_army(self):
        attacking_unit_types = [PHOENIX, COLOSSUS, IMMORTAL, STALKER, ZEALOT]
        flying_units = self.units.of_type(PHOENIX)
        attacking_ground_units = self.units.of_type(attacking_unit_types)
        if attacking_ground_units.amount < 30:
            attack_mode_allowed = False
        else:
            attack_mode_allowed = True

        most_exposed_nexus = self.structures(NEXUS).closest_to(self.enemy_start_locations[0])

        for army_unit in attacking_ground_units:
            nearest_enemies = self.enemy_units.sorted_by_distance_to(army_unit)
            #if army_unit.is_idle:
            if nearest_enemies.amount > 0:
                #wait at the most exposed base if nothing is attacking us
                if nearest_enemies.closest_distance_to(most_exposed_nexus) > 250 and not attack_mode_allowed:
                    self.do(army_unit.move(most_exposed_nexus + 10))
                #choose a target which is closest to you
                elif nearest_enemies.closest_distance_to(most_exposed_nexus) < 250:
                    target = self.choose_target(army_unit)
                    self.do(army_unit.attack(target))
                if attack_mode_allowed == 1:   #no restrictions on the distance to the target
                    target = self.choose_target(army_unit)
                    self.do(army_unit.attack(target))
            else: #wait at exposed base
                self.do(army_unit.move(most_exposed_nexus))

        #reveal some more enemy units if we are advanced enough
        if len(attacking_ground_units) > 20 and self.units(OBSERVER).amount == 2:
            for observer in self.units.of_type(OBSERVER):
                self.do(observer.move(self.enemy_start_locations[0]))
        #offensive
        #if self.units(COLOSSUS).amount > 15 and len(self.known_enemy_units) > 3:
         #   self.enemy_start_locations()

    #async def research(self):
    #want to do this after a lot of other stuff is setup
    # define some helper functions to clean up the code a bit

    async def research(self):
        if self.units(COLOSSUS).amount > 5:
            if not self.structures(FORGE).exists and not self.already_pending(FORGE):
                await self.build(FORGE, self.find_next_building_location(), 20)
            elif self.structures(FORGE).ready:
                for forge in self.structures(FORGE).idle:
                    if not self.already_pending_upgrade(UpgradeId.PROTOSSGROUNDARMORSLEVEL1)>0:
                        self.do(forge.research(UpgradeId.PROTOSSGROUNDARMORSLEVEL1))
                    elif not self.already_pending_upgrade(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL1)>0:
                        self.do(forge.research(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL1))
                    elif not self.already_pending_upgrade(UpgradeId.PROTOSSSHIELDSLEVEL1)>0:
                        self.do(forge.research(UpgradeId.PROTOSSSHIELDSLEVEL1))
                    elif self.structures(UnitTypeId.TWILIGHTCOUNCIL).exists and self.already_pending_upgrade(UpgradeId.PROTOSSGROUNDARMORSLEVEL1)>1:
                        self.do(forge.research(UpgradeId.PROTOSSGROUNDARMORSLEVEL2))

                # elif not self.units(UnitTypeId.TWILIGHTCOUNCIL).exists:
                  #  await self.build(TWILIGHTCOUNCIL, self.find_next_building_location(), 20)



    def can_afford_feed_unit(self, unit_enum):
        if self.can_feed(unit_enum) and self.can_afford(unit_enum):
            return 1
        else:
            return 0

    def get_all_army_units(self):
        attacking_unit_types = list[PHOENIX, COLOSSUS, IMMORTAL, STALKER, ZEALOT]
        my_units =  self.units.not_structure   #only want the army units to attack
        attacking_units = my_units.of_type(attacking_unit_types)
        return attacking_units

    def find_next_building_location(self):
        if self.structures(PYLON).exists:
            nextBuildlocation = self.structures(PYLON).closest_to(self.enemy_start_locations[0])
        else:
            nextBuildlocation = self.structures(NEXUS).first
        return nextBuildlocation


    def choose_target(self, army_unit=Unit) -> Unit:

        nearest_enemies = self.enemy_units.sorted_by_distance_to(army_unit)
        if len(nearest_enemies) >= 1:
            for enemy in nearest_enemies:
                if enemy.is_attacking and army_unit.target_in_range(enemy):
                    if target_selectable(army_unit, enemy):
                        target = enemy
                        return target
            return nearest_enemies[0]  #unless someone is attacking, take the closest

        # run_game(maps.get("AbyssalReefLE") ,[
#     Bot(Race.Protoss, DrRoboticus()),
#     Computer(Race.Terran, Difficulty.Easy)
# ], realtime=False)
