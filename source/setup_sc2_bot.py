from sc2 import BotAI

from sc2.units import Units, UnitSelection
import sc2.unit
from sc2.unit import Unit
from sc2.constants import AbilityId, UpgradeId, UnitTypeId
from sc2.constants import PROBE,  ZEALOT, STALKER,COLOSSUS, OBSERVER,IMMORTAL,PHOENIX
from sc2.constants import NEXUS, GATEWAY,PYLON, ASSIMILATOR, CYBERNETICSCORE, ROBOTICSBAY, ROBOTICSFACILITY, FORGE,  STARGATE

from enum import Enum


class Developmentstatus(Enum):
    STARTUP = 1
    RESOURCEGATHERING = 2
    BUILDDEFENSIVE_FORCE = 3
    BUILD_OFFENSIVE_ARMY = 4
    EXPANSION_RESEARCH = 5
    ATTACK = 6
    REBUILD = 7

class DrRoboticus(BotAI):   # the botAi class contains a lot of the methods we want to use
    def __init__(self):
        sc2.BotAI.__init__(self)  #this seems necessary to define the doctor and inherit the parent class methods
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
        for nexus in self.units(NEXUS).ready.noqueue:
            if self.can_afford_feed_unit(PROBE):
                #somehow only build if we need some (16 per nexus
                if (self.units(PROBE).amount / self.units(NEXUS).amount) <16:
                    await self.do(nexus.train(PROBE))
                    print("training probe")

    async def build_pylons(self):
        if self.supply_left < 8 and not self.already_pending(PYLON):
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                if self.can_afford(PYLON):  # method to check that we have enough resources
                    await self.build(PYLON, nexuses.first, 20)
                    # worker = self.select_build_worker(nexuses.first)
                    # if worker is not None:
                    #     if not self.already_pending(PYLON):
                    #         await self.do(worker.build(PYLON, nexuses.first.position, 20)) #check we arent already building

    async def build_ASSYMILATOR(self):
        for nexus in self.units(NEXUS).ready:
            vaspenes = self.state.vespene_geyser.closer_than(15.0,nexus)
            for vaspene in vaspenes:
                if not self.can_afford(ASSIMILATOR):
                    break
                worker = self.select_build_worker(vaspene.position)
                if worker is None:
                    break
                if not self.units(ASSIMILATOR).closer_than(1.0,vaspene).exists:
                    await self.do(worker.build(ASSIMILATOR,vaspene))
                    print("Building Assymilator")

    async def build_gateway(self):
        nexuses = self.units(NEXUS).ready
        if nexuses.exists:
            if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
                if not self.units(GATEWAY).closer_than(30.0, self.units(NEXUS).first).exists:
                    await self.build(GATEWAY, self.units(PYLON).furthest_to(self.units(NEXUS).first), 20)
                    #self.do(worker.build(GATEWAY, homenexus.position))

    async def build_army(self):
        for gateway in self.units(GATEWAY).ready.noqueue:
            if self.can_feed(ZEALOT):
                if self.units(ZEALOT).amount < 10 and self.can_afford(ZEALOT) and not self.units(CYBERNETICSCORE).exists:
                    if not self.units(CYBERNETICSCORE).ready:
                        await self.do(gateway.train(ZEALOT))
                        print("training ZEALOT")
            if self.units(CYBERNETICSCORE).ready:
                if self.can_feed(STALKER) and self.units(STALKER).amount < 25 and self.can_afford(STALKER):
                    await self.do(gateway.train(STALKER))
                    print("training stalker")
        if self.units(ROBOTICSFACILITY).ready:
            for Roboticsfacility in self.units(ROBOTICSFACILITY).ready.noqueue:
                if self.units(ROBOTICSBAY).ready and self.units(CYBERNETICSCORE).ready:
                    if self.can_feed(COLOSSUS) and self.can_afford(COLOSSUS)and self.units(COLOSSUS).amount < 20:
                        await self.do(Roboticsfacility.train(COLOSSUS))
                        print("training COLOSSUS")
                    elif not self.units(CYBERNETICSCORE).ready and self.can_afford_feed_unit(OBSERVER) and self.units(OBSERVER).amount < 2:
                        await self.do(Roboticsfacility.train(OBSERVER))

                elif self.can_feed(IMMORTAL) and self.can_afford(IMMORTAL)and self.units(IMMORTAL).amount < 15:
                        await self.do(Roboticsfacility.train(IMMORTAL))

        if self.units(STARGATE).exists:
            for stargate in self.units(STARGATE).ready.noqueue:
                if self.can_feed(PHOENIX) and self.can_afford(PHOENIX)and self.units(PHOENIX).amount < 5:
                    await self.do(stargate.train(PHOENIX))


    async def build_advanced_structures(self):
        nexuses = self.units(NEXUS).ready
        if nexuses.exists:
            if self.units(GATEWAY).exists and self.units(GATEWAY).ready:
                if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                    if not self.units(CYBERNETICSCORE).exists:
                        await self.build(CYBERNETICSCORE, self.find_next_building_location(), 20)
            if self.units(GATEWAY).exists and self.units(CYBERNETICSCORE).exists and self.units(CYBERNETICSCORE).ready:
                if self.can_afford(ROBOTICSFACILITY) and not self.already_pending(ROBOTICSFACILITY):
                    if not self.units(ROBOTICSFACILITY).amount >= 2:
                        await self.build(ROBOTICSFACILITY, self.find_next_building_location(), 20)
            if self.units(ROBOTICSFACILITY).exists and self.units(CYBERNETICSCORE).exists:
                if self.can_afford(STARGATE) and not self.already_pending(STARGATE):
                    if not self.units(STARGATE).exists:
                        await self.build(STARGATE, self.find_next_building_location(), 20)
            if self.units(ROBOTICSFACILITY).exists and self.units(CYBERNETICSCORE).exists:
                if self.can_afford(ROBOTICSBAY) and not self.already_pending(ROBOTICSBAY):
                    if not self.units(ROBOTICSBAY).exists:
                        await self.build(ROBOTICSBAY, self.find_next_building_location(), 20)
            if not self.units(FORGE).exists and not self.already_pending(FORGE):
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

        most_exposed_nexus = self.units(NEXUS).closest_to(self.enemy_start_locations[0])

        for army_unit in attacking_ground_units:
            nearest_enemies = self.known_enemy_units.sorted_by_distance_to(army_unit)
            #if army_unit.is_idle:
            if nearest_enemies.amount > 0:
                #wait at the most exposed base if nothing is attacking us
                if nearest_enemies.closest_distance_to(most_exposed_nexus) > 250 and not attack_mode_allowed:
                    await self.do(army_unit.move(most_exposed_nexus + 10))
                #choose a target which is closest to you
                elif nearest_enemies.closest_distance_to(most_exposed_nexus) < 250:
                    target = self.choose_target(army_unit)
                    await self.do(army_unit.attack(target))
                if attack_mode_allowed == 1:   #no restrictions on the distance to the target
                    target = self.choose_target(army_unit)
                    await self.do(army_unit.attack(target))
            else: #wait at exposed base
                await self.do(army_unit.move(most_exposed_nexus))

        #reveal some more enemy units if we are advanced enough
        if len(attacking_ground_units) > 20 and self.units(OBSERVER).amount == 2:
            for observer in self.units.of_type(OBSERVER):
                await self.do(observer.move(self.enemy_start_locations[0]))
        #offensive
        #if self.units(COLOSSUS).amount > 15 and len(self.known_enemy_units) > 3:
         #   self.enemy_start_locations()

    #async def research(self):
    #want to do this after a lot of other stuff is setup
    # define some helper functions to clean up the code a bit

    async def research(self):
        if self.units(COLOSSUS).amount > 5:
            if not self.units(FORGE).exists and not self.already_pending(FORGE):
                await self.build(FORGE, self.find_next_building_location(), 20)
            elif self.units(FORGE).ready:
                for forge in self.units(FORGE).idle:
                    if not self.already_pending_upgrade(UpgradeId.PROTOSSGROUNDARMORSLEVEL1)>0:
                        await self.do(forge.research(UpgradeId.PROTOSSGROUNDARMORSLEVEL1))
                    elif not self.already_pending_upgrade(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL1)>0:
                        await self.do(forge.research(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL1))
                    elif not self.already_pending_upgrade(UpgradeId.PROTOSSSHIELDSLEVEL1)>0:
                        await self.do(forge.research(UpgradeId.PROTOSSSHIELDSLEVEL1))
                    elif self.units(UnitTypeId.TWILIGHTCOUNCIL).exists and self.already_pending_upgrade(UpgradeId.PROTOSSGROUNDARMORSLEVEL1)>1:
                        await self.do(forge.research(UpgradeId.PROTOSSGROUNDARMORSLEVEL2))

                #elif not self.units(UnitTypeId.TWILIGHTCOUNCIL).exists:
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
        if self.units(PYLON).exists:
            nextBuildlocation = self.units(PYLON).closest_to(self.enemy_start_locations[0])
        else:
            nextBuildlocation = self.units(NEXUS).first
        return nextBuildlocation


    def choose_target(self, army_unit=Unit) -> Unit:

        nearest_enemies = self.known_enemy_units.sorted_by_distance_to(army_unit)
        if len(nearest_enemies) >= 1:
            for enemy in nearest_enemies:
                if enemy.is_attacking and army_unit.target_in_range(enemy):
                    if army_unit.target_selectable(enemy):
                        target = enemy
                        return target
            return nearest_enemies[0]  #unless someone is attacking, take the closest

        # run_game(maps.get("AbyssalReefLE") ,[
#     Bot(Race.Protoss, DrRoboticus()),
#     Computer(Race.Terran, Difficulty.Easy)
# ], realtime=False)
