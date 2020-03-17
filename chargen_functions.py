from utilities import roll_dice

def random_attr(method):
    #Roll a set of 29 random attributes using exploding dice and the three methods 29 2d100, 40 2d100 (take best), and 58 2d100 (take best)
    attributes = []
    if method == 1:
        while len(attributes) < 29:
            roll = roll_dice(2,100,True)
            attributes.append(roll)
        return attributes
    elif method == 2:
        while len(attributes) < 41:
            roll = roll_dice(2,100,True)
            attributes.append(roll)
        while len(attributes) > 29:
            attributes.remove(min(attributes))
        return attributes
    else:
        while len(attributes) < 59:
            roll = roll_dice(2,100,True)
            attributes.append(roll)
        while len(attributes) > 29:
            attributes.remove(min(attributes))
        return attributes

def height_curve(height_score, race_avg = 72):
    if height_score < 30:
        height = (race_avg*.3) + (height_score/150)*race_avg #22 - 36
    elif height_score < 50:
        height = (race_avg*.5) + ((height_score-29)/132)*race_avg #36 - 47
    elif height_score < 100:
        height = (race_avg*.66) + ((height_score-49)/258)*race_avg #48 - 62
    elif height_score < 160:
        height = (race_avg*.86) + ((height_score-99)/272)*race_avg #62 - 78
    elif height_score < 210:
        height = (race_avg*1.11) + ((height_score-159)/454)*race_avg #78 - 86
    elif height_score < 230:
        height = (race_avg*1.19) + ((height_score-209)/364)*race_avg #86 - 90
    elif height_score < 300:
        height = (race_avg*1.25) + ((height_score-229)/297)*race_avg #90 - 107
    else:
        height = (race_avg*1.5) + ((height_score-299)/910)*race_avg #107+ (400 = 115")
    
    return height

def attr_descriptions(attribute) -> str:
    desc = {}
    desc['Logic']='Facial Features skills define your character’s ability to solve Facial Featuresal problems in a direct manner, in other words, your ability to solve a problem without resorting to trial and error. Puzzle problems, math, composition skills, and troubleshooting are examples of Facial Features skills.  Note that this does not determine the speed with which such problems are solved, but rather, simply whether or not the problem is solvable at all by the individual. When rolling a save versus Facial Features, if time is a consideration, the save versus Facial Features determines whether or not a correct answer was given, a save versus Mental Celerity determines how quickly the answer was rendered.'
    desc['Memory']='Memory is your ability to retain information, as well as how quickly and readily information retention occurs. This ability constitutes both short-term and long-term memory. '
    desc['Wisdom']='Wisdom can almost be described as a combination of intuition and “common sense”. It is best used when attempting to notice a change in patterns or something out of the ordinary that is not related to the senses. '
    desc['Comprehension']='Comprehension is the ability to understand communication. In a nutshell, comprehension is the ability to recognize, absorb, and internalize communications. Comprehension and Communication are your two language abilities. '
    desc['Communication']='Communication is the ability to express your thoughts, either written, or verbally. People with high communication ratings tend to find it easier to get their point across, and may impart a bonus to the Comprehension saves of their audience. Comprehension and Communication are your two language abilities. '
    desc['Creativity']='Creativity describes your character’s ability to create something new and unique, whether it be an idea, art, or a solution to a problem that no one else recognizes (thinking “outside of the box”). In general, it describes a character’s inventiveness and imagination. '
    desc['Mental Celerity']='Mental Celerity is the speed with which the character thinks, and affects all saves that are time sensitive, including combat. Most people would term this as the ability to think on their feet. '
    desc['Willpower']='Willpower is the mental fortitude of a character. This ability is the amount of self control, emotional fortitude, and determination the character possesses. '
    desc['Steady State']='Steady state strength is strength imparted by “slow-twitch” muscle fibers. This is the classical definition of strength, the ability to hold an object of a particular weight for a particular unit of time. This statistic controls your encumbrance limit, which is the maximum amount of weight the character can carry without penalty. Total maximum carry weight is equal to five times this amount.  SS will play a small part in determining your tissue location hits values. '
    desc['Power']='Power is strength imparted by “fast-twitch” muscle fibers. This is the definition of strength commonly used, the ability to explosively lift weight from rest. This statistic controls your maximum lifts, and contributes to damage. PWR is also a major factor in determining tissue location hits. '
    desc['Manual Dexterity']='Manual dexterity defines your ability and coordination using your hands. It encompasses hand-eye coordination, limb separation (the ability to perform different actions simultaneously with different hands), digit manipulation, and ambidextrousness. This skill plays a vital role in combat. Based on your manual dexterity score, you will get a modifier to your attack/parry, as well as determine the modifier for your off hand. '
    desc['Pedal Dexterity']='Pedal dexterity defines your ability and coordination using your feet. It encompasses coordination, and limb separation. Pedal dexterity has a large effect on movement rate. '
    desc['Balance']='Balance is your ability to maintain balance of your own body and of other objects. '
    desc['Swiftness']='Swiftness is your ability to move quickly. Swiftness encompasses all bodily movements, and determines your maximum number of Action Points. Swiftness also has a major affect on your movement rate, attack/parry chance, and dodge chance. '
    desc['Flexibility']='Flexibility defines how flexible and mobile your character’s joints, tendons, and ligaments are. Flexibility plays a large role in a few skills, a small role in several skills, and will affect your movement rate and dodge chance. Flexibility will also modify your Effective Reach.'
    desc['Stamina']='Stamina defines your character’s general level of cardiovascular health. Stamina plays a large role in determining your Stamina points. '
    desc['Dermatology']='Dermatology defines the resiliency, toughness, thickness, and flexibility of your skin. As your body’s primary external defense mechanism, this is an important ability for all characters, and contributes to skin location hits. '
    desc['Bone Structure']='Bone structure defines the strength, thickness, and resiliency of your bones. BONE is highly important for all characters, as it alone defines your location hits for bone. '
    desc['Immune System']='Immune System determines your resistance to disease of all types, as well as your ability to fight off disease and return to health. '
    desc['Shock Resistance']='Shock resistance defines your body’s ability to withstand shock of any kind, be it electrical shock, cardiac shock, or septic shock. Shock can quickly lead to death if untreated, so your body’s resistance to shock is very important for all characters.'
    desc['Toxic Resistance']='Toxic resistance determines your ability to survive poisoning by toxic substances, be they natural or chemically formulated. Toxic resistance also determines how significantly your character is affected by state-altering substances (such as alcohol). '
    desc['Sight']='Sight defines your ability to visually examine your environment. It not only affects sight range, but also night vision, color differentiation, and peripheral vision. '
    desc['Hearing']='Hearing defines your ability to distinguish sound. Primarily, hearing affects your hearing range and directional assessment abilities. '
    desc['Taste/Smell']='Taste/Smell controls your ability to sense and recognize tastes and smells. '
    desc['Touch']='Touch determines your ability to differentiate and explore via your sense of touch. '
    desc['Facial Features']='Facial features determine how pleasing the shape and features on your face are to the average person. Again, since appearance is subjective, a high FAC score does not necessarily imply beauty to all. '
    desc['Height']='Height determines how tall or short your character is when compared against the average for his or her ethnicity. '
    desc['Body Fat']='Body fat determines how much protective fat is covering your body. FAT actually improves your location hits to skin, as it does serve a protective function. In addition, FAT can reduce the effects of cold environments on your body. However, in most cultures, high FAT ratings do not help your appearance. '
    desc['Shapeliness']='Shapeliness determines your character’s “figure”.  A high shapeliness rating would mean that your character has a voluptuous body (if female) or a “hunky” body (if male). Again, like all appearance sub-abilities, this ability is subjective.'

    return desc.get(attribute)

def rating_description(attribute, rating) -> str:
    attr_dict = {'Logic':{},'Wisdom':{},'Memory':{},'Comprehension':{},'Communication':{}, 'Creativity':{},'Mental Celerity':{},'Willpower':{},'Steady State':{},'Power':{},'Manual Dexterity':{},
                    'Pedal Dexterity':{},'Balance':{},'Swiftness':{},'Flexibility':{},'Stamina':{},'Dermatology':{},'Bone Structure':{},'Immune System':{}, 'Shock Resistance':{},'Toxic Resistance':{},
                    'Sight':{},'Hearing':{},'Taste/Smell':{},'Touch':{},'Facial Features':{},'Height':{},'Body Fat':{},'Shapeliness':{}}
    #Steps are [0]0-30,[1]31-70,[2]71-90,[3]91-110,[4]111-130,[5]131-160,[6]161-200,[7]200+
    #Logic
    attr_dict['Logic'][0] = 'Animal-level capabilities.'
    attr_dict['Logic'][1] = 'Difficulty with simple math (2+7), great difficulty with daily life.'
    attr_dict['Logic'][2] = 'Difficulty with easy math (42 divided by 18), difficulty with daily life, great difficulty with complex games such as chess.'
    attr_dict['Logic'][3] = 'Difficulty with fractions and percentages, great difficulty with complex math, difficulty with complex games.'
    attr_dict['Logic'][4] = 'Good at higher math, good at complex games, difficulty with very complex, open-ended problems.'
    attr_dict['Logic'][5] = 'Incredible ability with higher math and complex games, good at with very complex, open-ended problems.'
    attr_dict['Logic'][6] = 'Brilliant ability with higher math and complex games, very good with very complex, open-ended problems.'
    attr_dict['Logic'][7] = 'Unfathomable ability.'
    #Memory
    attr_dict['Memory'][0] = 'Animal-level capabilities.'
    attr_dict['Memory'][1] = 'Difficulty memorizing basic concepts (such as the alphabet).'
    attr_dict['Memory'][2] = 'Difficulty memorizing complex concepts, great difficulty with complete recall (such as reciting a page word for word).'
    attr_dict['Memory'][3] = 'Great difficulty memorizing extremely complex concepts (such as the full score for a musical piece), good at complete recall (can recite several important facts on a few subjects).'
    attr_dict['Memory'][4] = 'Some difficulty memorizing extremely complex concepts, excellent at complete recall (can recite great volumes of facts on many subjects).'
    attr_dict['Memory'][5] = 'Good at memorizing extremely complex concepts, brilliant at complete recall (can read several pages detailing highly complex concepts and recite them almost word for word immediately), memorizes many facts without effort, retains information for years after using it.'
    attr_dict['Memory'][6] = 'Very good at memorizing extremely complex concepts, Unfathomable at complete recall (can read 200+ pages and recite them almost word for word immediately, nearly permanent retention).'
    attr_dict['Memory'][7] = 'Truly photographic memory.'
    #Wisdom
    attr_dict['Wisdom'][0] = 'Animal-level capabilities.'
    attr_dict['Wisdom'][1] = 'Great difficulty with social cues and body language.'
    attr_dict['Wisdom'][2] = 'Some difficulty with social cues and body language, great difficulty recognizing change in complex patterns (such as political maneuvering).'
    attr_dict['Wisdom'][3] = 'Some difficulty recognizing change in complex patterns, great difficulty recognizing patterns in “chaos” (such as weather patterns).'
    attr_dict['Wisdom'][4] = 'Difficulty recognizing patterns in chaotic systems.'
    attr_dict['Wisdom'][5] = 'Good at recognizing patterns in chaotic systems.'
    attr_dict['Wisdom'][6] = '“It’s elementary, my dear….”'
    attr_dict['Wisdom'][7] = 'Can calculate the stock market based on the mating cycles of tree frogs.'
    #Comprehension
    attr_dict['Comprehension'][0] = 'Animal-level capabilities. Cannot speak understandably.'
    attr_dict['Comprehension'][1] = 'Basic understanding of a single language, will never have better than very poor reading ability (“See spot run”).'
    attr_dict['Comprehension'][2] = 'Fluency in a single language, difficult to achieve remedial understanding of related languages, may attain good reading ability.'
    attr_dict['Comprehension'][3] = 'Fluency in a single language and multiple dialects, some difficulty achieving remedial understanding of related languages, great difficulty achieving a basic understanding of un-related languages, may attain very good reading ability.'
    attr_dict['Comprehension'][4] = 'Mastery in a single language and can achieve fluency in multiple related languages, difficulty achieving a remedial understanding of un-related languages; Can become a speed reader.'
    attr_dict['Comprehension'][5] = 'Can achieve mastery in multiple languages, great difficulty in understanding non-human communication.'
    attr_dict['Comprehension'][6] = 'Can achieve mastery in most languages, difficulty in understanding non-human communication.'
    attr_dict['Comprehension'][7] = 'Can develop the ability to understand all detectible forms of communication.'
    #Steps are [0]0-30,[1]31-70,[2]71-90,[3]91-110,[4]111-130,[5]131-160,[6]161-200,[7]200+
    #Communication
    attr_dict['Communication'][0] = 'Animal-level capabilities. Can never learn to create even simple symbols.'
    attr_dict['Communication'][1] = 'Basic use of a single language, will never progress beyond very poor writing ability (“See spot run”).'
    attr_dict['Communication'][2] = 'Fluency in a single language, difficult to achieve remedial usage of related languages, may attain good writing ability.'
    attr_dict['Communication'][3] = 'Fluency in a single language and multiple dialects, some difficulty achieving remedial use of related languages, great difficulty achieving a basic usage of un-related languages, may attain very good writing ability .'
    attr_dict['Communication'][4] = 'Mastery in a single language and can achieve fluency in multiple related languages, difficulty achieving a remedial use of un-related languages.'
    attr_dict['Communication'][5] = 'Can achieve mastery in multiple languages, great difficulty in reproducing non-human communication.'
    attr_dict['Communication'][6] = 'Can achieve mastery in most languages, difficulty in reproducing non-human communication.'
    attr_dict['Communication'][7] = 'Can develop the ability to reproduce all detectible forms of communication.'
    #Creativity
    attr_dict['Creativity'][0] = 'Animal-level capabilities.'
    attr_dict['Creativity'][1] = 'Common thug.'
    attr_dict['Creativity'][2] = 'Used car salesman.'
    attr_dict['Creativity'][3] = 'Normal, low artistic ability.'
    attr_dict['Creativity'][4] = 'Amateur artist, cunning mind (common con artist, enterprising merchant).'
    attr_dict['Creativity'][5] = 'Accomplished artist, devious mind (mid-level politician).'
    attr_dict['Creativity'][6] = 'Master artist, diabolical cunning (high-level politician).'
    attr_dict['Creativity'][7] = 'Great master.'
    #Mental Celerity
    attr_dict['Mental Celerity'][0] = 'Animal-level capabilities.'
    attr_dict['Mental Celerity'][1] = 'Somewhat slow thought formulation, slow math computation, difficulty with non-instinctual quick thinking.'
    attr_dict['Mental Celerity'][2] = 'Somewhat quick thought formulation, median math computation, some difficulty with non-instinctual quick thinking.'
    attr_dict['Mental Celerity'][3] = 'Rapid thought formulation, very quick math computation, very good ability with non-instinctual quick thinking (accomplished soldier, top predatory animal).'
    attr_dict['Mental Celerity'][4] = '“Sharp as a tack”, capable of analyzing multiple possibilities at once.'
    attr_dict['Mental Celerity'][5] = 'Can resolve higher math internally, calculator-quick simple math computation, capable of analyzing most reasonable possibilities for any problem at the same time.'
    attr_dict['Mental Celerity'][6] = 'Capable of analyzing possibilities for multiple problems simultaneously, capable of completing several simultaneous complex thoughts.'
    attr_dict['Mental Celerity'][7] = 'Incalculable ability.'
    #Steps are [0]0-30,[1]31-70,[2]71-90,[3]91-110,[4]111-130,[5]131-160,[6]161-200,[7]200+
    #Willpower
    attr_dict['Willpower'][0] = 'Will always back down when challenged, very, very low pain threshold, never completes long tasks, emotionally handicapped.'
    attr_dict['Willpower'][1] = 'Usually backs down when challenged, low pain threshold, rarely completes long tasks, somewhat emotionally unstable.'
    attr_dict['Willpower'][2] = 'Sometimes backs down when challenged, average pain threshold, sometimes completes long tasks, emotionally stable.'
    attr_dict['Willpower'][3] = 'Only backs down when odds are against them, somewhat high pain threshold, usually completes long tasks, very emotionally stable.'
    attr_dict['Willpower'][4] = 'Very rarely backs down, regardless of odds, very high pain threshold, always completes long tasks, emotionally resilient.'
    attr_dict['Willpower'][5] = 'Never backs down and rarely compromises, extreme pain threshold, never gives up on “impossible” tasks, emotionally rock solid.'
    attr_dict['Willpower'][6] = 'Never backs down and never compromises, inhuman pain threshold, never gives up on “impossible” tasks, capable of weathering hellish emotional pain.'
    attr_dict['Willpower'][7] = '“Stubborn as a mule”, “That which doesn’t kill you…”'
    #Steady State
    attr_dict['Steady State'][0] = '5 second curl hold limit: '+ str(rating*.4) + ' lbs. Encumbrance limit: '+ str(rating*.15) + ' lbs.'
    attr_dict['Steady State'][1] = '5 second curl hold limit: '+ str(rating*.6) + ' lbs. Encumbrance limit: '+ str(rating*.3) + ' lbs.'
    attr_dict['Steady State'][2] = '5 second curl hold limit: '+ str(rating*.8) + ' lbs. Encumbrance limit: '+ str(rating*.5) + ' lbs.'
    attr_dict['Steady State'][3] = '5 second curl hold limit: '+ str(rating*1) + ' lbs. Encumbrance limit: '+ str(rating*.8) + ' lbs.'
    attr_dict['Steady State'][4] = '5 second curl hold limit: '+ str(rating*1.25) + ' lbs. Encumbrance limit: '+ str(rating*1) + ' lbs.'
    attr_dict['Steady State'][5] = '5 second curl hold limit: '+ str(rating*1.5) + ' lbs. Encumbrance limit: '+ str(rating*1.1) + ' lbs.'
    attr_dict['Steady State'][6] = '5 second curl hold limit: '+ str(rating*1.6) + ' lbs. Encumbrance limit: '+ str(rating*1.2) + ' lbs.'
    attr_dict['Steady State'][7] = '5 second curl hold limit: '+ str(rating*1.7) + ' lbs. Encumbrance limit: '+ str(rating*1.3) + ' lbs.'
    #Power
    attr_dict['Power'][0] = 'Max Bench Press: '+ str(rating*1) + ' lbs. Max Squat: '+ str(rating*1.5) + ' lbs. Max Deadlift: '+ str(rating*2)
    attr_dict['Power'][1] = 'Max Bench Press: '+ str(rating*1.5) + ' lbs. Max Squat: '+ str(rating*2) + ' lbs. Max Deadlift: '+ str(rating*2.5)
    attr_dict['Power'][2] = 'Max Bench Press: '+ str(rating*2) + ' lbs. Max Squat: '+ str(rating*2.5) + ' lbs. Max Deadlift: '+ str(rating*3)
    attr_dict['Power'][3] = 'Max Bench Press: '+ str(rating*2.25) + ' lbs. Max Squat: '+ str(rating*2.75) + ' lbs. Max Deadlift: '+ str(rating*3.25)
    attr_dict['Power'][4] = 'Max Bench Press: '+ str(rating*2.5) + ' lbs. Max Squat: '+ str(rating*3) + ' lbs. Max Deadlift: '+ str(rating*3.5)
    attr_dict['Power'][5] = 'Max Bench Press: '+ str(rating*2.75) + ' lbs. Max Squat: '+ str(rating*3.25) + ' lbs. Max Deadlift: '+ str(rating*3.75)
    attr_dict['Power'][6] = 'Max Bench Press: '+ str(rating*2.9) + ' lbs. Max Squat: '+ str(rating*3.6) + ' lbs. Max Deadlift: '+ str(rating*3.9)
    attr_dict['Power'][7] = 'Max Bench Press: '+ str(rating*3) + ' lbs. Max Squat: '+ str(rating*3.75) + ' lbs. Max Deadlift: '+ str(rating*4)
    #Steps are [0]0-30,[1]31-70,[2]71-90,[3]91-110,[4]111-130,[5]131-160,[6]161-200,[7]200+
    #Manual Dexterity
    attr_dict['Manual Dexterity'][0] = 'Some control of one hand at a time, disabled.'
    attr_dict['Manual Dexterity'][1] = 'Difficulty controlling both hands, somewhat poor finger control, slow hand movements.'
    attr_dict['Manual Dexterity'][2] = 'Some difficulty controlling both hands, somewhat slow hand movements.'
    attr_dict['Manual Dexterity'][3] = 'Average'
    attr_dict['Manual Dexterity'][4] = 'Talented, accomplished pianist, accomplished stage magician, skilled pickpocket.'
    attr_dict['Manual Dexterity'][5] = 'Amazing ability, ambidextrous, top pianist.'
    attr_dict['Manual Dexterity'][6] = 'These hands are MUCH quicker than the eye.'
    attr_dict['Manual Dexterity'][7] = 'Legendary slight of hand'
    #Pedal Dexterity
    attr_dict['Pedal Dexterity'][0] = 'Impaired control, slow leg movements, disabled.'
    attr_dict['Pedal Dexterity'][1] = 'Impaired control, somewhat slow leg movements.'
    attr_dict['Pedal Dexterity'][2] = 'Low Average'
    attr_dict['Pedal Dexterity'][3] = 'Average'
    attr_dict['Pedal Dexterity'][4] = 'Talented, accomplished kit drummer, accomplished dancer, skilled boxer, amateur tap dancer.'
    attr_dict['Pedal Dexterity'][5] = 'Highly talented, top boxer, professional tap dancer.'
    attr_dict['Pedal Dexterity'][6] = 'Amazing ability, top tap dancer.'
    attr_dict['Pedal Dexterity'][7] = 'Historic ability'
    #Balance
    attr_dict['Balance'][0] = 'Impaired balance, difficulty walking.'
    attr_dict['Balance'][1] = 'Impaired balance, clumsy.'
    attr_dict['Balance'][2] = 'Low balance, somewhat clumsy movements.'
    attr_dict['Balance'][3] = 'Average'
    attr_dict['Balance'][4] = 'Talented, can balance multiple objects with some difficulty.'
    attr_dict['Balance'][5] = 'Highly talented, can balance multiple objects, hold handstands indefinitely, skilled tightrope walker.'
    attr_dict['Balance'][6] = 'Amazing ability, top tightrope walker.'
    attr_dict['Balance'][7] = 'Legendary ability'
    #Steps are [0]0-30,[1]31-70,[2]71-90,[3]91-110,[4]111-130,[5]131-160,[6]161-200,[7]200+
    #Swiftness
    attr_dict['Swiftness'][0] = 'Very slow'
    attr_dict['Swiftness'][1] = 'Slow'
    attr_dict['Swiftness'][2] = 'Low average'
    attr_dict['Swiftness'][3] = 'Average'
    attr_dict['Swiftness'][4] = 'Talented, collegiate sprinter, amateur martial artist.'
    attr_dict['Swiftness'][5] = 'Highly talented, Olympic sprinter, accomplished martial artist.'
    attr_dict['Swiftness'][6] = 'Amazing ability, record-setting sprinter, top martial artist.'
    attr_dict['Swiftness'][7] = 'Legendary ability, Bruce Lee.'
    #Flexibility
    attr_dict['Flexibility'][0] = 'Very little flexibility, severe arthritis or other joint ailments.'
    attr_dict['Flexibility'][1] = 'Little flexibility, plagued by joint ailments.'
    attr_dict['Flexibility'][2] = 'Low average'
    attr_dict['Flexibility'][3] = 'Average'
    attr_dict['Flexibility'][4] = 'Talented, collegiate gymnast, amateur dancer, beginning contortionist.'
    attr_dict['Flexibility'][5] = 'Highly talented, Olympic gymnast, accomplished dancer, amateur contortionist.'
    attr_dict['Flexibility'][6] = 'Amazing ability, top gymnast or dancer, professional contortionist.'
    attr_dict['Flexibility'][7] = 'Legendary ability, Houdini.'
    #Stamina
    attr_dict['Stamina'][0] = 'Very poor condition. Likely to have serious cardio ailments.'
    attr_dict['Stamina'][1] = 'Out of shape. Average 50-year-old man.'
    attr_dict['Stamina'][2] = 'Average middle-aged man.'
    attr_dict['Stamina'][3] = 'Normal, healthy person in their prime.'
    attr_dict['Stamina'][4] = 'Conditioned body, amateur athlete. '
    attr_dict['Stamina'][5] = 'Astounding stamina, professional athlete.'
    attr_dict['Stamina'][6] = 'Record-setting athlete.'
    attr_dict['Stamina'][7] = 'Legendary stamina, record-setting endurance athlete.'
    #Steps are [0]0-30,[1]31-70,[2]71-90,[3]91-110,[4]111-130,[5]131-160,[6]161-200,[7]200+
    #Dermatology
    attr_dict['Dermatology'][0] = 'Unusually thin skinned, plagued by major skin diseases.'
    attr_dict['Dermatology'][1] = 'Thin skinned, somewhat more susceptible to skin diseases.'
    attr_dict['Dermatology'][2] = 'Low average'
    attr_dict['Dermatology'][3] = 'Average'
    attr_dict['Dermatology'][4] = 'High average'
    attr_dict['Dermatology'][5] = 'Thick skinned'
    attr_dict['Dermatology'][6] = 'Very thick skinned'
    attr_dict['Dermatology'][7] = 'Rhino hide'
    #Bone Structure
    attr_dict['Bone Structure'][0] = 'Severely weakened bones, small bumps may cause breakage.'
    attr_dict['Bone Structure'][1] = 'Weak bones, should avoid combat.'
    attr_dict['Bone Structure'][2] = 'Low average'
    attr_dict['Bone Structure'][3] = 'Average'
    attr_dict['Bone Structure'][4] = 'Strong bones, average athlete.'
    attr_dict['Bone Structure'][5] = 'Very strong bones, NFL lineman.'
    attr_dict['Bone Structure'][6] = 'Extremely strong bones.'
    attr_dict['Bone Structure'][7] = 'Genetic anomaly.'
    #Steps are [0]0-30,[1]31-70,[2]71-90,[3]91-110,[4]111-130,[5]131-160,[6]161-200,[7]200+
    #Immune System
    attr_dict['Immune System'][0] = 'Sick over half of the year.'
    attr_dict['Immune System'][1] = 'Serious illness strikes once per year, the Flu is cause for great concern, a Pneumonia infection will likely kill them.'
    attr_dict['Immune System'][2] = 'Low resistance to common illness, practically no resistance to rare afflictions.'
    attr_dict['Immune System'][3] = 'Average'
    attr_dict['Immune System'][4] = 'Somewhat high resistance common disease, low resistance to rare afflictions.'
    attr_dict['Immune System'][5] = 'High resistance common disease, somewhat resistant to rare afflictions.'
    attr_dict['Immune System'][6] = 'Very high resistance common disease, resistant to rare afflictions.'
    attr_dict['Immune System'][7] = 'Almost impervious to common disease, very resistant to rare afflictions.'
    #Shock Resistance
    attr_dict['Shock Resistance'][0] = 'Very highly deficient, poor circulation, may respond critically to any loss of blood.'
    attr_dict['Shock Resistance'][1] = 'Deficient, any large amount of blood loss will almost definitely lead to hypovolemic shock.'
    attr_dict['Shock Resistance'][2] = 'Somewhat deficient, can withstand some blood loss, but is significantly more prone to shock than average.'
    attr_dict['Shock Resistance'][3] = 'Average'
    attr_dict['Shock Resistance'][4] = 'Somewhat resistant, good circulation.'
    attr_dict['Shock Resistance'][5] = 'Very resistant, excellent circulation, significantly less prone to shock than average.'
    attr_dict['Shock Resistance'][6] = 'Highly resistant, may require extreme blood loss to induce shock.'
    attr_dict['Shock Resistance'][7] = 'Stands on mountaintops during thunderstorms for fun.'
    #Toxic Resistance
    attr_dict['Toxic Resistance'][0] = 'Very prone to toxins, might be able to handle a weak beer.'
    attr_dict['Toxic Resistance'][1] = 'Somewhat toxin prone, might be able to handle a few beers.'
    attr_dict['Toxic Resistance'][2] = 'Slightly toxin prone, could handle a few stout beers.'
    attr_dict['Toxic Resistance'][3] = 'Average'
    attr_dict['Toxic Resistance'][4] = 'Toxin resistant, could handle a bottle of stout spirits.'
    attr_dict['Toxic Resistance'][5] = 'Almost impervious to mild toxins, very difficult to get drunk.'
    attr_dict['Toxic Resistance'][6] = 'Resistant to strong poisons, nearly impossible to get drunk.'
    attr_dict['Toxic Resistance'][7] = 'Can sell thier blood to make snakebite venom.'
    #Steps are [0]0-30,[1]31-70,[2]71-90,[3]91-110,[4]111-130,[5]131-160,[6]161-200,[7]200+
    #Sight
    attr_dict['Sight'][0] = 'Clincally blind.'
    attr_dict['Sight'][1] = 'Highly deficient, very limited vision range'
    attr_dict['Sight'][2] = 'Low Average'
    attr_dict['Sight'][3] = 'Average'
    attr_dict['Sight'][4] = 'Very good vision'
    attr_dict['Sight'][5] = 'Exceptional vision'
    attr_dict['Sight'][6] = 'Astonishing vision'
    attr_dict['Sight'][7] = '“Eyes like a hawk”'
    #Hearing
    attr_dict['Hearing'][0] = 'Mostly deaf'
    attr_dict['Hearing'][1] = 'Very poor hearing'
    attr_dict['Hearing'][2] = 'Low average'
    attr_dict['Hearing'][3] = 'Average'
    attr_dict['Hearing'][4] = 'High Average'
    attr_dict['Hearing'][5] = 'Excellent hearing'
    attr_dict['Hearing'][6] = 'Exceptional hearing'
    attr_dict['Hearing'][7] = 'Daredevil'
    #Taste/Smell
    attr_dict['Taste/Smell'][0] = 'Only tastes/smells very strong substances.'
    attr_dict['Taste/Smell'][1] = 'Difficulty distinguishing similar odors and smells (oranges and lemons).'
    attr_dict['Taste/Smell'][2] = 'Difficulty distinguishing very similar odors and smells (lemon and lime).'
    attr_dict['Taste/Smell'][3] = 'Average'
    attr_dict['Taste/Smell'][4] = 'Can smell something out of the ordinary from double the normal distance.'
    attr_dict['Taste/Smell'][5] = 'Can list the spices in foods based on smelling them.'
    attr_dict['Taste/Smell'][6] = 'Can detect people by scent.'
    attr_dict['Taste/Smell'][7] = 'Sniffs butts to make friends.'
    #Touch
    attr_dict['Touch'][0] = 'Most body parts are numb, may have feeling in one or two locations'
    attr_dict['Touch'][1] = 'Dulled sense, may have difficulty feeling mild pain.'
    attr_dict['Touch'][2] = 'Dulled sense, may have difficulty feeling light contact.'
    attr_dict['Touch'][3] = 'Average'
    attr_dict['Touch'][4] = 'Sensitive'
    attr_dict['Touch'][5] = 'Highly sensitive'
    attr_dict['Touch'][6] = 'Extremely sensitive'
    attr_dict['Touch'][7] = 'Can detect minor changes in speed, direction, and temperature of air currents.'
    #Steps are [0]0-30,[1]31-70,[2]71-90,[3]91-110,[4]111-130,[5]131-160,[6]161-200,[7]200+
    #Facial Features
    attr_dict['Facial Features'][0] = 'Disfigured'
    attr_dict['Facial Features'][1] = 'Ugly'
    attr_dict['Facial Features'][2] = 'Low average'
    attr_dict['Facial Features'][3] = 'Average'
    attr_dict['Facial Features'][4] = 'Comely'
    attr_dict['Facial Features'][5] = 'Beautiful'
    attr_dict['Facial Features'][6] = 'Top Model'
    attr_dict['Facial Features'][7] = '“The face that launched a thousand ships…”'
    #Height
    attr_dict['Height'][0] = '“Follow the yellow brick road…”'
    attr_dict['Height'][1] = 'Really short'
    attr_dict['Height'][2] = 'Low average'
    attr_dict['Height'][3] = 'Average'
    attr_dict['Height'][4] = 'Bumps head on doorways'
    attr_dict['Height'][5] = '“How’s the weather up there?”'
    attr_dict['Height'][6] = 'Pro basketball star'
    attr_dict['Height'][7] = 'Often mistaken for a giant.'
    #Body Fat
    attr_dict['Body Fat'][0] = str(rating*.13) + '% body fat. Starving to death.'
    attr_dict['Body Fat'][1] = str(rating*.15) + '% body fat'
    attr_dict['Body Fat'][2] = str(rating*.22) + '% body fat'
    attr_dict['Body Fat'][3] = str(rating*.22) + '% body fat'
    attr_dict['Body Fat'][4] = str(rating*.27) + '% body fat'
    attr_dict['Body Fat'][5] = str(rating*.28) + '% body fat'
    attr_dict['Body Fat'][6] = str(rating*.3) + '% body fat'
    attr_dict['Body Fat'][7] = str(rating*.32) + '% body fat'
    #Shapeliness
    attr_dict['Shapeliness'][0] = 'Deformed'
    attr_dict['Shapeliness'][1] = 'Unappealing'
    attr_dict['Shapeliness'][2] = 'Low average'
    attr_dict['Shapeliness'][3] = 'Average'
    attr_dict['Shapeliness'][4] = 'Above Average'
    attr_dict['Shapeliness'][5] = 'Underwear model'
    attr_dict['Shapeliness'][6] = 'Crowdstopper'
    attr_dict['Shapeliness'][7] = 'Sex icon'


    if rating <= 30:
        i=0
    elif rating <=70:
        i=1
    elif rating <= 90:
        i=2
    elif rating <= 110:
        i=3
    elif rating <= 130:
        i=4
    elif rating <= 160:
        i=5
    elif rating <= 200:
        i=6
    else:
        i=7

    return attr_dict.get(attribute).get(i)
