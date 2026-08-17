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
  "A Nightmare on Elm Street": [
    "Freddy Krueger"
  ],
  "ARMS": [
    "Twintelle"
  ],
  "Adventure Time": [
    "Finn the Human",
    "Ice King",
    "Jake the Dog",
    "Marceline the Vampire Queen",
    "Princess Bubblegum"
  ],
  "Akame ga Kill": [
    "Akame",
    "Esdeath",
    "Leone"
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
  "Assassin's Creed": [
    "Ezio Auditore"
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
    "Azula",
    "Iroh",
    "Katara",
    "Mai (Avatar)",
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
    "Shadowheart"
  ],
  "Battlestar Galactica": [
    "Cylon Centurion"
  ],
  "Bayonetta": [
    "Bayonetta"
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
    "Splicer"
  ],
  "Black Butler": [
    "Ciel Phantomhive",
    "Sebastian Michaelis"
  ],
  "Black Lagoon": [
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
    "Handsome Jack",
    "Lilith (Borderlands)",
    "Mad Moxxi",
    "Psycho (Borderlands)",
    "Tiny Tina"
  ],
  "Brave": [
    "Merida"
  ],
  "Braveheart": [
    "William Wallace"
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
    "Makima",
    "Power (Chainsaw Man)"
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
  "Cinderella": [
    "Cinderella",
    "Fairy Godmother",
    "Lady Tremaine"
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
  "Cyberpunk 2077": [
    "Johnny Silverhand",
    "Judy Alvarez"
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
  "Danganronpa": [
    "Junko Enoshima"
  ],
  "Danger Girl": [
    "Abbey Chase",
    "Natalia Kassle"
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
  "F-Zero": [
    "Captain Falcon"
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
  "FernGully": [
    "Crysta"
  ],
  "Final Fantasy": [
    "Aerith Gainsborough",
    "Auron",
    "Barret Wallace",
    "Cecil Harvey",
    "Celes Chere",
    "Cloud Strife",
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
    "Azura"
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
  "Friday the 13th": [
    "Jason Voorhees"
  ],
  "Frieren: Beyond Journey's End": [
    "Fern",
    "Frieren"
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
    "Jon Snow",
    "Melisandre",
    "The Night King"
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
  "God of War": [
    "Freya",
    "Kratos"
  ],
  "Godzilla": [
    "Godzilla"
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
    "Bellatrix Lestrange",
    "Draco Malfoy",
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
  "Horizon": [
    "Aloy"
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
    "Inuyasha"
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
  "Kakegurui": [
    "Yumeko Jabami"
  ],
  "Keebler": [
    "Ernie Keebler"
  ],
  "Kellogg's": [
    "Tony the Tiger"
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
    "Jareth the Goblin King"
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
    "Lola Bunny",
    "Marvin the Martian",
    "Tasmanian Devil",
    "Yosemite Sam"
  ],
  "Mad Max": [
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
    "Ronald McDonald"
  ],
  "Medaka Box": [
    "Medaka Kurokami"
  ],
  "Metal Gear": [
    "Solid Snake"
  ],
  "Metroid": [
    "Samus Aran (Power Suit)",
    "Zero Suit Samus"
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
    "Fubuki (One Punch Man)",
    "Garou",
    "Genos",
    "Mumen Rider",
    "Saitama",
    "Tatsumaki"
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
  "Peanuts": [
    "Charlie Brown"
  ],
  "Peepoodo": [
    "Dr. Monique Pussycat"
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
    "Iris",
    "James (Team Rocket)",
    "Jessie (Team Rocket)",
    "Jigglypuff",
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
  "Sailor Moon": [
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
  "Scooby-Doo": [
    "Daphne Blake",
    "Fred Jones",
    "Shaggy",
    "Velma Dinkley"
  ],
  "Scream": [
    "Ghostface"
  ],
  "Sheena, Queen of the Jungle": [
    "Sheena"
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
    "Sung Jinwoo"
  ],
  "Sonic the Hedgehog": [
    "Dr. Eggman",
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
  "The Addams Family": [
    "Cousin Itt",
    "Gomez Addams",
    "Lurch",
    "Morticia Addams",
    "Uncle Fester",
    "Wednesday Addams"
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
    "Ellie Williams"
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
    "Frodo Baggins",
    "Galadriel",
    "Gandalf",
    "Gimli",
    "Gollum",
    "Legolas",
    "Samwise Gamgee",
    "Saruman",
    "Sauron",
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
  "The Nightmare Before Christmas": [
    "Jack Skellington",
    "Oogie Boogie",
    "Sally"
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
  "The Road to El Dorado": [
    "Chel",
    "Miguel",
    "Tulio",
    "Tzekel-Kan"
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
  "Ultraman": [
    "Ultraman"
  ],
  "Underworld": [
    "Selene (Underworld)"
  ],
  "Universal Monsters": [
    "Bride of Frankenstein",
    "Creature from the Black Lagoon",
    "Dracula",
    "Frankenstein's Monster",
    "The Mummy",
    "The Phantom of the Opera",
    "The Wolf Man"
  ],
  "Up": [
    "Carl Fredricksen"
  ],
  "V for Vendetta": [
    "V (V for Vendetta)"
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
 * Same table and same repair as `FIELDS_ADDED_BY_RELEASE` in identity_forge.js; the
 * two nodes hit the identical trap from opposite directions (a JS-inserted view widget
 * here, a Python-appended input there).
 */
const WIDGETS_ADDED_BY_RELEASE = [
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
            widgets_values: padLegacyCosplayerValues(this, info.widgets_values),
          };
        }
      } catch (err) {
        console.error("[IdentityForgeCosplayer] legacy widget mapping failed", err);
      }
      return configure ? configure.apply(this, [info]) : undefined;
    };
  },
});
