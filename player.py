class Player:
    """
    TODO implement utility classes for gear etc.

    A combination of setup (weapon+mods+gear+mods+talents) and traits (accuracy, bodyshot%, headshot%)
    """
    def __init__(self, name, weapon, gear, skills, talents, traits):
        self.name = name
        self.weapon = weapon
        self.gear = gear
        self.skills = skills
        self.talents = talents
        self.traits = traits
        self.ongoing_action = None
        self.max_hp = 10000
        self.hp = self.max_hp
        self.medkit = {
            "num_remaining": 5,
        }
        self.cooldowns = {}
        self.action_time_extended = 0

    def use_medkit(self, time_window):
        """
        Heals, reduces num of medkits, applies medkit cooldown, and reduces the time window.
        If time window isn't enough for the action, action will continue in self.ongoing_action.

        > HP goes up, and cooldown activates, in the beginning of activation (before the animation is over)
        > Animation (preventing further actions) takes approximately 1'000 ms
        > Cooldown time is approximately 13'000 ms

        :param time_window: Time given for the action, if not enough the action will remain as an ongoing_action
        :return: time remaining with respect to time_window after action completed
        """
        medkit_animation_time = 1000  # ms
        medkit_cooldown_time = 13000  # ms
        print("{} entering medkit animation".format(self.name))

        # Heal
        if self.hp < 0.60*self.max_hp:
            self.hp += int(round(0.4*self.max_hp))
        else:
            self.hp = self.max_hp
        print("{} healed to {}% HP using one medkit".format(self.name, round(self.hp/self.max_hp, 2)*100))

        # Reduce number and apply cooldown
        self.medkit["num_remaining"] -= 1
        self.cooldowns["medkit"] = medkit_cooldown_time
        print("{} has {} medkits remaining".format(self.name, self.medkit["num_remaining"]))

        # Animation lockout (persist in ongoing_action)
        time_window = time_window - medkit_animation_time
        if time_window < 0:
            def ongoing_medkit_use(action_remaining):
                def continue_medkit_use(time_remaining):
                    time_remaining = time_remaining - action_remaining
                    if time_remaining < 0:
                        overtime_remaining = time_remaining * -1
                        self.ongoing_action = ongoing_medkit_use(overtime_remaining)
                        print("{} still {} ms in medkit animation".format(self.name, overtime_remaining))
                        return 0
                    else:
                        self.ongoing_action = None
                        print("{} out of medkit animation with {} ms remaining".format(self.name, time_remaining))
                        return time_remaining
                return continue_medkit_use
            action_overtime_remaining = time_window * -1
            self.ongoing_action = ongoing_medkit_use(action_overtime_remaining)
            return 0
        else:
            return time_window

    def shoot_at(self, target):
        """
        TODO implement real calculations

        :param target: The target that is shot at, used for calculating dealt damage.
        :return: Tuple, containing damage dealt as an integer, and time extended (or reduced) by the last shot.
        """
        return 100, 0

    def fight(self, target, time_window):
        """
        :param target: The target that is acted upon (e.g. shot) against, used for calculating dealt damage.
        :param time_window: Time given to act (e.g. shoot) until calculation is performed.
        :return: Damage dealt as an integer.
        """
        damage_dealt = 0

        # Apply time extension to time window (either reducing or increasing it)
        time_window -= self.action_time_extended
        self.action_time_extended = 0
        total_actionable_time = time_window  # Persist the total time_window for cooldown calculations

        # Exploding a Support Station (35% [over]heal) is possible in parallel with any action
        if self.hp < 0.65*self.max_hp and 'supportstation' in self.skills and self.skills['supportstation'].is_active:
            self.skills['supportstation'].deactivate()  # Heal and cd

        # Continue (if) any ongoing action
        if self.ongoing_action is not None:
            time_window = self.ongoing_action(time_window)

        # Perform time consuming actions in order healing > buffs > shoot
        while time_window > 0:
            if self.hp < 0.60*self.max_hp and self.medkit['num_remaining'] > 0 and "medkit" not in self.cooldowns:
                time_window = self.use_medkit(time_window)  # May not finish, and be continued as an ongoing_action
            # else if =gothru buff skills=
            else:
                damage_dealt, time_extended = self.shoot_at(target)
                self.action_time_extended = time_extended
                time_window = 0

        # Reduce cooldowns by the total actionable time
        for k in list(self.cooldowns.keys()):
            self.cooldowns[k] -= total_actionable_time
            if self.cooldowns[k] <= 0:
                del self.cooldowns[k]
                print("{} has {} cooldown over".format(self.name, k))

        return damage_dealt

    def take_dmg(self, amount):
        self.hp = int(round(self.hp - amount))
        print("{} received {} damage (resulting in {}/{}HP)".format(self.name, amount, self.hp, self.max_hp))
