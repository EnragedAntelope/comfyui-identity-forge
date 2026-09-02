import { app } from "../../scripts/app.js";

/*
 * IdentityForgeCosplayer frontend extension -- the franchise filter.
 *
 * The problem it solves: the character combo is one flat list of ~1,800 bare
 * names with no franchise shown anywhere, so a user who remembers a *look* but
 * not a name has nothing to narrow by. ComfyUI's combo search matches the option
 * text, and the option text IS the value the backend receives, so the franchise
 * cannot simply be appended to each name -- ComfyUI validates combo values at
 * /prompt, and decorating them would invalidate the character stored in every
 * saved workflow.
 *
 * So this is a VIEW-ONLY control, and deliberately not a schema input:
 *
 *   - It is added here in JS with `serialize: false`, exactly like the main
 *     node's group headers and bulk buttons. ComfyUI skips non-serializing
 *     widgets when it writes `widgets_values`, so the serialized array is
 *     byte-identical to before this file existed. A workflow saved by an older
 *     version loads unchanged, and one saved now opens fine on an older version.
 *     There is no schema change, so `define_schema()` and the frontend fixture
 *     are untouched too.
 *   - Because it does not serialize, it does not need to: the filter is a way to
 *     *find* a character, not part of the character. It resets to "Any" on reload
 *     while the chosen character -- the thing that actually matters -- persists.
 *
 * Two UX rules it must never break:
 *
 *   1. Filtering never changes the user's selection. Narrowing to a franchise
 *      that excludes the current character keeps that character selected and
 *      keeps it in the list, so the widget can never silently resolve to
 *      something the user did not pick.
 *   2. The sentinels ("None", "Random -- any/female/male") survive every filter.
 *      They are how the node is turned off or randomized, and hiding them behind
 *      a franchise choice would strand the user.
 *
 * `random_scope` is a different control and stays untouched: it narrows what the
 * "Random --" entries may roll on the backend. This filter only narrows what the
 * dropdown shows. The tooltip says so, because the two are easy to confuse.
 *
 * Degrades gracefully -- any failure is caught so the node still works.
 */

// >>> GENERATED DATA — do not edit by hand. Regenerate: python scripts/generate_js_data.py >>>
const COSPLAYER_FRANCHISES = {
  "101 Dalmatians": [
    "Cruella de Vil"
  ],
  "A Certain Scientific Railgun": [
    "Misaka Mikoto"
  ],
  "A Nightmare on Elm Street": [
    "Freddy Krueger"
  ],
  "ARMS": [
    "Twintelle"
  ],
  "Ace Attorney": [
    "Maya Fey"
  ],
  "Adventure Time": [
    "Finn the Human",
    "Fionna",
    "Ice King",
    "Jake the Dog",
    "Marceline the Vampire Queen",
    "Princess Bubblegum"
  ],
  "Aeon Flux": [
    "Aeon Flux"
  ],
  "Akame ga Kill": [
    "Akame",
    "Esdeath",
    "Leone"
  ],
  "Akira": [
    "Kaneda"
  ],
  "Aladdin": [
    "Aladdin",
    "Genie",
    "Jafar",
    "Jasmine"
  ],
  "Alice in Wonderland": [
    "Alice",
    "Cheshire Cat",
    "Mad Hatter (Alice in Wonderland)",
    "Queen of Hearts",
    "White Queen (Alice in Wonderland)",
    "White Rabbit"
  ],
  "Alien": [
    "Ellen Ripley",
    "Vasquez",
    "Xenomorph"
  ],
  "Amagi Brilliant Park": [
    "Isuzu Sento",
    "Latifa Fleuranza",
    "Muse",
    "Salama",
    "Sylphy"
  ],
  "An American Tail": [
    "Fievel Mousekewitz"
  ],
  "Anastasia": [
    "Anastasia",
    "Bartok",
    "Dimitri",
    "Dowager Empress Marie",
    "Rasputin"
  ],
  "Animal Crossing": [
    "Isabelle"
  ],
  "Anne of Green Gables": [
    "Anne of Green Gables"
  ],
  "Arcane": [
    "Silco"
  ],
  "Archer": [
    "Barry Dylan",
    "Cheryl Tunt",
    "Dr. Krieger",
    "Katya Kazanova",
    "Lana Kane",
    "Malory Archer",
    "Pam Poovey",
    "Ray Gillette",
    "Slater (Archer)",
    "Sterling Archer",
    "Woodhouse"
  ],
  "Archie": [
    "Betty Cooper",
    "Sabrina Spellman",
    "Veronica Lodge"
  ],
  "Assassin's Creed": [
    "Ezio Auditore",
    "Kassandra"
  ],
  "Atlantis: The Lost Empire": [
    "Kida"
  ],
  "Attack of the 50 Foot Woman": [
    "The 50 Foot Woman"
  ],
  "Attack on Titan": [
    "Annie Leonhart",
    "Armin Arlert",
    "Eren Yeager",
    "Erwin Smith",
    "Hange Zoe",
    "Historia Reiss",
    "Levi Ackerman",
    "Mikasa Ackerman"
  ],
  "Avatar: The Last Airbender": [
    "Aang",
    "Appa",
    "Azula",
    "Iroh",
    "Katara",
    "Mai (Avatar)",
    "Momo",
    "Sokka",
    "Suki",
    "Toph Beifong",
    "Ty Lee",
    "Zuko"
  ],
  "Back to the Future": [
    "Marty McFly"
  ],
  "Baldur's Gate 3": [
    "Astarion",
    "Karlach",
    "Lae'zel",
    "Minthara",
    "Mizora",
    "Shadowheart"
  ],
  "Barbarella": [
    "Barbarella",
    "The Great Tyrant (Black Queen)"
  ],
  "Barsoom": [
    "Dejah Thoris"
  ],
  "Battlestar Galactica": [
    "Cylon Centurion",
    "Number Six"
  ],
  "Bayonetta": [
    "Bayonetta",
    "Jeanne"
  ],
  "Beauty and the Beast": [
    "Babette",
    "Beast (Beauty and the Beast)",
    "Belle",
    "Gaston",
    "Lumiere"
  ],
  "Beetlejuice": [
    "Beetlejuice",
    "Lydia Deetz"
  ],
  "Ben 10": [
    "Gwen Tennyson"
  ],
  "Berserk": [
    "Casca",
    "Griffith",
    "Guts"
  ],
  "Betty Boop": [
    "Betty Boop"
  ],
  "Big Boy": [
    "Big Boy"
  ],
  "Big Hero 6": [
    "Aunt Cass",
    "Baymax",
    "Go Go Tomago",
    "Hiro Hamada",
    "Honey Lemon"
  ],
  "BioShock": [
    "Big Daddy",
    "Elizabeth (BioShock)",
    "Splicer"
  ],
  "Black Butler": [
    "Ciel Phantomhive",
    "Sebastian Michaelis"
  ],
  "Black Clover": [
    "Noelle Silva"
  ],
  "Black Lagoon": [
    "Balalaika",
    "Revy"
  ],
  "Blade Runner": [
    "Pris",
    "Rachael",
    "Rick Deckard",
    "Roy Batty"
  ],
  "Bleach": [
    "Byakuya Kuchiki",
    "Grimmjow",
    "Ichigo Kurosaki",
    "Kenpachi Zaraki",
    "Nelliel Tu Odelschwanck",
    "Orihime Inoue",
    "Rangiku Matsumoto",
    "Renji Abarai",
    "Rukia Kuchiki",
    "Sosuke Aizen",
    "Tier Harribel",
    "Toshiro Hitsugaya",
    "Yoruichi"
  ],
  "BloodRayne": [
    "Rayne"
  ],
  "Bloodborne": [
    "Lady Maria"
  ],
  "Bob's Burgers": [
    "Bob Belcher",
    "Gene Belcher",
    "Linda Belcher",
    "Louise Belcher",
    "Tina Belcher"
  ],
  "Borderlands": [
    "Amara",
    "Handsome Jack",
    "Lilith (Borderlands)",
    "Mad Moxxi",
    "Psycho (Borderlands)",
    "Sir Hammerlock",
    "Tiny Tina",
    "Zer0"
  ],
  "Brave": [
    "Merida"
  ],
  "Braveheart": [
    "William Wallace"
  ],
  "Buck Rogers": [
    "Princess Ardala",
    "Twiki"
  ],
  "Buffy the Vampire Slayer": [
    "Buffy Summers"
  ],
  "Cap'n Crunch": [
    "Cap'n Crunch"
  ],
  "Captain Planet": [
    "Captain Planet",
    "Captain Pollution",
    "Doctor Blight",
    "Duke Nukem (Captain Planet)",
    "Gaia",
    "Gi",
    "Hoggish Greedly",
    "Kwame",
    "Linka",
    "Looten Plunder",
    "Ma-Ti",
    "Sly Sludge",
    "Verminous Skumm",
    "Wheeler",
    "Zarm"
  ],
  "Carmen Sandiego": [
    "Carmen Sandiego",
    "Coach Brunt",
    "Tigress (Carmen Sandiego)"
  ],
  "Castlevania": [
    "Alucard (Castlevania)",
    "Simon Belmont"
  ],
  "Celeste": [
    "Madeline"
  ],
  "Chainsaw Man": [
    "Aki Hayakawa",
    "Denji",
    "Himeno",
    "Makima",
    "Power (Chainsaw Man)",
    "Quanxi",
    "Reze"
  ],
  "Chaos! Comics": [
    "Lady Death"
  ],
  "Charlie and the Chocolate Factory": [
    "Oompa Loompa",
    "Willy Wonka"
  ],
  "Cheetos": [
    "Chester Cheetah"
  ],
  "Child's Play": [
    "Chucky"
  ],
  "Chip 'n Dale Rescue Rangers": [
    "Gadget Hackwrench"
  ],
  "Chrono Trigger": [
    "Ayla",
    "Crono",
    "Frog",
    "Magus"
  ],
  "Cinderella": [
    "Cinderella",
    "Fairy Godmother",
    "Lady Tremaine"
  ],
  "Clair Obscur: Expedition 33": [
    "Gustave",
    "Lune",
    "Maelle",
    "Sciel"
  ],
  "Clue": [
    "Yvette the Maid"
  ],
  "Coco": [
    "Hector Rivera"
  ],
  "Code Geass": [
    "C.C.",
    "Kallen Stadtfeld",
    "Lelouch vi Britannia",
    "Zero (Code Geass)"
  ],
  "Conan the Barbarian": [
    "Conan the Barbarian"
  ],
  "Cool World": [
    "Detective Frank Harris",
    "Holli Would",
    "Jack Deebs"
  ],
  "Coraline": [
    "Coraline",
    "Other Mother"
  ],
  "Corpse Bride": [
    "Emily (Corpse Bride)"
  ],
  "Cowboy Bebop": [
    "Faye Valentine",
    "Spike Spiegel"
  ],
  "Crash Bandicoot": [
    "Crash Bandicoot"
  ],
  "Crusade Comics": [
    "Shi (Ana Ishikawa)"
  ],
  "Cuphead": [
    "Cuphead"
  ],
  "Cyberpunk 2077": [
    "Johnny Silverhand",
    "Judy Alvarez",
    "Panam Palmer"
  ],
  "Cyberpunk: Edgerunners": [
    "David Martinez",
    "Lucy",
    "Rebecca (Cyberpunk)"
  ],
  "DC": [
    "Alan Scott",
    "Amethyst, Princess of Gemworld",
    "Aquaman",
    "Arisia Rrab",
    "Artemis",
    "Atom Smasher",
    "Atrocitus",
    "Bane",
    "Batgirl",
    "Batman",
    "Batwoman",
    "Big Barda",
    "Bizarro",
    "Black Adam",
    "Black Canary",
    "Black Manta",
    "Blackfire",
    "Bloodsport",
    "Blue Beetle (Jaime Reyes)",
    "Blue Beetle (Ted Kord)",
    "Booster Gold",
    "Brainiac",
    "Brainiac 5",
    "Bruce Wayne",
    "Bumblebee (DC)",
    "Captain Boomerang",
    "Captain Cold",
    "Cassandra Cain",
    "Catwoman",
    "Ch'p",
    "Cheetah",
    "Chemo",
    "Cheshire",
    "Circe",
    "Cosmic Boy",
    "Cyborg",
    "Darkseid",
    "Dawnstar",
    "Deadshot",
    "Deathstroke",
    "Dee Dee",
    "Despero",
    "Doctor Fate",
    "Doctor Mid-Nite",
    "Donna Troy",
    "Dove",
    "Enchantress (Suicide Squad)",
    "Etrigan the Demon",
    "Fatality",
    "Fire",
    "Firestorm",
    "Galatea",
    "Giganta",
    "Golden Glider",
    "Gorilla Grodd",
    "Grace Choi",
    "Granny Goodness",
    "Green Arrow",
    "Green Lantern",
    "Guy Gardner",
    "Gypsy",
    "Hal Jordan",
    "Harley Quinn",
    "Hawk (DC)",
    "Hawkgirl",
    "Hawkman",
    "Hippolyta",
    "Hourman",
    "Huntress",
    "Ice",
    "Jade (Jennifer-Lynn Hayden)",
    "Jay Garrick",
    "Jesse Quick",
    "Jessica Cruz",
    "Jinx (Teen Titans)",
    "John Constantine",
    "John Stewart",
    "Joker",
    "Katana",
    "Katma Tui",
    "Kid Flash",
    "Killer Croc",
    "Killer Frost",
    "Kilowog",
    "King Shark",
    "Kyle Rayner",
    "Lady Shiva",
    "Larfleeze",
    "Lex Luthor",
    "Liberty Belle",
    "Lightning Lad",
    "Livewire",
    "Lobo",
    "Lois Lane",
    "Lyssa Drak",
    "Mad Hatter (Jervis Tetch)",
    "Madame Xanadu",
    "Martian Manhunter",
    "Mary Marvel",
    "Maxima",
    "Mera",
    "Miss Martian",
    "Mr. Freeze",
    "Nightstar",
    "Nightwing",
    "Nubia",
    "Peacemaker",
    "Phantom Lady (Dee Tyler)",
    "Plastic Man",
    "Poison Ivy",
    "Polka-Dot Man",
    "Power Girl",
    "Punchline",
    "Ra's al Ghul",
    "Ratcatcher 2",
    "Red Claw",
    "Red Hood",
    "Reverse-Flash",
    "Rick Flag",
    "Robin",
    "Rose Wilson",
    "Salaak",
    "Sandman (Wesley Dodds)",
    "Saturn Girl",
    "Scarecrow (Batman)",
    "Shazam",
    "Silver Banshee",
    "Sinestro",
    "Star Sapphire",
    "Stargirl",
    "Starman (Ted Knight)",
    "Starro",
    "Starro Spore",
    "Static Shock",
    "Supergirl",
    "Superman",
    "Swamp Thing",
    "Tala",
    "Talia al Ghul",
    "Terra (Teen Titans)",
    "The Atom",
    "The Flash",
    "The Penguin",
    "The Riddler",
    "The Spectre",
    "Thorn",
    "Thunder (Anissa Pierce)",
    "Tomar-Re",
    "Two-Face",
    "Vixen",
    "Waverider",
    "Wildcat",
    "Wonder Girl (Cassie Sandsmark)",
    "Wonder Woman",
    "Zatanna Zatara",
    "Zatara"
  ],
  "DC (Teen Titans)": [
    "Beast Boy",
    "Raven",
    "Starfire"
  ],
  "Dandadan": [
    "Momo Ayase"
  ],
  "Danganronpa": [
    "Junko Enoshima"
  ],
  "Danger Girl": [
    "Abbey Chase",
    "Natalia Kassle",
    "Sydney Savage"
  ],
  "Danny Phantom": [
    "Danny Phantom",
    "Sam Manson"
  ],
  "Dark Souls": [
    "Solaire of Astora"
  ],
  "Darkstalkers": [
    "Anakaris",
    "Baby Bonnie Hood (B.B. Hood)",
    "Bishamon",
    "Demitri Maximoff",
    "Donovan Baine",
    "Felicia",
    "Hsien-Ko",
    "Huitzil",
    "Jedah Dohma",
    "Jon Talbain",
    "Lilith Aensland",
    "Lord Raptor",
    "Morrigan Aensland",
    "Pyron",
    "Q-Bee",
    "Rikuo",
    "Sasquatch",
    "Victor von Gerdenheim"
  ],
  "Darkwing Duck": [
    "Darkwing Duck"
  ],
  "Darling in the Franxx": [
    "Zero Two"
  ],
  "Darna": [
    "Darna"
  ],
  "Date A Live": [
    "Kaguya Yamai",
    "Kotori Itsuka",
    "Kurumi Tokisaki",
    "Miku Izayoi",
    "Mukuro Hoshimiya",
    "Natsumi",
    "Nia Honjo",
    "Origami Tobiichi",
    "Shido Itsuka",
    "Tohka Yatogami",
    "Yoshino",
    "Yuzuru Yamai"
  ],
  "Dead or Alive": [
    "Ayane",
    "Bass Armstrong",
    "Bayman",
    "Christie (Dead or Alive)",
    "Eliot",
    "Hayate",
    "Helena Douglas",
    "Hitomi",
    "Honoka",
    "Jann Lee",
    "Kasumi",
    "Kokoro",
    "Lei Fang",
    "Lisa Hamilton",
    "Marie Rose",
    "Mila",
    "Momiji",
    "Nyotengu",
    "Rachel",
    "Ryu Hayabusa",
    "Tina Armstrong",
    "Zack"
  ],
  "Death Note": [
    "L Lawliet",
    "Light Yagami",
    "Misa Amane",
    "Ryuk"
  ],
  "Delicious in Dungeon": [
    "Marcille Donato"
  ],
  "Demon Slayer": [
    "Akaza",
    "Daki",
    "Giyu Tomioka",
    "Inosuke Hashibira",
    "Kyojuro Rengoku",
    "Mitsuri Kanroji",
    "Muzan Kibutsuji",
    "Nezuko Kamado",
    "Shinobu Kocho",
    "Tanjiro Kamado",
    "Zenitsu Agatsuma"
  ],
  "Despicable Me": [
    "Gru"
  ],
  "Destiny": [
    "Mara Sov"
  ],
  "Devil May Cry": [
    "Dante",
    "Lady (Devil May Cry)",
    "Nero",
    "Trish",
    "Vergil"
  ],
  "Divinity: Original Sin": [
    "Astarte"
  ],
  "Doctor Who": [
    "Cyberman",
    "The Fourth Doctor",
    "The Tenth Doctor",
    "Weeping Angel"
  ],
  "Donkey Kong": [
    "Donkey Kong"
  ],
  "Doom": [
    "Doom Slayer"
  ],
  "Dora the Explorer": [
    "Dora the Explorer"
  ],
  "Dorohedoro": [
    "Nikaido"
  ],
  "Dr. Jekyll and Mr. Hyde": [
    "Dr. Jekyll",
    "Mr. Hyde"
  ],
  "Dr. Seuss": [
    "Horton",
    "The Cat in the Hat",
    "The Grinch",
    "The Lorax"
  ],
  "Dragon Age": [
    "Isabela",
    "Morrigan (Dragon Age)"
  ],
  "Dragon Ball": [
    "Android 17",
    "Android 18",
    "Android 21",
    "Beerus",
    "Broly",
    "Bulma",
    "Cell",
    "Chi-Chi",
    "Frieza",
    "Future Trunks",
    "Gohan",
    "Goku",
    "Krillin",
    "Launch",
    "Majin Buu",
    "Maron",
    "Master Roshi",
    "Piccolo",
    "Vegeta",
    "Videl",
    "Whis"
  ],
  "Dragon's Lair": [
    "Dirk the Daring",
    "Mordroc",
    "Princess Daphne"
  ],
  "DuckTales": [
    "Magica De Spell",
    "Scrooge McDuck"
  ],
  "Duke Nukem": [
    "Duke Nukem (video game)"
  ],
  "Dune": [
    "Lady Jessica",
    "Paul Atreides"
  ],
  "Duolingo": [
    "Duolingo Owl"
  ],
  "Durarara!!": [
    "Celty Sturluson"
  ],
  "Edward Scissorhands": [
    "Edward Scissorhands"
  ],
  "Elden Ring": [
    "Blaidd the Half-Wolf",
    "Malenia, Blade of Miquella",
    "Melina",
    "Queen Marika the Eternal",
    "Ranni the Witch",
    "Rennala, Queen of the Full Moon",
    "Starscourge Radahn"
  ],
  "Encanto": [
    "Bruno Madrigal",
    "Isabela Madrigal",
    "Luisa Madrigal",
    "Mirabel Madrigal"
  ],
  "Energizer": [
    "Energizer Bunny"
  ],
  "Ergo Proxy": [
    "Re-L Mayer"
  ],
  "Escape from New York": [
    "Snake Plissken"
  ],
  "Eureka Seven": [
    "Eureka"
  ],
  "Evil Dead": [
    "Ash Williams"
  ],
  "F-Zero": [
    "Captain Falcon"
  ],
  "FLCL": [
    "Haruko Haruhara"
  ],
  "Fables": [
    "Bloody Mary"
  ],
  "Fairy Tail": [
    "Brandish",
    "Erza Scarlet",
    "Juvia Lockser",
    "Lucy Heartfilia",
    "Mirajane Strauss",
    "Natsu Dragneel"
  ],
  "Fairy Tales": [
    "Gingerbread Man",
    "Goldilocks",
    "Little Red Riding Hood",
    "Thumbelina"
  ],
  "Fallout": [
    "Brotherhood of Steel Knight",
    "Nick Valentine",
    "The Ghoul",
    "Vault Dweller"
  ],
  "Family Guy": [
    "Lois Griffin",
    "Meg Griffin",
    "Peter Griffin",
    "Stewie Griffin"
  ],
  "Fantastic Mr Fox": [
    "Fantastic Mr Fox"
  ],
  "Farscape": [
    "Aeryn Sun",
    "Chiana",
    "Ka D'Argo",
    "Pa'u Zotoh Zhaan",
    "Rygel XVI",
    "Scorpius"
  ],
  "Fate/Grand Order": [
    "Jeanne d'Arc (Fate)",
    "Scathach"
  ],
  "Fate/stay night": [
    "Gilgamesh",
    "Rin Tohsaka",
    "Saber"
  ],
  "Fathom": [
    "Aspen Matthews"
  ],
  "Felix the Cat": [
    "Felix the Cat"
  ],
  "FernGully": [
    "Crysta"
  ],
  "Final Fantasy": [
    "Aerith Gainsborough",
    "Auron",
    "Barret Wallace",
    "Cactuar",
    "Cecil Harvey",
    "Celes Chere",
    "Chocobo",
    "Cloud Strife",
    "Fran",
    "Kain Highwind",
    "Kefka Palazzo",
    "Lightning",
    "Lulu",
    "Moogle",
    "Noctis",
    "Rikku",
    "Rosa Farrell",
    "Rydia",
    "Sephiroth",
    "Squall",
    "Tellah",
    "Terra Branford",
    "Tidus",
    "Tifa Lockhart",
    "Ultros",
    "Vincent Valentine",
    "Vivi Ornitier",
    "Yuffie Kisaragi",
    "Yuna",
    "Zidane"
  ],
  "Fire Emblem": [
    "Azura",
    "Lucina"
  ],
  "Firefly": [
    "Inara Serra",
    "Jayne Cobb",
    "River Tam"
  ],
  "Flash Gordon": [
    "Flash Gordon",
    "General Kala",
    "Klytus",
    "Ming the Merciless",
    "Prince Vultan",
    "Princess Aura"
  ],
  "Folklore": [
    "Baba Yaga",
    "Krampus",
    "Paul Bunyan",
    "Robin Hood",
    "Santa Claus"
  ],
  "Food Wars": [
    "Alice Nakiri",
    "Erina Nakiri",
    "Megumi Tadokoro",
    "Rindou Kobayashi",
    "Soma Yukihira"
  ],
  "Forbidden Planet": [
    "Robby the Robot"
  ],
  "Friday the 13th": [
    "Jason Voorhees"
  ],
  "Frieren: Beyond Journey's End": [
    "Fern",
    "Frieren",
    "Ubel"
  ],
  "Frozen": [
    "Anna",
    "Elsa",
    "Kristoff",
    "Olaf"
  ],
  "Fullmetal Alchemist": [
    "Alphonse Elric",
    "Edward Elric",
    "Greed",
    "King Bradley",
    "Lust",
    "Olivier Armstrong",
    "Riza Hawkeye",
    "Roy Mustang",
    "Scar",
    "Winry Rockbell"
  ],
  "Futurama": [
    "Amy Wong",
    "Bender",
    "Fry",
    "Leela",
    "Professor Farnsworth",
    "Zapp Brannigan",
    "Zoidberg"
  ],
  "Future Diary": [
    "Yuno Gasai"
  ],
  "G.I. Joe": [
    "Baroness",
    "Cobra Commander",
    "Destro",
    "Duke",
    "Scarlett",
    "Snake Eyes",
    "Storm Shadow"
  ],
  "Game of Thrones": [
    "Brienne of Tarth",
    "Cersei Lannister",
    "Daenerys Targaryen",
    "Drogon",
    "Ghost the Direwolf",
    "Jon Snow",
    "Melisandre",
    "The Night King"
  ],
  "Gargoyles": [
    "Goliath"
  ],
  "Geico": [
    "Geico Gecko"
  ],
  "Gen13": [
    "Caitlin Fairchild"
  ],
  "General Mills": [
    "Count Chocula"
  ],
  "Genshin Impact": [
    "Furina",
    "Ganyu",
    "Hu Tao",
    "Kaedehara Kazuha",
    "Raiden Shogun",
    "Tartaglia",
    "Venti",
    "Yae Miko",
    "Zhongli"
  ],
  "Ghost in the Shell": [
    "Motoko Kusanagi"
  ],
  "Ghostbusters": [
    "Ghostbuster",
    "Stay Puft Marshmallow Man"
  ],
  "Gintama": [
    "Kagura"
  ],
  "God of War": [
    "Freya",
    "Kratos"
  ],
  "Godzilla": [
    "Godzilla",
    "King Ghidorah",
    "Mothra"
  ],
  "Golden Kamuy": [
    "Asirpa"
  ],
  "Gravity Falls": [
    "Bill Cipher"
  ],
  "Grease": [
    "Sandy Olsson"
  ],
  "Green Giant": [
    "Jolly Green Giant"
  ],
  "Guilty Gear": [
    "Baiken",
    "Bridget",
    "Dizzy",
    "Elphelt Valentine",
    "I-No",
    "Jack-O' Valentine",
    "Ky Kiske",
    "May (Guilty Gear)",
    "Millia Rage",
    "Sol Badguy",
    "Testament"
  ],
  "Gurren Lagann": [
    "Kamina",
    "Nia Teppelin",
    "Simon",
    "Yoko Littner"
  ],
  "Hades": [
    "Megaera"
  ],
  "Half-Life": [
    "Alyx Vance"
  ],
  "Halloween": [
    "Michael Myers"
  ],
  "Halo": [
    "Cortana",
    "Master Chief"
  ],
  "Harry Potter": [
    "Albus Dumbledore",
    "Aragog",
    "Bellatrix Lestrange",
    "Buckbeak",
    "Draco Malfoy",
    "Fawkes",
    "Fleur Delacour",
    "Ginny Weasley",
    "Harry Potter",
    "Hermione Granger",
    "Lord Voldemort",
    "Luna Lovegood",
    "Minerva McGonagall",
    "Neville Longbottom",
    "Nymphadora Tonks",
    "Ron Weasley",
    "Rubeus Hagrid",
    "Severus Snape",
    "Sirius Black"
  ],
  "Hazbin Hotel": [
    "Alastor"
  ],
  "Heavy Metal": [
    "Julie",
    "Taarna"
  ],
  "Hell's Paradise": [
    "Akaginu",
    "Gabimaru",
    "Yamada Asaemon Sagiri",
    "Yuzuriha"
  ],
  "Hellblade": [
    "Senua"
  ],
  "Hellboy": [
    "Abe Sapien",
    "Hellboy",
    "Liz Sherman"
  ],
  "Hellraiser": [
    "Pinhead"
  ],
  "Hellsing": [
    "Alucard (Hellsing)"
  ],
  "Hercules": [
    "Aphrodite (Hercules)",
    "Hades",
    "Hercules",
    "Megara"
  ],
  "Hey Arnold!": [
    "Arnold",
    "Helga Pataki"
  ],
  "High School DxD": [
    "Akeno Himejima",
    "Asia Argento",
    "Issei Hyoudou",
    "Koneko Toujou",
    "Rias Gremory"
  ],
  "Highschool of the Dead": [
    "Saeko Busujima"
  ],
  "Hitman": [
    "Agent 47"
  ],
  "Hocus Pocus": [
    "Winifred Sanderson"
  ],
  "Hollow Knight": [
    "The Knight (Hollow Knight)"
  ],
  "Horizon": [
    "Aloy"
  ],
  "Hotel Transylvania": [
    "Mavis"
  ],
  "How to Train Your Dragon": [
    "Toothless"
  ],
  "Hunter x Hunter": [
    "Gon Freecss",
    "Hisoka Morow",
    "Kurapika"
  ],
  "IT": [
    "Pennywise"
  ],
  "Image": [
    "Avengelyne",
    "Glory",
    "Lady Supreme",
    "Savage Dragon",
    "Spawn",
    "The Maxx"
  ],
  "Indiana Jones": [
    "Indiana Jones"
  ],
  "Inside Out": [
    "Anger",
    "Joy",
    "Sadness"
  ],
  "Inspector Gadget": [
    "Inspector Gadget"
  ],
  "Inuyasha": [
    "Inuyasha",
    "Kagome Higurashi",
    "Kikyo",
    "Sango"
  ],
  "Invincible": [
    "Allen the Alien",
    "Anissa",
    "Atom Eve",
    "Battle Beast",
    "Dupli-Kate",
    "Invincible",
    "Omni-Man",
    "Rex Splode"
  ],
  "James Bond": [
    "Honey Ryder",
    "James Bond"
  ],
  "Jem and the Holograms": [
    "Jem",
    "Pizzazz"
  ],
  "Jennifer's Body": [
    "Jennifer Check"
  ],
  "JoJo's Bizarre Adventure": [
    "Dio Brando",
    "Giorno Giovanna",
    "Jolyne Cujoh",
    "Joseph Joestar",
    "Josuke Higashikata",
    "Jotaro Kujo",
    "Lisa Lisa"
  ],
  "Johnny Bravo": [
    "Johnny Bravo"
  ],
  "Josie and the Pussycats": [
    "Josie McCoy"
  ],
  "Judge Dredd": [
    "Judge Anderson",
    "Judge Dredd"
  ],
  "Jujutsu Kaisen": [
    "Gojo Satoru",
    "Maki Zenin",
    "Megumi Fushiguro",
    "Nanami Kento",
    "Nobara Kugisaki",
    "Sukuna",
    "Yuji Itadori"
  ],
  "KFC": [
    "Colonel Sanders"
  ],
  "KPop Demon Hunters": [
    "Mira",
    "Rumi",
    "Zoey"
  ],
  "Kabuki": [
    "Kabuki"
  ],
  "Kakegurui": [
    "Yumeko Jabami"
  ],
  "Keebler": [
    "Ernie Keebler"
  ],
  "Kellogg's": [
    "Tony the Tiger"
  ],
  "Kick-Ass": [
    "Hit-Girl"
  ],
  "Kid Icarus": [
    "Palutena"
  ],
  "Kill Bill": [
    "Elle Driver",
    "Gogo Yubari",
    "O-Ren Ishii",
    "The Bride (Beatrix Kiddo)"
  ],
  "Kill la Kill": [
    "Mako Mankanshoku",
    "Nui Harime",
    "Ragyo Kiryuin",
    "Ryuko Matoi",
    "Satsuki Kiryuin"
  ],
  "Kim Possible": [
    "Bonnie Rockwaller",
    "Dr. Drakken",
    "Duff Killigan",
    "Kim Possible",
    "Monkey Fist",
    "Ron Stoppable",
    "Shego"
  ],
  "King Kong": [
    "King Kong"
  ],
  "Kingdom Hearts": [
    "Aqua (Kingdom Hearts)",
    "Axel",
    "Kairi",
    "Riku",
    "Roxas",
    "Sora"
  ],
  "Kirby": [
    "Kirby"
  ],
  "KonoSuba": [
    "Aqua (KonoSuba)",
    "Darkness (KonoSuba)",
    "Kazuma Satou",
    "Megumin"
  ],
  "Kool-Aid": [
    "Kool-Aid Man"
  ],
  "Labyrinth": [
    "Jareth the Goblin King",
    "Sarah Williams"
  ],
  "League of Legends": [
    "Ahri",
    "Akali",
    "Ambessa",
    "Brand",
    "Briar",
    "Caitlyn",
    "Dr. Mundo",
    "Ekko",
    "Elise",
    "Evelynn",
    "Gwen (League of Legends)",
    "Illaoi",
    "Irelia",
    "Janna",
    "Jax",
    "Jhin",
    "Jinx (League of Legends)",
    "Kai'Sa",
    "Katarina",
    "Leona (League of Legends)",
    "Lux",
    "Mel Medarda",
    "Miss Fortune",
    "Morgana",
    "Neeko",
    "Nidalee",
    "Pyke",
    "Seraphine",
    "Sett",
    "Sona",
    "Teemo",
    "Thresh",
    "Vi",
    "Yasuo",
    "Yone",
    "Yunara",
    "Zeri",
    "Zilean",
    "Zyra"
  ],
  "Legend": [
    "King Arthur",
    "Merlin"
  ],
  "Lilo and Stitch": [
    "Lilo",
    "Nani Pelekai",
    "Stitch"
  ],
  "Literature": [
    "Curious George",
    "Paddington Bear"
  ],
  "Little House on the Prairie": [
    "Laura Ingalls"
  ],
  "Little Nightmares": [
    "Six"
  ],
  "LittleBigPlanet": [
    "Sackboy"
  ],
  "Lollipop Chainsaw": [
    "Cordelia Starling",
    "Juliet Starling",
    "Nick Carlyle",
    "Rosalind Starling"
  ],
  "Looney Tunes": [
    "Bugs Bunny",
    "Daffy Duck",
    "Elmer Fudd",
    "Foghorn Leghorn",
    "Lola Bunny",
    "Marvin the Martian",
    "Porky Pig",
    "Road Runner",
    "Speedy Gonzales",
    "Sylvester",
    "Tasmanian Devil",
    "Tweety",
    "Wile E. Coyote",
    "Yosemite Sam"
  ],
  "Lupin III": [
    "Fujiko Mine"
  ],
  "Mad Max": [
    "Immortan Joe",
    "Imperator Furiosa",
    "Mad Max"
  ],
  "Madoka Magica": [
    "Homura Akemi (Devil)",
    "Kyoko Sakura",
    "Madoka Kaname (Ultimate)",
    "Mami Tomoe",
    "Sayaka Miki"
  ],
  "Magi": [
    "Morgiana"
  ],
  "Magic: The Gathering": [
    "Liliana Vess"
  ],
  "Mars Attacks!": [
    "The Martian Ambassador"
  ],
  "Marvel": [
    "Abomination",
    "Agatha Harkness",
    "Aleta Ogord",
    "America Chavez",
    "Angel",
    "Angela",
    "Ant-Man",
    "Apocalypse",
    "Banshee",
    "Baron Zemo",
    "Beast (X-Men)",
    "Big Bertha",
    "Binary",
    "Bishop",
    "Black Bolt",
    "Black Cat",
    "Black Mamba",
    "Black Panther",
    "Black Widow",
    "Blackheart",
    "Blade",
    "Blink",
    "Bullseye",
    "Cable",
    "Captain America",
    "Captain Carter",
    "Captain Marvel",
    "Carnage",
    "Colossus",
    "Crystal",
    "Cyclops",
    "Daredevil",
    "Dazzler",
    "Deadpool",
    "Doctor Doom",
    "Doctor Octopus",
    "Doctor Strange",
    "Domino",
    "Drax",
    "Electro",
    "Elektra",
    "Emma Frost",
    "Enchantress (Marvel)",
    "Falcon",
    "Firestar",
    "Galactus",
    "Gambit",
    "Gamora",
    "Ghost Rider",
    "Giant-Man",
    "Green Goblin",
    "Groot",
    "Hawkeye",
    "Hela",
    "Hellcat",
    "Hulk",
    "Human Torch",
    "Iceman",
    "Invisible Woman",
    "Iron Fist",
    "Iron Man",
    "J. Jonah Jameson",
    "Jane Foster Thor",
    "Jean Grey",
    "Jubilee",
    "Juggernaut",
    "Julia Carpenter",
    "Justice (New Warriors)",
    "Kang the Conqueror",
    "Kingpin",
    "Kitty Pryde",
    "Kraven the Hunter",
    "Krystalin",
    "La Lunatica",
    "Lady Sif",
    "Lascivious",
    "Loki",
    "Lorelei (Asgardian)",
    "Luke Cage",
    "Magik",
    "Magma",
    "Magneto",
    "Mantis",
    "Mary Jane Watson",
    "Medusa",
    "Mister Fantastic",
    "Mister Sinister",
    "Mistress Death",
    "Misty Knight",
    "Mockingbird",
    "Moon Knight",
    "Moondragon",
    "Moonstone",
    "Morgan le Fay",
    "Ms. Marvel (Kamala Khan)",
    "Ms. Marvel (Sharon Ventura)",
    "Mysterio",
    "Mystique",
    "Namor",
    "Namora",
    "Namorita",
    "Nebula",
    "Nick Fury",
    "Nico Minoru",
    "Night Thrasher",
    "Nightcrawler",
    "Nocturne",
    "Nova (Frankie Raye)",
    "Nova (Richard Rider)",
    "Okoye",
    "Peggy Carter",
    "Photon (Monica Rambeau)",
    "Polaris",
    "Professor X",
    "Psylocke",
    "Punisher",
    "Pyro",
    "Quasar",
    "Quicksilver",
    "Rachel Summers",
    "Rage (Marvel)",
    "Red Skull",
    "Rhino",
    "Rocket Raccoon",
    "Rogue",
    "Sabretooth",
    "Sandman (Spider-Man)",
    "Satana",
    "Scarlet Witch",
    "Sebastian Shaw",
    "Selene Gallio (Black Queen)",
    "Sersi",
    "Shanna the She-Devil",
    "Sharon Carter",
    "She-Hulk",
    "Shriek",
    "Shuri",
    "Silk",
    "Silver Sable",
    "Silver Surfer",
    "Snowbird",
    "Songbird",
    "Spectrum",
    "Speedball",
    "Spider-Gwen",
    "Spider-Man",
    "Spider-Woman",
    "Spider-Woman (Julia Carpenter)",
    "Spiral",
    "Squirrel Girl",
    "Star-Lord",
    "Stature",
    "Storm",
    "Sunfire (Exiles)",
    "Taskmaster",
    "Thanos",
    "The Thing",
    "Thor",
    "Tigra",
    "Titania",
    "Tony Stark",
    "Typhoid Mary",
    "Ultron",
    "Valkyrie",
    "Venom",
    "Venus (Marvel)",
    "Viper",
    "Vision",
    "Vulture",
    "War Machine",
    "Wasp",
    "White Widow",
    "Winter Soldier",
    "Wolverine",
    "X-23",
    "Yelena Belova",
    "Yondu"
  ],
  "Mary Poppins": [
    "Mary Poppins"
  ],
  "Mass Effect": [
    "Commander Shepard",
    "Garrus Vakarian",
    "Jack (Mass Effect)",
    "Liara T'Soni",
    "Miranda Lawson",
    "Mordin Solus",
    "Tali'Zorah",
    "Urdnot Wrex"
  ],
  "Masters of the Universe": [
    "Beast Man",
    "Evil-Lyn",
    "He-Man",
    "Man-At-Arms",
    "Orko",
    "Ram-Man",
    "She-Ra",
    "Skeletor",
    "Sorceress",
    "Teela"
  ],
  "McDonald's": [
    "Grimace",
    "Hamburglar",
    "Mayor McCheese",
    "Ronald McDonald"
  ],
  "Medaka Box": [
    "Medaka Kurokami"
  ],
  "Mega Man": [
    "Mega Man"
  ],
  "Metal Gear": [
    "Quiet",
    "Solid Snake"
  ],
  "Metroid": [
    "Samus Aran (Power Suit)",
    "Zero Suit Samus"
  ],
  "Metropolis": [
    "Maria (Metropolis)"
  ],
  "Michelin": [
    "Michelin Man"
  ],
  "Michiko & Hatchin": [
    "Michiko Malandro"
  ],
  "Mickey Mouse & Friends": [
    "Daisy Duck",
    "Donald Duck",
    "Goofy",
    "Mickey Mouse",
    "Minnie Mouse"
  ],
  "Miraculous Ladybug": [
    "Bunnyx",
    "Carapace",
    "Cat Noir",
    "Hawk Moth",
    "King Monkey",
    "Ladybug",
    "Mayura",
    "Pegasus",
    "Queen Bee",
    "Rena Rouge",
    "Ryuko",
    "Viperion"
  ],
  "Mirror's Edge": [
    "Faith Connors"
  ],
  "Mistress of the Dark": [
    "Elvira"
  ],
  "Moana": [
    "Maui",
    "Moana"
  ],
  "Mobile Suit Gundam": [
    "Char Aznable"
  ],
  "Monogatari": [
    "Hitagi Senjougahara",
    "Kiss-Shot Acerola-Orion Heart-Under-Blade"
  ],
  "Monster High": [
    "Abbey Bominable",
    "Frankie Stein"
  ],
  "Monsters vs. Aliens": [
    "Ginormica"
  ],
  "Mortal Kombat": [
    "Baraka",
    "Cassie Cage",
    "Cetrion",
    "D'Vorah",
    "Ermac",
    "Frost",
    "Goro",
    "Jade (Mortal Kombat)",
    "Johnny Cage",
    "Kabal",
    "Kano",
    "Kitana",
    "Kung Lao",
    "Liu Kang",
    "Mileena",
    "Quan Chi",
    "Raiden",
    "Reptile",
    "Scorpion",
    "Shang Tsung",
    "Shao Kahn",
    "Sheeva",
    "Sindel",
    "Skarlet",
    "Smoke",
    "Sonya Blade",
    "Sub-Zero",
    "Tanya"
  ],
  "Mr. Clean": [
    "Mr. Clean"
  ],
  "Mulan": [
    "Mulan"
  ],
  "My Dress-Up Darling": [
    "Marin Kitagawa"
  ],
  "My Hero Academia": [
    "All Might",
    "Bakugo",
    "Dabi",
    "Deku",
    "Endeavor",
    "Eraser Head",
    "Hawks",
    "Himiko Toga",
    "Midnight (My Hero Academia)",
    "Mirko",
    "Momo Yaoyorozu",
    "Mt. Lady",
    "Nejire Hado",
    "Ochaco Uraraka",
    "Shoto Todoroki",
    "Tomura Shigaraki",
    "Tsuyu Asui"
  ],
  "My Life as a Teenage Robot": [
    "Jenny Wakeman"
  ],
  "Nana": [
    "Nana Osaki"
  ],
  "Nancy Drew": [
    "Nancy Drew"
  ],
  "Naruto": [
    "Gaara",
    "Hinata Hyuga",
    "Ino Yamanaka",
    "Itachi Uchiha",
    "Jiraiya",
    "Kakashi Hatake",
    "Konan",
    "Madara Uchiha",
    "Mei Terumi",
    "Might Guy",
    "Minato Namikaze",
    "Naruto Uzumaki",
    "Orochimaru",
    "Pain (Nagato)",
    "Rock Lee",
    "Sakura Haruno",
    "Sasuke Uchiha",
    "Shikamaru Nara",
    "Temari",
    "Tsunade"
  ],
  "Neon Genesis Evangelion": [
    "Asuka Langley Soryu",
    "Misato Katsuragi",
    "Rei Ayanami",
    "Shinji Ikari"
  ],
  "Nickelodeon": [
    "Mr. Krabs",
    "Patrick Star",
    "Plankton",
    "Sandy Cheeks",
    "SpongeBob SquarePants",
    "Squidward"
  ],
  "NieR": [
    "Kaine"
  ],
  "NieR: Automata": [
    "2B",
    "A2"
  ],
  "Noragami": [
    "Bishamonten"
  ],
  "Oh My Goddess!": [
    "Belldandy",
    "Urd"
  ],
  "One Piece": [
    "Boa Hancock",
    "Brook",
    "Charlotte Smoothie",
    "Donquixote Doflamingo",
    "Franky",
    "Monkey D. Luffy",
    "Nami",
    "Nico Robin",
    "Portgas D. Ace",
    "Roronoa Zoro",
    "Sanji",
    "Shanks",
    "Shirahoshi",
    "Trafalgar Law",
    "Usopp"
  ],
  "One Punch Man": [
    "Captain Mizuki",
    "Fubuki (One Punch Man)",
    "Garou",
    "Genos",
    "Mumen Rider",
    "Saitama",
    "Tatsumaki"
  ],
  "Oshi no Ko": [
    "Ai Hoshino"
  ],
  "Overlord": [
    "Ainz Ooal Gown",
    "Albedo (Overlord)",
    "Shalltear Bloodfallen"
  ],
  "Overwatch": [
    "Ana",
    "Ashe (Overwatch)",
    "Brigitte",
    "D.Va",
    "Doomfist",
    "Genji",
    "Hanzo",
    "Junker Queen",
    "Junkrat",
    "Kiriko",
    "Mei",
    "Mercy",
    "Moira",
    "Pharah",
    "Reaper",
    "Reinhardt",
    "Soldier 76",
    "Sombra",
    "Symmetra",
    "Tracer",
    "Widowmaker",
    "Zarya"
  ],
  "Pac-Man": [
    "Pac-Man"
  ],
  "Panty & Stocking with Garterbelt": [
    "Panty Anarchy",
    "Stocking Anarchy"
  ],
  "Peanuts": [
    "Charlie Brown"
  ],
  "Peepoodo": [
    "Dr. Monique Pussycat"
  ],
  "Penny Dreadful": [
    "Vanessa Ives"
  ],
  "Persona": [
    "Aigis",
    "Ann Takamaki",
    "Futaba Sakura",
    "Haru Okumura",
    "Joker (Persona)",
    "Makoto Niijima",
    "Mitsuru Kirijo",
    "Naoto Shirogane",
    "Sumire Yoshizawa"
  ],
  "Peter Pan": [
    "Captain Hook",
    "Peter Pan",
    "Tinker Bell",
    "Wendy Darling"
  ],
  "Pikmin": [
    "Captain Olimar"
  ],
  "Pillsbury": [
    "Pillsbury Doughboy"
  ],
  "Pinocchio": [
    "Jiminy Cricket",
    "Pinocchio"
  ],
  "Pippi Longstocking": [
    "Pippi Longstocking"
  ],
  "Pirates of the Caribbean": [
    "Calypso (Tia Dalma)",
    "Davy Jones",
    "Elizabeth Swann",
    "Hector Barbossa",
    "Jack Sparrow",
    "Will Turner"
  ],
  "Planters": [
    "Mr. Peanut"
  ],
  "Pocahontas": [
    "Pocahontas"
  ],
  "Pokemon": [
    "Arcanine",
    "Ash Ketchum",
    "Bea (Pokemon)",
    "Brock",
    "Bulbasaur",
    "Charizard",
    "Cynthia",
    "Dawn",
    "Eevee",
    "Elesa",
    "Gary Oak",
    "Gengar",
    "Gyarados",
    "Iris",
    "James (Team Rocket)",
    "Jessie (Team Rocket)",
    "Jigglypuff",
    "Lapras",
    "Leon (Pokemon)",
    "Lillie",
    "Lucario",
    "Marnie",
    "May",
    "Meowth",
    "Mewtwo",
    "Misty",
    "Nemona",
    "Nurse Joy",
    "Officer Jenny",
    "Pikachu",
    "Psyduck",
    "Red (Pokemon)",
    "Serena",
    "Snorlax",
    "Squirtle"
  ],
  "Popeye": [
    "Bluto",
    "Olive Oyl",
    "Popeye"
  ],
  "Portal": [
    "Chell",
    "GLaDOS"
  ],
  "Predator": [
    "Predator"
  ],
  "Prison School": [
    "Hana Midorikawa",
    "Kate Takenomiya",
    "Mari Kurihara",
    "Meiko Shiraki"
  ],
  "Pulp Fiction": [
    "Mia Wallace"
  ],
  "Rainbow Brite": [
    "Rainbow Brite"
  ],
  "Rambo": [
    "Rambo"
  ],
  "Ranma 1/2": [
    "Ranma Saotome"
  ],
  "Rascal Does Not Dream of Bunny Girl Senpai": [
    "Mai Sakurajima"
  ],
  "Ratchet & Clank": [
    "Rivet"
  ],
  "Re:Zero": [
    "Emilia",
    "Ram",
    "Rem",
    "Subaru Natsuki"
  ],
  "Record of Ragnarok": [
    "Aphrodite (Record of Ragnarok)",
    "Brunhilde",
    "Buddha (Record of Ragnarok)",
    "Jack the Ripper (Record of Ragnarok)",
    "Lu Bu",
    "Shiva (Record of Ragnarok)"
  ],
  "Red Alert": [
    "Yuri"
  ],
  "Red Dead Redemption": [
    "Arthur Morgan",
    "Sadie Adler"
  ],
  "Red Sonja": [
    "Red Sonja"
  ],
  "Remember Me": [
    "Nilin"
  ],
  "Rent-a-Girlfriend": [
    "Chizuru Mizuhara"
  ],
  "Resident Evil": [
    "Ada Wong",
    "Albert Wesker",
    "Chris Redfield",
    "Claire Redfield",
    "Jill Valentine",
    "Lady Dimitrescu",
    "Leon S. Kennedy",
    "Nemesis"
  ],
  "Rick and Morty": [
    "Morty Smith",
    "Rick Sanchez",
    "Summer Smith"
  ],
  "Rise of the Guardians": [
    "Jack Frost"
  ],
  "Robin Hood (1973)": [
    "Maid Marian"
  ],
  "RoboCop": [
    "RoboCop"
  ],
  "Rosario + Vampire": [
    "Moka Akashiya"
  ],
  "Rugrats": [
    "Reptar"
  ],
  "Sailor Moon": [
    "Luna (Sailor Moon)",
    "Queen Beryl",
    "Sailor Jupiter",
    "Sailor Mars",
    "Sailor Mercury",
    "Sailor Moon",
    "Sailor Neptune",
    "Sailor Pluto",
    "Sailor Saturn",
    "Sailor Uranus",
    "Sailor Venus",
    "Tuxedo Mask"
  ],
  "Samurai Jack": [
    "Samurai Jack"
  ],
  "Samurai Shodown": [
    "Nakoruru"
  ],
  "Scooby-Doo": [
    "Daphne Blake",
    "Fred Jones",
    "Shaggy",
    "Velma Dinkley"
  ],
  "Scott Pilgrim": [
    "Ramona Flowers"
  ],
  "Scream": [
    "Ghostface"
  ],
  "Sheena, Queen of the Jungle": [
    "Sheena"
  ],
  "Sherlock Holmes": [
    "Sherlock Holmes"
  ],
  "Shrek": [
    "Lord Farquaad",
    "Princess Fiona",
    "Puss in Boots",
    "Shrek"
  ],
  "Silent Hill": [
    "Nurse (Silent Hill)",
    "Pyramid Head"
  ],
  "Sin City": [
    "Marv"
  ],
  "Sinbad: Legend of the Seven Seas": [
    "Eris",
    "Sinbad"
  ],
  "Sleeping Beauty": [
    "Aurora",
    "Maleficent"
  ],
  "Snow White": [
    "Evil Queen",
    "Snow White"
  ],
  "Solo Leveling": [
    "Cha Hae-in",
    "Sung Jinwoo"
  ],
  "Sonic the Hedgehog": [
    "Amy Rose",
    "Dr. Eggman",
    "Rouge the Bat",
    "Sonic the Hedgehog"
  ],
  "Soul Calibur": [
    "Astaroth",
    "Cassandra Alexandra",
    "Cervantes de Leon",
    "Heishiro Mitsurugi",
    "Ivy Valentine",
    "Kilik",
    "Li Long",
    "Maxi",
    "Rock Adams",
    "Seong Mi-na",
    "Siegfried Schtauffen",
    "Sophitia Alexandra",
    "Taki",
    "Voldo",
    "Xianghua",
    "Yoshimitsu"
  ],
  "Soul Eater": [
    "Maka Albarn"
  ],
  "South Park": [
    "Eric Cartman",
    "Kenny McCormick",
    "Kyle Broflovski",
    "Stan Marsh"
  ],
  "Space Ace": [
    "Commander Borf",
    "Kimberly (Space Ace)",
    "Space Ace"
  ],
  "Speed Racer": [
    "Speed Racer"
  ],
  "Spice and Wolf": [
    "Holo"
  ],
  "Spy x Family": [
    "Loid Forger",
    "Yor Forger"
  ],
  "Spyro": [
    "Elora"
  ],
  "Squid Game": [
    "Front Man",
    "Pink Guard",
    "Seong Gi-hun"
  ],
  "Star Fox": [
    "Fox McCloud"
  ],
  "Star Trek": [
    "Andorian",
    "Borg Drone",
    "Captain Janeway",
    "Captain Kirk",
    "Captain Picard",
    "Cardassian",
    "Data",
    "Deanna Troi",
    "Dr. McCoy",
    "Ferengi",
    "Geordi La Forge",
    "Gowron",
    "Ilia",
    "Klingon",
    "Mr. Spock",
    "Seven of Nine",
    "Tellarite",
    "Uhura",
    "Vulcan",
    "Worf"
  ],
  "Star Wars": [
    "2-1B Droid",
    "4-LOM",
    "Aayla Secura",
    "Admiral Ackbar",
    "Ahsoka Tano",
    "Anakin Skywalker",
    "Asajj Ventress",
    "Aurra Sing",
    "BB-8",
    "Bantha",
    "Barriss Offee",
    "Battle Droid",
    "Bib Fortuna",
    "Bo-Katan Kryze",
    "Boba Fett",
    "Bossk",
    "Bothan",
    "C-3PO",
    "Cad Bane",
    "Cal Kestis",
    "Captain Phasma",
    "Captain Rex",
    "Cassian Andor",
    "Chewbacca",
    "Chief Chirpa",
    "Chopper",
    "Constable Zuvio",
    "Count Dooku",
    "Dark Trooper",
    "Darth Maul",
    "Darth Revan",
    "Darth Talon",
    "Darth Vader",
    "Dathomirian",
    "Death Trooper",
    "Dengar",
    "Devaronian",
    "Dexter Jettster",
    "Doctor Cornelius Evazan",
    "Duros",
    "Emperor Palpatine",
    "Figrin D'an",
    "Finn",
    "General Grievous",
    "Gonk Droid",
    "Gran",
    "Grand Admiral Thrawn",
    "Grand Inquisitor",
    "Greedo",
    "Greez Dritus",
    "Grogu",
    "Han Solo",
    "Hera Syndulla",
    "Hondo Ohnaka",
    "IG-88",
    "Imperial Officer",
    "Imperial Royal Guard",
    "Ithorian",
    "Jabba the Hutt",
    "Jango Fett",
    "Jar Jar Binks",
    "Jawa",
    "Jyn Erso",
    "K-2SO",
    "Kaminoan",
    "Ki-Adi-Mundi",
    "Kuiil",
    "Kylo Ren",
    "Lando Calrissian",
    "Lobot",
    "Loth-Cat",
    "Luke Skywalker",
    "Luminara Unduli",
    "Mace Windu",
    "Mara Jade",
    "Max Rebo",
    "Maz Kanata",
    "Mon Mothma",
    "Mynock",
    "Nien Nunb",
    "Nute Gunray",
    "Obi-Wan Kenobi",
    "Obi-Wan Kenobi (Force Ghost)",
    "Oola",
    "Padme Amidala",
    "Plo Koon",
    "Poe Dameron",
    "Ponda Baba",
    "Porg",
    "Praetorian Guard",
    "Princess Leia Organa",
    "Qui-Gon Jinn",
    "R2-D2",
    "Rancor",
    "Rey",
    "Sabine Wren",
    "Salacious Crumb",
    "Saw Gerrera",
    "Scout Trooper",
    "Sebulba",
    "Shaak Ti",
    "Snowtrooper",
    "Stormtrooper",
    "TIE Pilot",
    "Tauntaun",
    "The Mandalorian",
    "Tusken Raider",
    "Unkar Plutt",
    "Vette",
    "Wampa",
    "Watto",
    "Wedge Antilles",
    "Wicket the Ewok",
    "Yoda",
    "Zeb Orrelios",
    "Zorii Bliss",
    "Zuckuss"
  ],
  "Star vs. the Forces of Evil": [
    "Star Butterfly"
  ],
  "StarCraft": [
    "Nova Terra",
    "Sarah Kerrigan"
  ],
  "Steins;Gate": [
    "Makise Kurisu"
  ],
  "Steven Universe": [
    "Amethyst (Steven Universe)",
    "Garnet",
    "Lapis Lazuli",
    "Pearl",
    "Peridot",
    "Rose Quartz",
    "Spinel",
    "Steven Universe",
    "Topaz"
  ],
  "Stranger Things": [
    "Eleven"
  ],
  "Strawberry Shortcake": [
    "Strawberry Shortcake"
  ],
  "Street Fighter": [
    "AKI",
    "Akuma",
    "Blanka",
    "Cammy White",
    "Chun-Li",
    "Crimson Viper",
    "Dhalsim",
    "E. Honda",
    "Elena",
    "Guile",
    "Juri Han",
    "Ken Masters",
    "Kimberly Jackson",
    "Laura Matsuda",
    "Lily",
    "M. Bison",
    "Maki Genryusai",
    "Manon",
    "Marisa",
    "Menat",
    "Poison",
    "Rainbow Mika",
    "Ryu",
    "Sagat",
    "Sakura Kasugano",
    "Vega",
    "Zangief"
  ],
  "Stripperella": [
    "Stripperella"
  ],
  "Studio Ghibli": [
    "Arrietty Clock",
    "Baron Humbert von Gikkingen",
    "Catbus",
    "Haku (dragon form)",
    "Howl",
    "Kaguya",
    "Kiki",
    "Nausicaa",
    "No-Face",
    "Porco Rosso",
    "Princess Mononoke",
    "Totoro"
  ],
  "Super Mario": [
    "Bowser",
    "Daisy",
    "Luigi",
    "Mario",
    "Pauline",
    "Princess Peach",
    "Rosalina",
    "Toad",
    "Waluigi",
    "Wario",
    "Yoshi"
  ],
  "Sword Art Online": [
    "Asuna Yuuki",
    "Kirito",
    "Leafa",
    "Sinon"
  ],
  "System Shock": [
    "SHODAN"
  ],
  "TMNT": [
    "April O'Neil",
    "Casey Jones",
    "Donatello",
    "Karai",
    "Leonardo",
    "Michelangelo",
    "Raphael",
    "Shredder",
    "Splinter"
  ],
  "Tangled": [
    "Flynn Rider",
    "Rapunzel"
  ],
  "Tank Girl": [
    "Tank Girl"
  ],
  "Tarzan": [
    "Jane Porter",
    "Tarzan"
  ],
  "Team Fortress 2": [
    "Demoman (Team Fortress 2)",
    "Engineer (Team Fortress 2)",
    "Heavy (Team Fortress 2)",
    "Medic (Team Fortress 2)",
    "Pyro (Team Fortress 2)",
    "Sniper (Team Fortress 2)",
    "Spy (Team Fortress 2)"
  ],
  "Tekken": [
    "Anna Williams",
    "Asuka Kazama",
    "Christie Monteiro",
    "Heihachi Mishima",
    "Hwoarang",
    "Jin Kazama",
    "Jun Kazama",
    "Kazuya Mishima",
    "King",
    "Lili",
    "Ling Xiaoyu",
    "Nina Williams",
    "Paul Phoenix",
    "Zafina"
  ],
  "That Time I Got Reincarnated as a Slime": [
    "Milim Nava"
  ],
  "The 100": [
    "Lexa"
  ],
  "The Addams Family": [
    "Cousin Itt",
    "Gomez Addams",
    "Lurch",
    "Morticia Addams",
    "Uncle Fester",
    "Wednesday Addams"
  ],
  "The Apothecary Diaries": [
    "Maomao"
  ],
  "The BFG": [
    "The BFG"
  ],
  "The Big Lebowski": [
    "The Dude"
  ],
  "The Boys": [
    "A-Train",
    "Billy Butcher",
    "Black Noir",
    "Crimson Countess",
    "Firecracker",
    "Homelander",
    "Mother's Milk",
    "Queen Maeve",
    "Sister Sage",
    "Soldier Boy",
    "Starlight",
    "The Deep"
  ],
  "The Brady Bunch": [
    "Marcia Brady"
  ],
  "The Citadel": [
    "The Martyr"
  ],
  "The Craft": [
    "Nancy Downs"
  ],
  "The Crow": [
    "Eric Draven"
  ],
  "The Emperor's New Groove": [
    "Yzma"
  ],
  "The Fifth Element": [
    "Diva Plavalaguna",
    "Leeloo",
    "Ruby Rhod",
    "Zorg"
  ],
  "The Flintstones": [
    "Bamm-Bamm Rubble",
    "Barney Rubble",
    "Betty Rubble",
    "Fred Flintstone",
    "Pebbles Flintstone",
    "The Great Gazoo",
    "Wilma Flintstone"
  ],
  "The Girl with the Dragon Tattoo": [
    "Lisbeth Salander"
  ],
  "The Hunchback of Notre Dame": [
    "Esmeralda",
    "Frollo",
    "Quasimodo"
  ],
  "The Hunger Games": [
    "Katniss Everdeen"
  ],
  "The Incredibles": [
    "Dash",
    "Edna Mode",
    "Elastigirl",
    "Frozone",
    "Mr. Incredible",
    "Syndrome",
    "Violet"
  ],
  "The Iron Giant": [
    "The Iron Giant"
  ],
  "The Jetsons": [
    "Elroy Jetson",
    "George Jetson",
    "Jane Jetson",
    "Judy Jetson",
    "Mr. Spacely",
    "Rosie the Robot"
  ],
  "The King of Fighters": [
    "Athena Asamiya",
    "Iori Yagami",
    "K'",
    "Kyo Kusanagi",
    "Leona Heidern",
    "Mai Shiranui",
    "Terry Bogard"
  ],
  "The Last of Us": [
    "Ellie Williams",
    "Joel Miller"
  ],
  "The Legend of Korra": [
    "Asami Sato",
    "Korra"
  ],
  "The Legend of Zelda": [
    "Ganondorf",
    "Impa",
    "Link",
    "Midna",
    "Mipha",
    "Sheik",
    "Urbosa",
    "Zelda"
  ],
  "The Little Mermaid": [
    "Ariel",
    "Prince Eric",
    "Ursula"
  ],
  "The Lord of the Rings": [
    "Aragorn",
    "Arwen",
    "Bilbo Baggins",
    "Boromir",
    "Eowyn",
    "Fell Beast",
    "Frodo Baggins",
    "Galadriel",
    "Gandalf",
    "Gimli",
    "Gollum",
    "Legolas",
    "Samwise Gamgee",
    "Saruman",
    "Sauron",
    "Shelob",
    "Tauriel",
    "Witch-King of Angmar"
  ],
  "The Mask": [
    "The Mask"
  ],
  "The Matrix": [
    "Agent Smith",
    "Morpheus (The Matrix)",
    "Neo",
    "Trinity"
  ],
  "The NeverEnding Story": [
    "Falkor"
  ],
  "The Nightmare Before Christmas": [
    "Jack Skellington",
    "Oogie Boogie",
    "Sally"
  ],
  "The Owl House": [
    "Eda Clawthorne"
  ],
  "The Partridge Family": [
    "Laurie Partridge"
  ],
  "The Phantom": [
    "The Phantom"
  ],
  "The Powerpuff Girls": [
    "Blossom",
    "Bubbles",
    "Buttercup",
    "Mojo Jojo"
  ],
  "The Princess and the Frog": [
    "Dr. Facilier",
    "Tiana"
  ],
  "The Ring": [
    "Samara"
  ],
  "The Rising of the Shield Hero": [
    "Raphtalia"
  ],
  "The Road to El Dorado": [
    "Chel",
    "Miguel",
    "Tulio",
    "Tzekel-Kan"
  ],
  "The Rocketeer": [
    "The Rocketeer"
  ],
  "The Rocky Horror Picture Show": [
    "Columbia",
    "Dr. Frank-N-Furter",
    "Magenta",
    "Riff Raff"
  ],
  "The Sandman": [
    "Death of the Endless",
    "Delirium",
    "Desire of the Endless",
    "Despair of the Endless",
    "Destiny of the Endless",
    "Destruction of the Endless",
    "Dream of the Endless"
  ],
  "The Seven Deadly Sins": [
    "Diane",
    "Elizabeth Liones",
    "Meliodas"
  ],
  "The Shadow": [
    "The Shadow"
  ],
  "The Simpsons": [
    "Bart Simpson",
    "Homer Simpson",
    "Krusty the Clown",
    "Lisa Simpson",
    "Marge Simpson",
    "Mr. Burns",
    "Ned Flanders",
    "Sideshow Bob"
  ],
  "The Smurfs": [
    "Gargamel",
    "Papa Smurf",
    "Smurfette"
  ],
  "The Spirit": [
    "The Spirit"
  ],
  "The Terminator": [
    "Sarah Connor",
    "The Terminator"
  ],
  "The Texas Chain Saw Massacre": [
    "Leatherface"
  ],
  "The Tick": [
    "The Tick"
  ],
  "The Toxic Avenger": [
    "The Toxic Avenger"
  ],
  "The Venture Bros": [
    "Dr. Mrs. The Monarch",
    "The Monarch",
    "Triana Orpheus"
  ],
  "The Walking Dead": [
    "Michonne"
  ],
  "The Witcher": [
    "Ciri",
    "Geralt of Rivia",
    "Triss Merigold",
    "Yennefer of Vengerberg"
  ],
  "The Wizard of Oz": [
    "Cowardly Lion",
    "Dorothy Gale",
    "Glinda",
    "Scarecrow (Wizard of Oz)",
    "Tin Man",
    "Wicked Witch of the West"
  ],
  "Thunderbirds": [
    "Lady Penelope"
  ],
  "Thundercats": [
    "Cheetara",
    "Lion-O",
    "Mumm-Ra",
    "Panthro",
    "Tygra"
  ],
  "Tokyo Ghoul": [
    "Ken Kaneki",
    "Rize Kamishiro",
    "Touka Kirishima"
  ],
  "Tomb Raider": [
    "Lara Croft"
  ],
  "Top Cow": [
    "Aphrodite IX",
    "Cyblade",
    "The Darkness (Jackie Estacado)",
    "Velocity"
  ],
  "Toy Story": [
    "Bo Peep",
    "Buzz Lightyear",
    "Jessie (Toy Story)",
    "Woody"
  ],
  "Transformers": [
    "Bumblebee (Transformers)",
    "Megatron",
    "Optimus Prime",
    "Soundwave",
    "Starscream"
  ],
  "Trigun": [
    "Vash the Stampede"
  ],
  "Tron": [
    "Quorra"
  ],
  "Twenty Thousand Leagues Under the Sea": [
    "Captain Nemo"
  ],
  "Ultraman": [
    "Ultraman"
  ],
  "Undertale": [
    "Papyrus",
    "Sans"
  ],
  "Underworld": [
    "Selene (Underworld)"
  ],
  "Universal Monsters": [
    "Bride of Frankenstein",
    "Creature from the Black Lagoon",
    "Dracula",
    "Frankenstein's Monster",
    "Nosferatu",
    "The Invisible Man",
    "The Mummy",
    "The Phantom of the Opera",
    "The Wolf Man"
  ],
  "Up": [
    "Carl Fredricksen"
  ],
  "Urusei Yatsura": [
    "Lum Invader"
  ],
  "V for Vendetta": [
    "V (V for Vendetta)"
  ],
  "Valkyria Chronicles": [
    "Selvaria Bles"
  ],
  "Vampirella": [
    "Vampirella"
  ],
  "Vocaloid": [
    "Hatsune Miku",
    "Kagamine Rin",
    "Megurine Luka"
  ],
  "Voltron": [
    "Princess Allura"
  ],
  "Warhammer 40,000": [
    "Commissar",
    "Sister of Battle",
    "Space Marine",
    "Tech-Priest"
  ],
  "WarioWare": [
    "Ashley"
  ],
  "Watchmen": [
    "Doctor Manhattan",
    "Nite Owl",
    "Ozymandias",
    "Rorschach",
    "Silk Spectre",
    "The Comedian"
  ],
  "Wendy's": [
    "Wendy"
  ],
  "Who Framed Roger Rabbit": [
    "Jessica Rabbit",
    "Roger Rabbit"
  ],
  "WildStorm": [
    "Apollo (WildStorm)",
    "Diva",
    "Grifter",
    "Jenny Sparks",
    "Midnighter",
    "Zealot"
  ],
  "Winnie the Pooh": [
    "Christopher Robin",
    "Eeyore",
    "Piglet",
    "Tigger",
    "Winnie the Pooh"
  ],
  "Witchblade": [
    "Sara Pezzini"
  ],
  "World of Warcraft": [
    "Arthas Menethil",
    "Illidan Stormrage",
    "Jaina Proudmoore",
    "Sylvanas Windrunner",
    "Tyrande Whisperwind"
  ],
  "Wreck-It Ralph": [
    "Vanellope von Schweetz",
    "Wreck-It Ralph"
  ],
  "Xena: Warrior Princess": [
    "Xena"
  ],
  "Xenoblade Chronicles": [
    "Pyra"
  ],
  "Youngblood": [
    "Riptide",
    "Suprema",
    "Vogue"
  ],
  "Your Lie in April": [
    "Kaori Miyazono"
  ],
  "Yu Yu Hakusho": [
    "Yusuke Urameshi"
  ],
  "Yu-Gi-Oh!": [
    "Dark Magician",
    "Dark Magician Girl",
    "Yami Yugi"
  ],
  "Zootopia": [
    "Judy Hopps",
    "Nick Wilde"
  ],
  "Zorro": [
    "Zorro"
  ]
};
// <<< GENERATED DATA <<<

const FILTER_WIDGET = "franchise_filter";
const CHARACTER_WIDGET = "character";
const ANY = "Any";

/** Every built-in character name that has a franchise, for sentinel detection. */
const KNOWN_NAMES = new Set(Object.values(COSPLAYER_FRANCHISES).flat());

function comboValues(widget) {
  // ComfyUI has carried a combo's option list on `options.values` throughout, but
  // it may be a function in some builds -- read through either shape.
  const options = widget.options || (widget.options = {});
  const values = typeof options.values === "function"
    ? options.values(widget, null)
    : options.values;
  return Array.isArray(values) ? values : [];
}

function setComboValues(widget, values) {
  const options = widget.options || (widget.options = {});
  options.values = values;
}

/**
 * Rebuild the character list for `franchise`, preserving the original ordering.
 *
 * Filtering the pristine snapshot (rather than rebuilding from the generated map)
 * keeps the backend's own ordering and means a character added through
 * user_options.json -- absent from the generated map, so not in KNOWN_NAMES -- is
 * treated as a sentinel and stays visible under every filter. Hiding a user's own
 * character would be the worst possible failure here.
 */
function filteredOptions(allOptions, franchise, currentValue) {
  if (franchise === ANY) return allOptions.slice();

  const inFranchise = new Set(COSPLAYER_FRANCHISES[franchise] || []);
  const kept = allOptions.filter(
    (name) => !KNOWN_NAMES.has(name) || inFranchise.has(name),
  );
  // UX rule 1: the current selection is always reachable, even out of franchise.
  if (currentValue != null && !kept.includes(currentValue)) kept.push(currentValue);
  return kept;
}

function setupCosplayer(node) {
  const widgets = node.widgets || [];
  const character = widgets.find((w) => w.name === CHARACTER_WIDGET);
  if (!character) return;
  // Re-entry guard: onNodeCreated can fire again for the same node on some paths.
  if (widgets.some((w) => w.name === FILTER_WIDGET)) return;

  // Snapshot the pristine list once; every filter is derived from this, never
  // from the currently-filtered list (which would narrow irreversibly).
  const allOptions = comboValues(character).slice();
  if (!allOptions.length) return;

  const franchises = Object.keys(COSPLAYER_FRANCHISES).sort((a, b) =>
    a.localeCompare(b),
  );

  const filter = node.addWidget(
    "combo",
    FILTER_WIDGET,
    ANY,
    (value) => {
      setComboValues(character, filteredOptions(allOptions, value, character.value));
      node.setDirtyCanvas(true, true);
    },
    { values: [ANY, ...franchises], serialize: false },
  );
  filter.tooltip =
    "Narrows the character list above so it can be browsed by franchise. " +
    "View only -- it is not saved with the workflow and does not affect the " +
    "output. The 'None' and 'Random --' entries always stay in the list, and a " +
    "character you have already picked is never filtered away. To limit what the " +
    "'Random --' entries roll on, use 'random_scope' instead.";

  // Place it directly under `character` -- the widget it acts on. Reordering is
  // safe precisely because this widget does not serialize: the relative order of
  // the serializing widgets, and therefore `widgets_values`, is unchanged.
  const current = node.widgets.indexOf(filter);
  if (current > -1) {
    node.widgets.splice(current, 1);
    node.widgets.splice(node.widgets.indexOf(character) + 1, 0, filter);
  }
}

/**
 * Widgets added in a release after the workflow being loaded was saved, newest first.
 *
 * `franchise_filter` was added at 0.89.0 with `serialize: false`, on the reasoning
 * that a non-serializing widget cannot disturb `widgets_values`. **That is true when
 * writing and false when reading.** Measured on a live instance: this node has 8
 * widgets, two of them non-serializing, and `serialize()` still emits **8** values --
 * one per entry in `node.widgets`. `configure()` reads them back the same way.
 *
 * So a workflow saved before 0.89.0 carries 7 values, the node now has 8 widgets, and
 * the filter sits at index 1 -- every widget after `character` was restored one slot
 * out. Reported by the maintainer, who had to recreate each Cosplayer node by hand.
 *
 * `random_pool` (1.1.0) is a Python-appended input, always the LAST widget (schema
 * appends it after `upstream`, and `upstream` is a pure socket with no widget of its
 * own) -- the direct precedent is `FIELDS_ADDED_BY_RELEASE` in identity_forge.js.
 * Newest-first here also means highest-target-index-first: `random_pool`'s slot
 * (last) is padded before `franchise_filter`'s (right after `character`), so the
 * splice below still lands correctly even from a 7-value pre-0.89.0 array where
 * neither widget has a slot yet -- verified by hand for all three legacy lengths
 * (7 -> 9 needs both pads, 8 -> 9 needs one, 9 -> 9 is untouched) and pinned in
 * tests/frontend/cosplayer.test.mjs.
 *
 * Same table and same repair as `FIELDS_ADDED_BY_RELEASE` in identity_forge.js; the
 * two nodes hit the identical trap from opposite directions (a JS-inserted view widget
 * here, a Python-appended input there).
 */
const WIDGETS_ADDED_BY_RELEASE = [
  ["random_pool"], // 1.1.0
  [FILTER_WIDGET], // 0.89.0
];

/**
 * Pad a legacy `widgets_values` so each value lands on the widget that saved it.
 *
 * Length is the only signal the array carries, so the match must be exact: an
 * unrecognised length is left untouched rather than guessed at, because a wrong guess
 * scrambles a workflow silently instead of failing loudly. Silent on success -- the
 * values end up correct, so there is nothing for the user to act on.
 */
function padLegacyCosplayerValues(node, values) {
  const total = (node.widgets || []).length;
  if (!Array.isArray(values) || values.length >= total) return values;
  const padded = values.slice();
  for (const added of WIDGETS_ADDED_BY_RELEASE) {
    if (padded.length + added.length > total) continue;
    const slots = added
      .map((name) => (node.widgets || []).findIndex((w) => w.name === name))
      .filter((i) => i > -1)
      .sort((a, b) => a - b);
    if (slots.length !== added.length) continue;
    // Ascending: each splice shifts what follows, so low-to-high keeps later
    // indices correct as we go.
    for (const slot of slots) {
      padded.splice(slot, 0, node.widgets[slot]?.value ?? ANY);
    }
    if (padded.length === total) break;
  }
  return padded.length === total ? padded : values;
}

/**
 * Length ComfyUI's OWN V3 `ComfyNode.configure()` expects `widgets_values` to
 * have, per its internal (and here unavoidably reproduced) `migrateWidgetsValues`
 * rule -- see `dodgeUpstreamMigrationBug` below for why this exists at all.
 * Mirrors that rule exactly: for every schema input that is either already a
 * named widget on this node or `forceInput` (always a socket), count 2 slots if
 * it carries `control_after_generate`, else 1.
 */
function schemaMigrationMaskLength(node) {
  try {
    const inputs = node?.constructor?.nodeData?.inputs;
    if (!inputs) return null;
    const widgetNames = new Set((node.widgets || []).map((w) => w.name));
    let length = 0;
    for (const input of Object.values(inputs)) {
      if (!(widgetNames.has(input.name) || input.forceInput)) continue;
      length += input.control_after_generate ? 2 : 1;
    }
    return length;
  } catch (_) {
    return null;
  }
}

/**
 * Work around a ComfyUI-core bug (not ours to fix, lives in the shipped
 * frontend bundle's V3 `ComfyNode.prototype.configure`) that silently drops
 * `random_pool`'s saved value on EVERY load of this node, verified live via
 * Playwright against a real instance (1.1.0 picker fix round; see
 * docs/worklog or the task-4 fix report for the trace).
 *
 * `ComfyNode.configure()` runs `e.widgets_values = migrateWidgetsValues(
 * ComfyNode.nodeData.inputs, this.widgets, e.widgets_values)` before handing
 * off to the real (LiteGraph) positional assignment. That helper exists to
 * strip a stale `widgets_values` slot for an input that is now `forceInput`
 * (always a socket, e.g. this node's `upstream` chaining input) -- but it
 * derives how many slots to expect PURELY from the Python schema
 * (`ComfyNode.nodeData.inputs`), with no idea this file adds an extra
 * JS-only widget (`franchise_filter`) outside that schema. When its
 * schema-derived count happens to equal our actual `widgets_values.length`
 * (it does, unconditionally, for every 1.1.0-shaped save of this node: 6
 * plain inputs + 2 slots for `seed`'s `control_after_generate` + 1 for the
 * always-`forceInput` `upstream` = 9, which is also this node's real widget
 * count once `franchise_filter` and `random_pool` both exist), it applies its
 * filter -- and because `random_pool` (not `upstream`) is the actual LAST
 * schema input (see `define_schema()` in nodes/identity_forge_cosplayer.py,
 * which appends it after `upstream` precisely so its slot only ever grows at
 * the tail), that filter unconditionally strips the LAST element of
 * `widgets_values`. That is exactly `random_pool`'s slot.
 *
 * We cannot patch ComfyUI's shipped bundle. The only lever available here is
 * the LENGTH of the array handed to the base `configure()`: the bug's `if
 * (i.length === n?.length)` guard only fires on an exact match. So this
 * mirrors that same length calculation and, only when our already-correctly
 * padded array would collide with it, appends one inert trailing value
 * (a duplicate of the last real value). The real LiteGraph assignment loop
 * that runs afterward only ever consumes one value per entry in
 * `node.widgets`, so a longer array is harmless -- nothing ever reads the
 * extra element.
 */
function dodgeUpstreamMigrationBug(node, values) {
  if (!Array.isArray(values) || !values.length) return values;
  const maskLength = schemaMigrationMaskLength(node);
  if (maskLength !== null && values.length === maskLength) {
    return [...values, values[values.length - 1]];
  }
  return values;
}

/**
 * Visual order the maintainer wants `random_pool` grouped near `random_scope`,
 * the other randomization-constraint widget -- distinct from `node.widgets`'
 * real array order (see the `WIDGETS_ADDED_BY_RELEASE` comment above for why
 * that array order, and therefore `random_pool`'s index, can never move: it
 * IS a serializing, Python-schema widget, unlike `franchise_filter`). Any
 * widget not named here (e.g. the `control_after_generate` companion LiteGraph
 * auto-adds next to `seed`) keeps its normal position relative to its
 * neighbours.
 */
const VISUAL_WIDGET_ORDER = [
  CHARACTER_WIDGET,
  FILTER_WIDGET,
  "random_scope",
  "random_pool",
  "look_level",
  "mask",
  "props",
  "seed",
];

/**
 * Make widgets DRAW in `VISUAL_WIDGET_ORDER` without moving anything in
 * `node.widgets` itself.
 *
 * `franchise_filter`'s own reorder above (see the comment on its splice) is
 * NOT a precedent for this: it works by physically moving the widget's index
 * in `node.widgets`, which is safe for it ONLY in the writing direction
 * because it declares `serialize: false` -- and even that turned out to be
 * unsafe in the reading direction (see the `WIDGETS_ADDED_BY_RELEASE` comment:
 * `serialize()` still emits one value per `node.widgets` entry regardless of
 * `serialize: false`, which is exactly the legacy-load bug that comment
 * documents). `random_pool` IS a serializing widget, so physically moving it
 * would directly break `configure()`'s index-based mapping of
 * `widgets_values` -- the one invariant this whole release protects. That
 * mechanism does not generalize here, so this uses a different one.
 *
 * Read directly out of the pinned `comfyui-frontend-package` 1.51.9 bundle
 * (`static/assets/settingStore-*.js`, minified, decoded by hand for this fix --
 * see the task-4c report for the exact excerpts): `LGraphNode.prototype
 * ._arrangeWidgets` assigns each widget's `.y` (its drawn vertical offset) by
 * iterating `node.getLayoutWidgets()` -- NOT `node.widgets` directly -- and
 * accumulating height in THAT order:
 *
 *   getLayoutWidgets(){ return this.widgets?.filter(w => !w.hidden) ?? [] }
 *   ...
 *   let l = n; for (let w of layoutWidgets) w.y = l, l += w.computedHeight ?? 0;
 *
 * `drawWidgets()` then iterates `node.widgets` (real array order) only to
 * draw each widget AT the `.y` it was already assigned -- so the draw loop's
 * own order never matters, only `getLayoutWidgets()`'s does. Overriding
 * `getLayoutWidgets()` on this one node instance therefore retargets only
 * where things draw; `node.widgets`, `serialize()`, `configure()`, and
 * `widgets_values` indexing never see it. Hit-testing reads back each
 * widget's own `.last_y` (set from that same `.y` during the same draw pass),
 * so clicks land on the right widget wherever it actually drew, regardless of
 * array position -- nothing extra is needed there.
 *
 * Cross-frontend-version note: `getLayoutWidgets` is a method on this forked
 * LiteGraph's `LGraphNode`, not a documented/stable public API, and classic
 * (pre-fork) LiteGraph computes widget `.y` by iterating `node.widgets`
 * directly with no such indirection point to hook. Feature-detected below:
 * on a frontend with no `getLayoutWidgets` method, this override is simply
 * never called by anything, so it is inert -- widgets draw in their natural
 * array-order position, exactly as they did before this function existed.
 * Either way `node.widgets`' order is untouched, so the worst case of this
 * being wrong on some frontend version is that the cosmetic reorder silently
 * does not apply there, never a compatibility regression.
 *
 * CONFIRMED GAP, not a residual risk (an earlier version of this comment
 * called this "unconfirmed" -- it has since been checked directly and does
 * not work): this override has NO effect when the "Nodes 2.0" / VueNodes DOM
 * renderer is active, which is a *different* rendering path entirely, not a
 * fallback of the one described above. Read directly out of the same 1.51.9
 * bundle: VueNodes' `NodeWidgets.vue` component renders `processedWidgets`
 * (from `useProcessedWidgets` -> `computeProcessedWidgets`), which builds its
 * list with a single `for (let [i, w] of nodeData.widgets.entries())` --
 * straight array order, no sort, no `getLayoutWidgets` call anywhere in that
 * function. `nodeData.widgets` is not a separate copy either: `extractVueNodeData`
 * redefines `node.widgets` itself as an accessor (`Object.defineProperty`)
 * backed by a reactive-mirrored array of the SAME order, so in VueNodes mode
 * `node.widgets` IS the one and only order Vue renders from -- there is no
 * second, overridable channel analogous to `getLayoutWidgets()` for the DOM
 * path. Confirmed live (Playwright against `:8288` in actual Nodes-2.0 mode,
 * querying real rendered DOM order): `random_pool` still draws last. See the
 * task-4c report for the full trace and why a CSS-`order` / MutationObserver
 * workaround on the rendered DOM was considered and rejected rather than
 * shipped -- this file has no test infrastructure for real Vue-rendered DOM,
 * unlike everything else in this comment block.
 *
 * One more thing the bundle source above does NOT show: `_arrangeWidgets`
 * (and therefore this override) only actually RUNS when LiteGraph's own
 * per-frame draw loop sees `node._widgetSlotsDirty === true` -- the same flag
 * `addCustomWidget`/`removeWidget` set, and the ONLY thing that clears it is
 * `arrange()` itself finishing. Overriding `getLayoutWidgets()` alone changes
 * what a FUTURE layout pass would compute but does not invalidate a `.y` a
 * PAST pass already cached -- and every widget on this node already went
 * through one such pass (from its own construction) before this override
 * ever attaches. Caught live: without the line below, `random_pool` kept
 * drawing at its pre-fix position through a fresh node add AND a full
 * ComfyUI restart, because nothing had touched a widget slot (add/remove)
 * since that first, pre-override layout pass. Setting the same flag the
 * engine itself uses to invalidate this cache is what makes the NEXT draw
 * actually call `arrange()` again, this time through our override.
 */
function applyVisualWidgetOrder(node) {
  if (node.__ifVisualOrderApplied) return;
  if (typeof node.getLayoutWidgets !== "function") return;
  const baseGetLayoutWidgets = node.getLayoutWidgets.bind(node);
  const rank = (name) => {
    const i = VISUAL_WIDGET_ORDER.indexOf(name);
    return i === -1 ? VISUAL_WIDGET_ORDER.length : i;
  };
  node.getLayoutWidgets = function () {
    return baseGetLayoutWidgets()
      .map((w, i) => [w, i])
      .sort(([wa, ia], [wb, ib]) => rank(wa.name) - rank(wb.name) || ia - ib)
      .map(([w]) => w);
  };
  node.__ifVisualOrderApplied = true;
  // Force the next draw to redo the (now-overridden) layout pass -- see the
  // comment above. Feature-detected the same way: an older/classic LiteGraph
  // node without this field simply never had a cached `.y` to invalidate.
  if ("_widgetSlotsDirty" in node) node._widgetSlotsDirty = true;
}

app.registerExtension({
  name: "identity_forge.cosplayer.ui",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData?.name !== "IdentityForgeCosplayer") return;
    const onCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const result = onCreated?.apply(this, arguments);
      try {
        setupCosplayer(this);
      } catch (err) {
        console.error("[IdentityForgeCosplayer] franchise filter setup failed", err);
      }
      try {
        applyVisualWidgetOrder(this);
      } catch (err) {
        console.error("[IdentityForgeCosplayer] visual widget reorder failed", err);
      }
      return result;
    };

    // `configure`, not `onConfigure`: LiteGraph applies widgets_values and only then
    // calls onConfigure, so by then the values are already in the wrong widgets.
    // onNodeCreated has run by now, so the filter exists and can be located by name.
    const configure = nodeType.prototype.configure;
    nodeType.prototype.configure = function (info) {
      try {
        if (info && Array.isArray(info.widgets_values)) {
          info = {
            ...info,
            widgets_values: dodgeUpstreamMigrationBug(
              this,
              padLegacyCosplayerValues(this, info.widgets_values),
            ),
          };
        }
      } catch (err) {
        console.error("[IdentityForgeCosplayer] legacy widget mapping failed", err);
      }
      return configure ? configure.apply(this, [info]) : undefined;
    };
  },
});
