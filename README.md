# Crimson Sand

A roguelike focusing on realism using the No Limits gaming system (see doc in repo for details). 

Requirements: (tested on the versions listed)</br>
Python 3.7 +</br>
Bearlibterminal 0.15.7 +</br>
numpy 1.16.2 +</br>
libtcod 9.2.5 +</br>

dill 0.3.1.1+</br>



Current Features:

- 29 hit locations

- Each location has three components: skin, tissue, and bone, and each has it's own deflection, soak, and health based on research

- Realistic injury effects ranging from light bruising to slicing a character in two. Accuracy of effects confirmed by watching animal carcasses attacked with period accurate weaponry. 

- Diseases accurately modeled. A head injury may lead to a persistent coma, while a liver injury may lead to cirrhosis. 

- Damage model based on physics, with PSI as the damage metric and weapon damage calculated based on skill, character weight, character physical power, stance, angle, distance, and type of blow. 

- Four different damage types: Piercing, Slashing, Bludgeoning, and Tearing. Each type is more or less effective versus a specific location component. For example, bludgeoning affects all components simultaneously but is more impactful on bone, while tearing is nearly completely ineffective vs bone. 

- No fixed weapon values. Weapon characteristics determined by the length, width, depth, materials, center of gravity, and pivot. 

- 29 Attributes, covering all aspects of a character, from pedal dexterity to taste acuity.

- No limits to attribute or skill value. Percentile-based system using modifiers and exploding dice to simulate logarithmic scales.

- Facing taking into account. A character facing away from an opponent cannot see or attack the opponent. 

- View distance calculated using facing, the character's 'Sight' attribute, and a 180 degree view angle. 

- Defensive options are dodge, parry, and block. Auto-block is implemented for specific locations based on the guard the character has selected. 

- Guards and maneuvers are weapon specific and real-world. Accurate sword and martial arts guards are in place and usable. 

- Stances implemented are also real world and usable. Open/Closed, Long/Short, High/Low, and Front/Rear decisions on weight distribution affects stability, dodging, and power generation.

- Blocking an attack does damage to the blocking implement equal to the attack damage.

- Feints implemented in a non-obvious way by giving a perceived attack bonus. Lack of information can fool both the PC and AI. 

- AI does not cheat. It remembers the last opponent location and hunts for them based on that information. 

- Attack history maintained for both PC and AI. Based on the character's Memory attribute, a certain number of attacks are remembered. If an opponent repeats an aspect of an old attack (using the same angle, weapon, location, or type of attack), you get a bonus to dodge or parry it. 

- AI operates on the same perceived percentages as the PC does. 

- Area of Control implemented, giving accurate advantages and disadvantages based on weapon length and engagement distance.

- Grappling implemented, allowing for nearly any imaginable wrestling combination, from a Kimora to an ankle compression lock, using generic terms like 'Limb capture' and 'Joint Lock'. If prerequisites are required, they are implemented. For example, a joint lock on the elbow requires you first perform a limb capture on the hand or arm. 

- Grappling defenses include reversal options for maneuvers that are reversible.

- Reach modeled using weapon length, limb length, relative angle, character flexibility, and pivot point. For example, based on the angle of you and your opponent, you may be able to punch his left shoulder but not his right. Or you may be able to stomp his foot but not his hand. 

  



Future Features: Too numerous to list. See issues for a reasonable idea of what is in progress and a very broad roadmap. 1.0 will be feature complete when the combat and management layers are both fully implemented as an arena-style gladiatorial combat simulator.  



Current Problems:

- Tuning problems, especially with unarmed and bludgeoning attacks.
- No help. Key combinations are contained (and modifiable) in options.py
- Currently in debugging state on character creation and unplayable (need to create a strable branch)

