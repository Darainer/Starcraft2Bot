"""Map-based expansion classification shared by scouting and target assessment."""


def is_expansion(bot, point):
    return bool(bot.enemy_start_locations) and all(
        point.distance_to(start) > 12 for start in bot.enemy_start_locations
    )


def expansion_sites(bot):
    homes = [bot.start_location, *(base.position for base in bot.townhalls.ready)]
    return [
        site
        for site in bot.expansion_locations_list
        if is_expansion(bot, site) and all(site.distance_to(home) > 12 for home in homes)
    ]
