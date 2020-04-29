
import enums
from components.ai import CombatAI


#UI Vars
screen_width = 180
screen_height = 90
status_panel_h = screen_height
status_panel_w = 30
status_panel_x = screen_width - status_panel_w
status_panel_y = 0

enemy_panel_h = screen_height
enemy_panel_w = 30
enemy_panel_x = 0
enemy_panel_y = 0

message_panel_h = 15
message_panel_w = screen_width - status_panel_w - enemy_panel_w
message_panel_y = screen_height - message_panel_h + 1
message_panel_x = enemy_panel_w

map_width = screen_width - status_panel_w - enemy_panel_w
map_height = screen_height - message_panel_h + 1
map_x = enemy_panel_w
map_y = 0

panel_types = (0,1,2,3)
panel_colors = (('white','light_gray'), ('black','white'), ('black', 'yellow'), ('yellow', 'crimson'))

#Map setup
blocked = ((30,30),(30,31),(30,32),(30,33),(30,34),(30,35),(31,30),(32,30),(33,30),(34,30),(35,30))

#Debug
debug = True

#Base time units
fps = 30

#Player stat archetypes for testing
fat = [130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,400,130]
tank = [130,130,130,130,130,130,130,130,250,250,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,180,200,130]
fw = [130,130,130,130,130,130,130,130,150,150,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,50,50,130]
hw = [130,130,130,130,130,130,130,130,250,250,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,150,80,130]
hopeless_fat = [40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,130,480,40]
hopeless = [40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40]
midget = [130,130,130,130,130,130,130,130,250,250,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,30,80,130]
tallboy = [130,130,130,130,130,130,130,130,250,250,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,350,80,130]
hi_init = [130,130,130,130,130,130,430,130,250,250,130,130,130,430,130,130,130,130,130,130,130,130,130,130,130,130,350,80,130]
low_init = [130,130,130,130,130,130,30,130,150,150,130,130,130,30,130,130,130,130,130,130,130,130,130,130,130,130,50,50,130]

#Function below needed to convert archetype lists into correct format for entity creation
def convert_attr_list(attr_list) -> dict:
    abr_list = ['log','mem','wis','comp','comm','cre','men','will','ss','pwr','man','ped','bal','swift','flex','sta','derm','bone','immune','shock','toxic','sit','hear','ts','touch','fac','ht','fat','shape']
    attr_dict = dict()
    i = 0
    for a in attr_list:
        attr_dict[abr_list[i]] = a
        i += 1
    return attr_dict

#Fighter specs
player_attr = convert_attr_list(hw)
player_s_dict = {'brawling': 8, 'deflect': 8, 'dodge': 6, 'wrestling': 12, 'long_sword': 8}
player_fighter = ['Player', player_attr, player_s_dict, 4]
player_r_weapon = 'De_Medium_Sword'
player_l_weapon = 'Unarmed'
player_rf_weapon = 'Unarmed'
player_lf_weapon = 'Unarmed'
player_weapons = {'r_wpn': player_r_weapon, 'l_wpn': player_l_weapon, 'rf_wpn': player_rf_weapon, 'lf_wpn': player_lf_weapon}
player_armor = [{'component':'Curiass','construction':'Plate','main_material' : 'Hardened Steel','thickness':.1},{'component':'Hauberk','construction':'Padded','main_material' : 'leather','thickness':.3}, {'component':'Hauberk','construction':'Chain','main_material' : 'Hardened Steel','thickness':.2}, {'component':'Jerkin','construction':'Padded','main_material' : 'Cloth','thickness':.05}, {'component':'Coif','construction':'Chain','main_material' : 'Hardened Steel','thickness':.3}, {'component':'Coif','construction':'Padded','main_material' : 'Cloth','thickness':.3}]

#Enemy specs
enemy_attr = convert_attr_list(low_init)
enemy_s_dict = {}
enemy_fighter = ['Enemy', enemy_attr, enemy_s_dict, 0, CombatAI]
enemy_r_weapon = 'Unarmed'
enemy_l_weapon = 'Unarmed'
enemy_rf_weapon = 'Unarmed'
enemy_lf_weapon = 'Unarmed'
enemy_weapons = {'r_wpn': enemy_r_weapon, 'l_wpn': enemy_l_weapon, 'rf_wpn': enemy_rf_weapon, 'lf_wpn': enemy_lf_weapon}
enemy_armor = [{'component':'Curiass','construction':'Plate','main_material' : 'Hardened Steel','thickness':.1},{'component':'Hauberk','construction':'Padded','main_material' : 'leather','thickness':.3}, {'component':'Hauberk','construction':'Chain','main_material' : 'Hardened Steel','thickness':.2}, {'component':'Jerkin','construction':'Padded','main_material' : 'Cloth','thickness':.05}, {'component':'Coif','construction':'Chain','main_material' : 'Hardened Steel','thickness':.3}, {'component':'Coif','construction':'Padded','main_material' : 'Cloth','thickness':.3}]
enemy_no_armor = []
#Fighter and Weapons lists
fighters = [player_fighter, enemy_fighter]
weapons = {'Player': player_weapons, 'Enemy': enemy_weapons}

#Entity list
player = (60, 50, '@', 'white', 'Player', enums.EntityState.conscious, True, True)
enemy = (60, 60, '@', 'yellow', 'Enemy', enums.EntityState.conscious, False, True)
entities = [player, enemy]

#New player template
new_player = (60, 50, '@', 'white', 'New Player', enums.EntityState.conscious, True, True)

#Name dict for random names
common_male = ['Merek','Carac','Ulric','Tybalt','Borin','Sadon','Terrowin','Rowan','Forthwind','Althalos','Fendrel','Brom','Hadrian','Benedict','Gregory','Peter','Henry','Frederick','Walter','Thomas','Arthur','Bryce','Donald','Leofrick','Letholdus','Lief','Barda','Rulf','Robin','Gavin','Terryn','Ronald','Jarin','Cassius','Leo','Cedric','Gavin','Peyton','Josef','Janshai','Doran','Asher','Quinn','Zane','Xalvador','Favian','Destrian','Dain','Lord Falk','Berinon','Tristan','Gorvenal']
common_female = ['Millicent','Alys','Ayleth','Anastas','Alianor','Cedany','Ellyn','Helewys','Malkyn','Peronell','Sybbyl','Ysmay','Thea','Jacquelyn','Amelia','Gloriana','Bess','Catherine','Anne','Mary','Arabella','Elizabeth','Hildegard','Brunhild','Adelaide','Alice','Beatrix','Cristiana','Eleanor','Emeline','Isabel','Juliana','Margaret','Matilda','Mirabelle','Rose','Helena','Guinevere','Isolde','Maerwynn','Muriel','Winifred','Godiva','Catrain','Angmar','Gussalen','Jasmine','Josselyn','Maria','Victoria','Gwendolynn','Enndolynn','Janet','Luanda','Krea','Rainydayas','Atheena','Dimia','Phrowenia','Aleida','Ariana','Alexia','Katelyn','Katrina','Loreena','Kaylein','Seraphina','Duraina','Ryia','Farfelee','Iseult','Benevolence','Brangian','Elspeth']
norse_male = ['Abraham','Adam','Adel','Adolf','Adrian','Ágúst','Albert','Antonius','Ari','Árni','Axel','Baldur','Bárður','Bernhard','Bjarni','Björgólfur','Bjorn','Brandur','Brynjólfur','Carl','Christian','Dagur','Davíð','Eggert','Eiður','Einar','Eldar','Ellert','Elmar','Felix','Friðrik','Frosti','Garðar','Gísli','Gissur','Grímur','Guðmundur','Gunnar','Gunnlaugur','Gustav','Halldór','Hannes','Haraldur','Haukur','Helge','Herman','Hörður','Hrafn','Ingvar','Irnes','Jakob','Jóhann','Jón','Jonas','Karel','Karl','Karli','Kjartan','Klaus','Kristján','Kristofer','Kristófer','Leif','Linus','Matthias','Njáll','Olaf','Ólafur','Óli','Otto','Páll','Philip','Ragnar','Robert','Rudolph','Samuel','Sigurður','Skúli','Snorri','Stefán','Sveinbjörn','Sveinn','Theodor','Thor','Þórður','Þorsteinn','Þorvaldur','Tobias','Trausti','Vilhjálmur']
norse_female = ['Agnes','Amalia','Anna','Anneliese','Antonia','Aurora','Björk','Caroline','Charlotta','Dagmar','Elsa','Emma','Erika','Estelle','Frida','Frøydis','Grete','Guðrún','Heidi','Helena','Helene','Helga','Hilda','Hildur','Hulda','Ingrid','Judith','Kalla','Karen','Karolin','Karolina','Katrín','Kerstin','Kristi','Kristin','Maria','Marianne','Monika','Natalie','Nikoletta','Nina','Olivia','Ósk','Rita','Sigríður','Sigurrós','Steinunn','Susanne','Tara','Unnur','Valerie']
verdurian_male = ['Ahmose Pen-Nekhebet','Ahmose Sipair','Ahmose Sipar','Ahmose Sitayet','Ahmose','son of Ebana','Amenemhab','Amenemhet','Amenemhet','Amenhirkhepshef','Amenhotep','son of Hapu','Amenken','Amenmose','Amunemhat','Amunemhet','Anen','Ani','Ankhkhaf','Anubisemonekeh','Auibre','Banefre','Baufre','Bay','Bebi','Bek','Dedi','Dedu','Djar','Djau','Djedefhor','Djedptahaufankh','Djehontyhetep','Djehutihotep','Djhutmose','Hapuneseb','Hardedef','Harkhaf','Haremhab','Hekaib','Hemiunu','Henenu','Hepzefa','Herihor','Horwedja','Huy','Huya','Ibebi','Ibi','Idu','Idut','Ikernofret','Ikhernofret','Ikudidy','Imhotep','Ineni','Intef','Inyotefoker','Ipuki','Irsu','Ipy','Iumeri','Kagemni','Kawab','Kenamon','Kewab','Kha','Khaemweset','Khamet','Khenemsu','Khensuhotep','Khentemsemet','Khuenre','Kheruef','Khufukaef','Khnumhotep','Khui','Khusebek','Khuy','Maherpa','Mahu','Mai','Ma\'nakhtuf','Masaharta','May','Maya','Mehy','Meketre','Men','Menkhaf','Menkheperresenb','Menna','Merenre','Mereruka','Meri','Merimose','Meriptah','Merkha','Mernuterseteni','Meryatum','Meryre','Merytatum','Metjen','Minnakht','Mitry','Montuherkhopshef','Nakht','Nakhte','Nanefer-ka-ptah','Nebamun','Nebemakhet','Nebenteru','Nebetka','Nebmakhet','Nebwawi','Nebwenef','Neferhotep','Neferkheperuhersekheper','Neferiryetnes','Neferma\'at','Neferpert','Neferti','Neferu','Nefer-weben','Nehesy','Nehi','Nekaure','Nekhebu','Nekonekh','Nekure','Nenkhsekhmet','Nenwef','Nessumontu','Nibamon','Nibamun','Nebamon','Padiaset','Pamiu','Panehsi','Panhey','Panhesy','Parennefer','Paser','Patenemheb','Pawah','Pawara','Pawero','Penno','Penni','Penne','Pentu','Pepy-Nakht','Pinhasy','Prehirwonmef','Prehirwonnef','Ptahshepses','Ptah-Shepses','Puyemre','Rahotep','Raia','Ramose','Ranofer','Rawer','Re\'emkuy','Re\'hotpe','Rehu-erdjersenb','Rehu\'ardjersen','Rekhmire','Renni','Ro-an','Ro-en','Ra-an','Rudjek','Ruia','Sabaf','Sabni','Sabu','Sarenpet','Sebek-khu','Sebni','Sehetepibre','Inti Sendjemib','Mehi Sendjemib','Senenmut','Sen-nefer','Setau','Setka','Sihathor','Simontu','Surero','Tchanun','Tchay','Teni-menu','Thaneni','Theshen','Thethi','Thuity','Ti','Tiy','Tia','Tjuroy','Tuta','Urhiya','Userhat','Wahneferhotep','Wajmose','Wenamon','Weni','Wenisankh','Unasankh','Weshptah','Woser','Yey','Yuf','Yuia','Yuny','Yuya','Zezemonekh']
verdurian_female = ['A\'at','Ahhotep','Ahmose','Ahmose Hentempet','Ahmose Hent-Tenemu','Ahmose Henuttimehu','Ahmose Inhapi','Ahmose Meryetamun','Ahmose Meryt-Amon','Ahmose Nefertary','Ahmose-Nefertari','Ahmose Nefertiry','Ahmose Sitkamose','Ahmose Tumerisy','Ahset','Amtes','Yamtisy','Amunet','Amuniet','Ana','Aneksi','Ankhesenamon','Ankhesenpaaten','Ankhesenpaaten-ta-sherit','Ankhes-Pepi','Ankhetitat','Ankhnesmerire','Ankhnesmery-Re','Ankhnes-Pepi','Aoh','Ashait','Ashayt','Ast','Atet','Baketamon','Bakt','Baktwerel','Beketaten','Berenib','Bernib','Betresh/Tarset','Betrest','Bint-Anath','Bunefer','Dedyet','Fent-Ankhet','Gilukhipan','Hapynma\'at','Hedjhekenu','Henhenet','Henhenit','Henite','Hent','Hentaneb','Hentmereb','Hentmire','Hent-Temehu','Henutmire','Henutsen','Henuttawy','Herit','Herneith','Hetepheres','Hetep-heres','Hetephernebty','Heterphenebty','Huy','Imi','Yem','Inhapi','Thent hep','Intakaes','Iput','Ipwet','Ipy','Isetnofret','Isis','Istnofret','Isetnofret','Itekuyet','Itet','Kasmut','Kawit','Kemanub','Kemanut','Kemsit','Kemsiyet','Khemsait','Kentetenka','Khama\'at','Khamerernebty','Khemut','Khentikus','Khentkawes','Khenut','Khnumt','Khnumet','Khumyt','Khumit','Khuit','Kiya','Ma\'at Hornefrure','Maatkare Nefertary','Maketaten','Meket-Aten','Mekytaten','Maia','Menhet','Menwi','Mereneith','Mereryet','Meresankh','Meritites','Merneith','Merseger','Merti','Meryetamun','Meryetre','Merysankh','Merytamon','Meryt-Amon','Merit-Amon','Merytaten','Meritaten','Mayati','Merytaten-tasherit','Meryt-Re-Hatshepsut','Mutemwiya','Mutnodjme','Mutnodjmet','Mutnofret','Muyet','Nebet','Nebettawy','Nebt','Nebt-tawya','Nebt-tawy','Neferhent','Neferhetep','Neferhetepes','Neferkent','Neferneferure','Nefertari','Nefertiti','Nefertkau','Nefertkaw','Neferu','Neferu','Neferukhayt','Neferukayt','Neferukhayet','Neferukhebt','Neferu-Re','Nefret','Nefru','Nefru-Ptah','Nefrusheri','Nefru-Sobek','Nefru-totenen','Nefrutoten','Neith','Neithotep','Nemathap','Nenseddjedet','Neshkons','Nestanebtishru','Nit','Nitemat','Nithotep','Nodjmet','Nofret','Nofret','Nubkhas','Nubkhesed','Rai','Raia','Redji','Reputneb','Sadeh','Sadek','Sebek-shedty-Neferu','Senebsen','Senisonbe','Sennuwy','Seshseshet','Shesheshet','Sitamun','Sit-Hathor-Yunet','Sitre','Sobekemsaf','Sotepenre','Ta-Opet','Tadukhipa','Takhaet','Tarset','Taweret','Tem','Tener','Teo','Tetisheri','Tey','Thent Hep','Inhapi','Tia','Tiy','Tiye','Tjepu','Tuia','Tuya','Tuyu','Twosre','Weret-Imtes']
kebrini_male = ['Abaka','Achigh Shirun','Adarkidai','Adkiragh','Adya','Agasiletai','Agsaldai','Aguchu','Agujam','Achujam Bugural','Ajai','Ajinai','Akhutai','Alagh','Alagh Yid','Altun Ashugh','Amasar','Arin Tasai','Argasun Qorchi','Arkhai Khasar','Asha Gambu','Ashigh Temur','Badai','Bagaridai','Bai Shingor','Bala','Balagachi','Bardam','Bartan','Barulatai','Bede','Bedes','Begugtei','Belgunutei','Besutei','Biger','Bilge','Boal','Bodonchar','Bogarji','Bogen','Bogorchu','Bolkhadar','Borjigidai','Boroghul','Boroldai','Boroldai Suyalbi','Bortachikhan','Bucharan','Bughutu Salji','Bugidai','Bugunutei','Bugurul','Bukidai','Bultechu','Bulugan','Buqatai','Buri Bulchiru','Butu','Cyriacus Buyirugh','Chanai','Chanar','Chaghagan Khoga','Chaghagan Uua','Chagurkhai','Chakhurkhan','Chidukhul','Chigu','Chiledu','Chilger','Chiluku P','Chimbai','Chimbai Dargan','Chulgetei','Dagun','Daidukul','Darbai','Daritai','Dei','Devet Berdi','Dhunan','Dobun','Dodai','Dologadai','Donoi','Dorbei','Dori Bukha','Durulji Tayiji','Duua','Erke Khara','Geugi','Guchugur','Gughlug','Gugun','Gur','Harghasun','Hobogetur','Horkhudagh','Husun','Idughadai','Inalchi','Inancha Bilge','Jakha Gambu','Jajiradai','Janggi','Jarchigudai','Jeder','Jirghogadai','Jebke','Jegu','Jelme','Jubkhan','Jungdu','Jungsai','Jungso','Jungshoi','Jurchedei','Kamala','Khachi','Khada','Khadagan','Khadagan Daldurkhan','Khadagan Tasai','Khagatai Darmala','Khaguran','Khaidai','Khal','Khaligudar','Khalja','Kharachar','Kharchu','Khashi','Khongkhai','Khongtaghar','Qoricar Mergan','Khorchi','Khorghosun','Khori Shilemun Taisi','Khori Subechi','Khorilartai','Khongkhortai','Khuchar','Khudu','Khudus','Khudus Khalkhan','Khudukha','Khurchakhus','Khuril Ashigh','Khutula','Khuyildar','Kinggiyadai Bukha','Kiratai','Kiriltugh','Kishiligh','Kogsegu Sabragh','Koko Chos','Kokochu','Kokochu Kirsagan','Kokochu Teb Tenggeri','Kuchar','Kuyuk','Maqa Tudan','Maqali','Masgud','Megujin','Menggetu','Megetu','Morokha','Mungke','Muge','Mulkhalkhu','Munglig','Mungetu','Munggugur','Mutugen','Narin Kegen','Narin Togoril','Nayaga','Nekun Taisi','Odchigin Abaga','Ogele','Okhotur','Okin','Okin Barkhagh','Olai Anda','Olar','Oldaghar','Ong','Onggiran','Onggur','Orda','Ordu Coronartai','Sacha','Sechegur','Semsochi','Sidurgu','Shigi Khutukhu','Shikigur','Shilugei','Shinghkhor','Shiraghul','Shirgugetu','Siban','Sinkur','Sokhor','Sorkhan Shira','Sorkhatu Jurki','Soyiketu','Sukegei','Suyiketu','Tabur N','Tagadhur','Taghai','Tahar N','Taichar','Taichu','Tamachag','Taragai P','Tartu','Tayang','Telegetu','Temuge','Tobsakha','Tobukha','Todogen Girte','Tolon','Tolun','Torbi Tashi','Tordung','Torgaljin','Torgan','Tumbinai','Tumun','Tungge','Tungkhuidai','Tutei','Tuyuideger','Uchikin','Udutai','Uighurtai','Ukhuna','Ukilen','Yabuqa','Yedi Tublugh','Yegu','Yesunge','Yeke Cheren','Yeke Chiledu','Yeke Couru','Yokhunan','Yurukhan']
kebrini_female = ['Alagh Yid','Alaqa','Barghujin','Berude','Borte','Borte Jusin','Botokhui Targhun','Budan','Chagur','Chakha','Checheyigen','Chotan','Dagasi','Dorgene','Ebegei','Gorbeljin','Gurbesu','Holuikhan','Hujaghur','Ibakha','Jaliqai','Khadagan','Khogaghchin','Khojin','Khorijin','Khugurchin','Maral','Nomolun','Orbei','Sayin Maral Qayag','Silun Gorgelji','Sokhatai','Tegusken','Temulun','Temulun Abagai','Yesugen','Yesui','Yisu Qatun','Yisugei Qatun']
wedei_male = ['Bika','Bukuro','Do:ngu','Gusa','Naugu','La:igu','Jauka','Kalte:du','Kaltoa','Kenur','Lu:gu','Ma:nka','Mo:mo','Muku','No:gu','?o:dugu','?ol','?or','?orzuko','?u:ma','Pu?an','Rakugu','Ru:gu','Saiju?','Sa?gu','Simul','So?ka','Sojo','Suk','Telgu','Tikma','To:gu','To:rogu','We:a','Ye:bi:li','Zeba','Zaitoa']
wedei_female = ['Bi:po:','Bi:zi','Buka','Go:rtuzi','Jenka','Jo?po:','Jo?zi','Kunu','Loda','Ma:in','Ma?ayuma','Mogau','No:zi','?eka','?ina','?iyan','Paira','Pirzi','Reja','Re:tema','So?mi?','Saki','Sali:l','Sabukka','Sabukma','Sekibu','Seya','Si','Siya','Ta?zi','Teldi:n','Watasu:','Wete','Yai','Ya:li','Yoru','Zaiji']
wedei_unisex = ['Anda','Ba:un','Bi:ka','Da:iul','Itera','Iterul','Ka:yomul','Kala','Ku:rul','Ma:un','Miri?','Muna','Nanno','No:bi:','?a:ila:ul','?egeul','?ota','Paudu','Pikji','Raka','Rasak','Ruk','Ruzi','Seki','Su:wata','Sabuk','Sal','Selul','Sukzau','Tokka','Weda?','Wen','Worgu','Ye:bi:','Zaikka','Zaupo:','Ze:tur']
name_dict = {'Common':{'male':[],'female':[],'unisex':[]},'Norse':{'male':[],'female':[],'unisex':[]},'Verdurian':{'male':[],'female':[],'unisex':[]},'Kebrini':{'male':[],'female':[],'unisex':[]},'Wedei':{'male':[],'female':[],'unisex':[]}}
name_dict['Common']['male'] = common_male
name_dict['Common']['female'] = common_female
name_dict['Norse']['male'] = norse_male
name_dict['Norse']['female'] = norse_female
name_dict['Verdurian']['male'] = verdurian_male
name_dict['Verdurian']['female'] = verdurian_female
name_dict['Kebrini']['male'] = kebrini_male
name_dict['Kebrini']['female'] = kebrini_female
name_dict['Wedei']['male'] = wedei_male
name_dict['Wedei']['female'] = wedei_female
name_dict['Wedei']['unisex'] = wedei_unisex

#Key Dicts in order of key, command_verb
default_keys = {'q':{'move':'nw'}, 'w':{'move':'n'}, 'e':{'move':'ne'}, 'd':{'move':'e'}, 'c':{'move':'se'}, 
                'x':{'move':'s'}, 'z':{'move':'sw'},'a':{'move':'w'}, 41: {'esc': 'esc'}, '.':{'spin':'cw'}, ',':{'spin':'ccw'},
                80: {'move':'w'}, 79:{'move':'e'},82:{'move':'n'},81:{'move':'s'},';':{'strafe':'strafe'},95:{'move':'nw'}, 
                96:{'move':'n'}, 97:{'move':'ne'}, 94:{'move':'e'}, 91:{'move':'se'},90:{'move':'s'},
                89:{'move':'sw'},92:{'move':'w'},98:{'spin':'ccw'},'u':{'stand':'stand'},'p':{'prone':'prone'},'k':{'kneel':'kneel'},
                '@':{'csheet':'csheet'}}

key_maps = [default_keys]

#Gameplay options
show_rolls = True