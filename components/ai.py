from combat_functions import avoid_attack, determine_valid_angles, angle_id, calc_modifiers, make_attack_roll, apply_dam, dam_effect_finder, dam_effects, perform_attack, calc_history_modifier
from enums import CombatPhase
from components.fighter import Fighter
from fov_aoc import aoc_check
import global_vars

class CombatAI:
    def __init__ (self, host):
        self.host = host
        self.atk_result = []
        self.atk_success = False
        self.mods = []

    def take_turn(self, entity, entities, combat_phase):
        messages = []
        #Check AOC for targets in case one moved
        entity.fighter.targets = aoc_check(entities, entity)
        
        if len(self.host.targets) == 0:
            combat_phase = CombatPhase.action
            messages.append(entity.name + ' ends ' +  'turn. ')
            self.host.end_turn = True
            return messages, combat_phase

        
        
        curr_target = self.host.targets[0]
        
        #ACTION PHASE
        # See if we have enough AP to attack
        min_ap = self.host.swift + 1

        for wpn in entity.weapons:
            for atk in wpn.attacks:

                cs = entity.determine_combat_stats(wpn, atk)
                b_psi = cs.get('b psi')
                s_psi = cs.get('s psi')
                p_psi = cs.get('p psi')
                t_psi = cs.get('t psi')
                final_ap = cs.get('final ap')
                if final_ap < min_ap: 
                    min_ap = final_ap
                    
        
        #Attack logic begins
        
        if min_ap <= self.host.ap:

            best_score = 0
            best_atk = []
            loc_list = curr_target.fighter.locations
            #Locations to be scored higher because they kill the foe
            critical_locs = {0,1,2,6}

            for wpn in entity.weapons:
                for atk in wpn.attacks:
                    if final_ap <= self.host.ap:
                        for location in loc_list:
                            loc_id = loc_list.index(location)
                            #Skip if location destroyed
                            if not any(location):
                                continue
                            else:
                                for angle_str in determine_valid_angles(loc_id):
                                    #Variable Init
                                    angle = angle_id(angle_str)
                                    dam_score = 0
                                    hit_score = 0
                                    overall_score = 0
                                    cs = entity.determine_combat_stats(wpn, atk, loc_id, angle)
                                    b_psi = cs.get('b psi')
                                    s_psi = cs.get('s psi')
                                    p_psi = cs.get('p psi')
                                    t_psi = cs.get('t psi')
                                    to_hit = cs.get('to hit')
                                    dodge_mod = cs.get('dodge mod')
                                    final_ap = cs.get('final ap')
                                    parry_ap = cs.get('parry ap')
                                    parry_mod = cs.get('parry mod')
                                    dam = (b_psi + s_psi + p_psi + t_psi)
                                    #Attks/rd
                                    atks_rd = self.host.ap / final_ap
                                    #Dam/rd
                                    dam_base = dam * atks_rd
                                    if len(curr_target.fighter.attacker_history) > 0:
                                            history_mod = calc_history_modifier(curr_target, atk, loc_id, angle)
                                            dodge_mod += history_mod
                                            parry_mod += history_mod
                                    #Award points based on dam mult in respect to remaining hits in hit loc
                                    for layer in location:
                                        if layer > 0:
                                            dam_score += dam_base / layer
                                    #Award points based on ability to hit
                                    best_avoid = max(dodge_mod+curr_target.fighter.dodge, parry_mod+curr_target.fighter.deflect)
                                    if to_hit == best_avoid:
                                        hit_score = 1
                                    else:    
                                        hit_score = (100/(to_hit - best_avoid))
                                    overall_score = dam_score * hit_score   
                                    for loc in critical_locs:
                                        if loc_id == loc: overall_score *= 1.5
                                    if overall_score > best_score:
                                        best_atk = [wpn, atk, loc_id, angle]
                                        best_score = overall_score
            #Clear the list
            self.host.combat_choices.clear()
            #Add new choices to list
            for i in best_atk:
                self.host.combat_choices.append(i)

            #Commit attack
            
            cs = entity.determine_combat_stats(best_atk[0], best_atk[1], best_atk[2], best_atk[3])
            tot_er = cs.get('total er')
            b_psi = cs.get('b psi')
            s_psi = cs.get('s psi')
            p_psi = cs.get('p psi')
            t_psi = cs.get('t psi')
            to_hit = cs.get('to hit')
            to_parry = cs.get('to parry')
            dodge_mod = cs.get('dodge mod')
            final_ap = cs.get('final ap')
            parry_ap = cs.get('parry ap')
            parry_mod = cs.get('parry mod')
            
            if len(curr_target.fighter.attacker_history) > 0:
                history_mod = calc_history_modifier(curr_target, self.host.combat_choices[1], self.host.combat_choices[2], self.host.combat_choices[3])
                dodge_mod += history_mod
                parry_mod += history_mod
            messages, combat_phase = perform_attack(entity, entities, to_hit, curr_target, cs, combat_phase)
        else:
            combat_phase = CombatPhase.action
            messages.append(entity.name + ' ends ' +  'turn. ')
            self.host.end_turn = True

        return messages, combat_phase