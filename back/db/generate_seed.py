# Generates db/seed.sql with synthetic but meaningful demo data.
# Usage (from back/):  python db/generate_seed.py
# Deterministic: random.seed(42) gives the same file every time.
# Standard library only, no network.
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)
OUT = Path(__file__).parent / "seed.sql"

# ---------------------------------------------------------------------
# Reference tables
# ---------------------------------------------------------------------
CATEGORIES = ["Fiction", "Non-Fiction", "Fantasy", "Sci-Fi", "Mystery", "Biography"]

LIBRARIANS = [
    ("Online", "online@library.local"),  # used for loans made on the website
    ("Гүлнара Сейітқали", "gulnara@library.local"),
    ("Айдос Нұрланұлы", "aidos@library.local"),
    ("Елена Петрова", "elena@library.local"),
    ("Michael Brown", "michael@library.local"),
]

# (name, country, language group) - the group decides which books it prints
PUBLISHERS = [
    ("Penguin Books", "United Kingdom", "en"),
    ("HarperCollins", "United States", "en"),
    ("Bloomsbury", "United Kingdom", "en"),
    ("Secker & Warburg", "United Kingdom", "en"),
    ("Allen & Unwin", "United Kingdom", "en"),
    ("Scribner", "United States", "en"),
    ("Ace Books", "United States", "en"),
    ("Simon & Schuster", "United States", "en"),
    ("Collins Crime Club", "United Kingdom", "en"),
    ("Bantam Books", "United States", "en"),
    ("Random House", "United States", "en"),
    ("Vintage", "United Kingdom", "en"),
    ("Doubleday", "United States", "en"),
    ("Alfred A. Knopf", "United States", "en"),
    ("Little, Brown and Company", "United States", "en"),
    ("Macmillan", "United Kingdom", "en"),
    ("Faber & Faber", "United Kingdom", "en"),
    ("Hodder & Stoughton", "United Kingdom", "en"),
    ("Gollancz", "United Kingdom", "en"),
    ("Tor Books", "United States", "en"),
    ("Del Rey", "United States", "en"),
    ("Picador", "United Kingdom", "en"),
    ("Oxford University Press", "United Kingdom", "en"),
    ("Houghton Mifflin", "United States", "en"),
    ("Viking Press", "United States", "en"),
    ("Эксмо", "Россия", "ru"),
    ("АСТ", "Россия", "ru"),
    ("Азбука", "Россия", "ru"),
    ("Жазушы", "Қазақстан", "kk"),
    ("Атамұра", "Қазақстан", "kk"),
    ("Фолиант", "Қазақстан", "kk"),
]

# Real authors: name -> (birth year, country)
AUTHORS = {
    "George Orwell": (1903, "United Kingdom"),
    "Harper Lee": (1926, "United States"),
    "F. Scott Fitzgerald": (1896, "United States"),
    "Jane Austen": (1775, "United Kingdom"),
    "J.D. Salinger": (1919, "United States"),
    "Gabriel García Márquez": (1927, "Colombia"),
    "Ernest Hemingway": (1899, "United States"),
    "John Steinbeck": (1902, "United States"),
    "Paulo Coelho": (1947, "Brazil"),
    "Charlotte Brontë": (1816, "United Kingdom"),
    "Emily Brontë": (1818, "United Kingdom"),
    "Herman Melville": (1819, "United States"),
    "Mark Twain": (1835, "United States"),
    "Charles Dickens": (1812, "United Kingdom"),
    "Victor Hugo": (1802, "France"),
    "Kazuo Ishiguro": (1954, "United Kingdom"),
    "Khaled Hosseini": (1965, "United States"),
    "Toni Morrison": (1931, "United States"),
    "Chinua Achebe": (1930, "Nigeria"),
    "Albert Camus": (1913, "France"),
    "Franz Kafka": (1883, "Czechia"),
    "Oscar Wilde": (1854, "Ireland"),
    "Virginia Woolf": (1882, "United Kingdom"),
    "Haruki Murakami": (1949, "Japan"),
    "Cormac McCarthy": (1933, "United States"),
    "Yann Martel": (1963, "Canada"),
    "Markus Zusak": (1975, "Australia"),
    "Margaret Atwood": (1939, "Canada"),
    "Лев Толстой": (1828, "Россия"),
    "Фёдор Достоевский": (1821, "Россия"),
    "Антон Чехов": (1860, "Россия"),
    "Александр Пушкин": (1799, "Россия"),
    "Николай Гоголь": (1809, "Украина"),
    "Иван Тургенев": (1818, "Россия"),
    "Михаил Лермонтов": (1814, "Россия"),
    "Владимир Набоков": (1899, "Россия"),
    "Михаил Шолохов": (1905, "Россия"),
    "Михаил Булгаков": (1891, "Россия"),
    "Абай Құнанбайұлы": (1845, "Қазақстан"),
    "Мұхтар Әуезов": (1897, "Қазақстан"),
    "Ілияс Есенберлин": (1915, "Қазақстан"),
    "Ғабит Мүсірепов": (1902, "Қазақстан"),
    "Мағжан Жұмабаев": (1893, "Қазақстан"),
    "Олжас Сулейменов": (1936, "Казахстан"),
    "Frank Herbert": (1920, "United States"),
    "Isaac Asimov": (1920, "United States"),
    "Ray Bradbury": (1920, "United States"),
    "Aldous Huxley": (1894, "United Kingdom"),
    "William Gibson": (1948, "Canada"),
    "Philip K. Dick": (1928, "United States"),
    "Arthur C. Clarke": (1917, "United Kingdom"),
    "Orson Scott Card": (1951, "United States"),
    "Douglas Adams": (1952, "United Kingdom"),
    "H.G. Wells": (1866, "United Kingdom"),
    "Mary Shelley": (1797, "United Kingdom"),
    "Jules Verne": (1828, "France"),
    "Andy Weir": (1972, "United States"),
    "Liu Cixin": (1963, "China"),
    "Stanisław Lem": (1921, "Poland"),
    "Kurt Vonnegut": (1922, "United States"),
    "Robert A. Heinlein": (1907, "United States"),
    "Ursula K. Le Guin": (1929, "United States"),
    "Dan Simmons": (1948, "United States"),
    "Аркадий Стругацкий": (1925, "Россия"),
    "Борис Стругацкий": (1933, "Россия"),
    "Иван Ефремов": (1908, "Россия"),
    "Евгений Замятин": (1884, "Россия"),
    "J.R.R. Tolkien": (1892, "United Kingdom"),
    "J.K. Rowling": (1965, "United Kingdom"),
    "C.S. Lewis": (1898, "United Kingdom"),
    "George R.R. Martin": (1948, "United States"),
    "Terry Pratchett": (1948, "United Kingdom"),
    "Neil Gaiman": (1960, "United Kingdom"),
    "Patrick Rothfuss": (1973, "United States"),
    "Brandon Sanderson": (1975, "United States"),
    "Lewis Carroll": (1832, "United Kingdom"),
    "L. Frank Baum": (1856, "United States"),
    "Philip Pullman": (1946, "United Kingdom"),
    "Robert Jordan": (1948, "United States"),
    "Andrzej Sapkowski": (1948, "Poland"),
    "Susanna Clarke": (1959, "United Kingdom"),
    "Michael Ende": (1929, "Germany"),
    "Сергей Лукьяненко": (1968, "Россия"),
    "Agatha Christie": (1890, "United Kingdom"),
    "Arthur Conan Doyle": (1859, "United Kingdom"),
    "Edgar Allan Poe": (1809, "United States"),
    "Dan Brown": (1964, "United States"),
    "Stieg Larsson": (1954, "Sweden"),
    "Gillian Flynn": (1971, "United States"),
    "Raymond Chandler": (1888, "United States"),
    "Dashiell Hammett": (1894, "United States"),
    "Wilkie Collins": (1824, "United Kingdom"),
    "Patricia Highsmith": (1921, "United States"),
    "Tana French": (1973, "Ireland"),
    "Paula Hawkins": (1972, "United Kingdom"),
    "Thomas Harris": (1940, "United States"),
    "Umberto Eco": (1932, "Italy"),
    "Борис Акунин": (1956, "Россия"),
    "Dorothy L. Sayers": (1893, "United Kingdom"),
    "Yuval Noah Harari": (1976, "Israel"),
    "Stephen Hawking": (1942, "United Kingdom"),
    "Leonard Mlodinow": (1954, "United States"),
    "Jared Diamond": (1937, "United States"),
    "Daniel Kahneman": (1934, "Israel"),
    "Malcolm Gladwell": (1963, "Canada"),
    "Rachel Carson": (1907, "United States"),
    "Carl Sagan": (1934, "United States"),
    "Richard Dawkins": (1941, "United Kingdom"),
    "Bill Bryson": (1951, "United States"),
    "James Clear": (1986, "United States"),
    "Susan Cain": (1968, "United States"),
    "Charles Darwin": (1809, "United Kingdom"),
    "Steven Levitt": (1967, "United States"),
    "Stephen J. Dubner": (1963, "United States"),
    "Dale Carnegie": (1888, "United States"),
    "Viktor Frankl": (1905, "Austria"),
    "Adam Smith": (1723, "United Kingdom"),
    "Walter Isaacson": (1952, "United States"),
    "Michelle Obama": (1964, "United States"),
    "Anne Frank": (1929, "Netherlands"),
    "Nelson Mandela": (1918, "South Africa"),
    "Malcolm X": (1925, "United States"),
    "Alex Haley": (1921, "United States"),
    "Ron Chernow": (1949, "United States"),
    "Tara Westover": (1986, "United States"),
    "Ashlee Vance": (1977, "United States"),
    "Benjamin Franklin": (1706, "United States"),
    "Maya Angelou": (1928, "United States"),
    "Phil Knight": (1938, "United States"),
    "Trevor Noah": (1984, "South Africa"),
    "Paul Kalanithi": (1977, "United States"),
    "Rebecca Skloot": (1972, "United States"),
    "Helen Keller": (1880, "United States"),
    "Mahatma Gandhi": (1869, "India"),
}

# Real books: (title, year, genre, [authors], language, short description).
# The descriptions are our own short summaries.
BOOKS = [
    # --- Fiction ---
    ("1984", 1949, "Fiction", ["George Orwell"], "en", "A clerk in a total surveillance state starts to doubt the Party. A warning about power and truth."),
    ("Animal Farm", 1945, "Fiction", ["George Orwell"], "en", "Farm animals overthrow their owner and slowly become what they fought against."),
    ("To Kill a Mockingbird", 1960, "Fiction", ["Harper Lee"], "en", "A child watches her father defend an innocent man in a racist small town."),
    ("The Great Gatsby", 1925, "Fiction", ["F. Scott Fitzgerald"], "en", "A mysterious millionaire throws parties to win back a lost love in the Jazz Age."),
    ("Pride and Prejudice", 1813, "Fiction", ["Jane Austen"], "en", "Elizabeth Bennet and Mr Darcy learn that first impressions can be wrong."),
    ("The Catcher in the Rye", 1951, "Fiction", ["J.D. Salinger"], "en", "A teenager wanders New York for three days after leaving his school."),
    ("One Hundred Years of Solitude", 1967, "Fiction", ["Gabriel García Márquez"], "en", "Seven generations of one family live through the magic and wars of a small town."),
    ("The Old Man and the Sea", 1952, "Fiction", ["Ernest Hemingway"], "en", "An old fisherman fights a giant marlin far out at sea."),
    ("The Grapes of Wrath", 1939, "Fiction", ["John Steinbeck"], "en", "A farming family travels to California during the Great Depression."),
    ("The Alchemist", 1988, "Fiction", ["Paulo Coelho"], "en", "A young shepherd follows a dream about treasure across the desert."),
    ("Jane Eyre", 1847, "Fiction", ["Charlotte Brontë"], "en", "An orphan governess finds love and a dark secret in a remote house."),
    ("Wuthering Heights", 1847, "Fiction", ["Emily Brontë"], "en", "A wild love story on the Yorkshire moors turns into revenge."),
    ("Moby-Dick", 1851, "Fiction", ["Herman Melville"], "en", "Captain Ahab hunts the white whale that took his leg."),
    ("Adventures of Huckleberry Finn", 1884, "Fiction", ["Mark Twain"], "en", "A boy and an escaped slave travel down the Mississippi on a raft."),
    ("Great Expectations", 1861, "Fiction", ["Charles Dickens"], "en", "An orphan receives money from an unknown benefactor and learns what really matters."),
    ("Les Misérables", 1862, "Fiction", ["Victor Hugo"], "en", "A former convict tries to live honestly while a policeman hunts him."),
    ("Never Let Me Go", 2005, "Fiction", ["Kazuo Ishiguro"], "en", "Three friends from a strange boarding school slowly learn their purpose."),
    ("The Kite Runner", 2003, "Fiction", ["Khaled Hosseini"], "en", "A man returns to Kabul to repair a betrayal from his childhood."),
    ("Beloved", 1987, "Fiction", ["Toni Morrison"], "en", "A formerly enslaved mother is haunted by the past she escaped."),
    ("Things Fall Apart", 1958, "Fiction", ["Chinua Achebe"], "en", "A proud Igbo leader sees his world change when missionaries arrive."),
    ("The Stranger", 1942, "Fiction", ["Albert Camus"], "en", "A calm, distant man commits a crime and faces an absurd trial."),
    ("The Trial", 1925, "Fiction", ["Franz Kafka"], "en", "A bank clerk is arrested and never learns what he is accused of."),
    ("The Picture of Dorian Gray", 1890, "Fiction", ["Oscar Wilde"], "en", "A young man stays beautiful while his portrait shows every sin."),
    ("Mrs Dalloway", 1925, "Fiction", ["Virginia Woolf"], "en", "One day in London as a woman prepares an evening party."),
    ("Norwegian Wood", 1987, "Fiction", ["Haruki Murakami"], "en", "A student in Tokyo remembers love and loss in the late 1960s."),
    ("The Road", 2006, "Fiction", ["Cormac McCarthy"], "en", "A father and son walk south through a burned, empty country."),
    ("Life of Pi", 2001, "Fiction", ["Yann Martel"], "en", "A boy survives at sea in a lifeboat with a Bengal tiger."),
    ("The Book Thief", 2005, "Fiction", ["Markus Zusak"], "en", "In Nazi Germany a girl steals books and shares them with others."),
    ("The Handmaid's Tale", 1985, "Fiction", ["Margaret Atwood"], "en", "In a strict theocracy women lose all rights; one of them tells her story."),
    ("Война и мир", 1869, "Fiction", ["Лев Толстой"], "ru", "Судьбы нескольких дворянских семей на фоне войны с Наполеоном."),
    ("Анна Каренина", 1878, "Fiction", ["Лев Толстой"], "ru", "История любви, которая ломает правила высшего общества."),
    ("Преступление и наказание", 1866, "Fiction", ["Фёдор Достоевский"], "ru", "Бедный студент совершает убийство и не может жить с этим."),
    ("Братья Карамазовы", 1880, "Fiction", ["Фёдор Достоевский"], "ru", "Три брата, их отец и спор о вере, свободе и вине."),
    ("Вишнёвый сад", 1904, "Fiction", ["Антон Чехов"], "ru", "Семья теряет старое имение и вишнёвый сад."),
    ("Евгений Онегин", 1833, "Fiction", ["Александр Пушкин"], "ru", "Роман в стихах о скучающем дворянине и Татьяне."),
    ("Мёртвые души", 1842, "Fiction", ["Николай Гоголь"], "ru", "Чичиков скупает умерших крестьян и показывает Россию помещиков."),
    ("Отцы и дети", 1862, "Fiction", ["Иван Тургенев"], "ru", "Молодой нигилист Базаров спорит со старшим поколением."),
    ("Герой нашего времени", 1840, "Fiction", ["Михаил Лермонтов"], "ru", "Несколько историй о Печорине, умном и холодном офицере."),
    ("Защита Лужина", 1930, "Fiction", ["Владимир Набоков"], "ru", "Гениальный шахматист живёт внутри своей игры."),
    ("Тихий Дон", 1940, "Fiction", ["Михаил Шолохов"], "ru", "Жизнь донских казаков в годы войн и революции."),
    ("Өлеңдер жинағы", 1909, "Fiction", ["Абай Құнанбайұлы"], "kk", "Абайдың өлеңдері: адам, еңбек, білім және ел туралы ойлар."),
    ("Абай жолы", 1956, "Fiction", ["Мұхтар Әуезов"], "kk", "Ұлы ақын Абайдың өмірі мен заманы туралы эпопея."),
    ("Көшпенділер", 1973, "Fiction", ["Ілияс Есенберлин"], "kk", "Қазақ хандығының тарихы туралы үш кітаптан тұратын роман."),
    ("Ұлпан", 1974, "Fiction", ["Ғабит Мүсірепов"], "kk", "Ақылды әрі батыл қазақ әйелі Ұлпанның тағдыры."),
    ("Батыр Баян", 1923, "Fiction", ["Мағжан Жұмабаев"], "kk", "Абылай заманындағы батыр Баян туралы дастан."),
    # --- Sci-Fi ---
    ("Dune", 1965, "Sci-Fi", ["Frank Herbert"], "en", "A noble family takes control of a desert planet that holds the most valuable spice."),
    ("Foundation", 1951, "Sci-Fi", ["Isaac Asimov"], "en", "A mathematician plans how to shorten the dark age after a galactic empire falls."),
    ("I, Robot", 1950, "Sci-Fi", ["Isaac Asimov"], "en", "Stories about robots that follow three laws, and where the laws break."),
    ("Fahrenheit 451", 1953, "Sci-Fi", ["Ray Bradbury"], "en", "A fireman burns books until he starts reading one."),
    ("Brave New World", 1932, "Sci-Fi", ["Aldous Huxley"], "en", "A comfortable future where people are made happy and never free."),
    ("Neuromancer", 1984, "Sci-Fi", ["William Gibson"], "en", "A burned-out hacker gets one last job inside cyberspace."),
    ("Do Androids Dream of Electric Sheep?", 1968, "Sci-Fi", ["Philip K. Dick"], "en", "A bounty hunter chases androids and asks what makes us human."),
    ("2001: A Space Odyssey", 1968, "Sci-Fi", ["Arthur C. Clarke"], "en", "A mission to Jupiter follows a mysterious black monolith."),
    ("Ender's Game", 1985, "Sci-Fi", ["Orson Scott Card"], "en", "A gifted child is trained in battle school to fight an alien war."),
    ("The Hitchhiker's Guide to the Galaxy", 1979, "Sci-Fi", ["Douglas Adams"], "en", "Seconds before Earth is destroyed, Arthur Dent is pulled into a comic trip through space."),
    ("The War of the Worlds", 1898, "Sci-Fi", ["H.G. Wells"], "en", "Martians land in England and nothing can stop them."),
    ("The Time Machine", 1895, "Sci-Fi", ["H.G. Wells"], "en", "An inventor travels to the far future and finds humanity split in two."),
    ("Frankenstein", 1818, "Sci-Fi", ["Mary Shelley"], "en", "A scientist creates life and runs from what he has made."),
    ("Twenty Thousand Leagues Under the Seas", 1870, "Sci-Fi", ["Jules Verne"], "en", "Captain Nemo takes his prisoners around the world in a submarine."),
    ("The Martian", 2011, "Sci-Fi", ["Andy Weir"], "en", "An astronaut left alone on Mars uses science to stay alive."),
    ("The Three-Body Problem", 2008, "Sci-Fi", ["Liu Cixin"], "en", "A secret project makes contact with a civilisation from a chaotic star system."),
    ("Solaris", 1961, "Sci-Fi", ["Stanisław Lem"], "en", "Scientists study a living ocean that answers with their own memories."),
    ("Slaughterhouse-Five", 1969, "Sci-Fi", ["Kurt Vonnegut"], "en", "A soldier becomes unstuck in time after the bombing of Dresden."),
    ("Stranger in a Strange Land", 1961, "Sci-Fi", ["Robert A. Heinlein"], "en", "A man raised by Martians comes to Earth and questions its customs."),
    ("The Left Hand of Darkness", 1969, "Sci-Fi", ["Ursula K. Le Guin"], "en", "An envoy visits a cold planet where people have no fixed gender."),
    ("Hyperion", 1989, "Sci-Fi", ["Dan Simmons"], "en", "Seven pilgrims tell their stories on the way to a deadly creature."),
    ("Пикник на обочине", 1972, "Sci-Fi", ["Аркадий Стругацкий", "Борис Стругацкий"], "ru", "Сталкер ходит в опасную Зону, оставленную пришельцами."),
    ("Трудно быть богом", 1964, "Sci-Fi", ["Аркадий Стругацкий", "Борис Стругацкий"], "ru", "Земной наблюдатель живёт в жестоком средневековом мире."),
    ("Туманность Андромеды", 1957, "Sci-Fi", ["Иван Ефремов"], "ru", "Далёкое будущее, где Земля входит в Великое Кольцо цивилизаций."),
    ("Мы", 1924, "Sci-Fi", ["Евгений Замятин"], "ru", "Инженер Единого Государства пишет дневник и начинает сомневаться."),
    # --- Fantasy ---
    ("The Hobbit", 1937, "Fantasy", ["J.R.R. Tolkien"], "en", "Bilbo Baggins leaves his quiet home to help dwarves reclaim their treasure."),
    ("The Fellowship of the Ring", 1954, "Fantasy", ["J.R.R. Tolkien"], "en", "Frodo sets out with eight companions to destroy a dangerous ring."),
    ("Harry Potter and the Philosopher's Stone", 1997, "Fantasy", ["J.K. Rowling"], "en", "An orphan learns he is a wizard and starts school at Hogwarts."),
    ("The Lion, the Witch and the Wardrobe", 1950, "Fantasy", ["C.S. Lewis"], "en", "Four children walk through a wardrobe into the frozen land of Narnia."),
    ("A Game of Thrones", 1996, "Fantasy", ["George R.R. Martin"], "en", "Noble houses fight for the Iron Throne while winter is coming."),
    ("A Wizard of Earthsea", 1968, "Fantasy", ["Ursula K. Le Guin"], "en", "A proud young wizard releases a shadow and must hunt it down."),
    ("Good Omens", 1990, "Fantasy", ["Terry Pratchett", "Neil Gaiman"], "en", "An angel and a demon try to stop the end of the world."),
    ("American Gods", 2001, "Fantasy", ["Neil Gaiman"], "en", "Old gods brought to America fight the new gods of media and technology."),
    ("The Name of the Wind", 2007, "Fantasy", ["Patrick Rothfuss"], "en", "A legendary hero tells the true story of his youth."),
    ("Mistborn: The Final Empire", 2006, "Fantasy", ["Brandon Sanderson"], "en", "A street thief with magic powers joins a plan to overthrow an immortal ruler."),
    ("Alice's Adventures in Wonderland", 1865, "Fantasy", ["Lewis Carroll"], "en", "A girl falls down a rabbit hole into a world of nonsense."),
    ("The Wonderful Wizard of Oz", 1900, "Fantasy", ["L. Frank Baum"], "en", "A tornado carries Dorothy to Oz, and she looks for a way home."),
    ("Northern Lights", 1995, "Fantasy", ["Philip Pullman"], "en", "Lyra travels north to save kidnapped children."),
    ("The Eye of the World", 1990, "Fantasy", ["Robert Jordan"], "en", "Village friends flee from dark forces that hunt one of them."),
    ("The Last Wish", 1993, "Fantasy", ["Andrzej Sapkowski"], "en", "Stories about Geralt, a monster hunter in a morally grey world."),
    ("Jonathan Strange & Mr Norrell", 2004, "Fantasy", ["Susanna Clarke"], "en", "Two magicians bring magic back to England during the Napoleonic wars."),
    ("The Neverending Story", 1979, "Fantasy", ["Michael Ende"], "en", "A lonely boy reads a book and becomes part of its story."),
    ("Мастер и Маргарита", 1967, "Fantasy", ["Михаил Булгаков"], "ru", "Воланд приезжает в Москву, а Маргарита спасает Мастера."),
    ("Ночной дозор", 1998, "Fantasy", ["Сергей Лукьяненко"], "ru", "Светлые и Тёмные Иные следят друг за другом в Москве."),
    # --- Mystery ---
    ("Murder on the Orient Express", 1934, "Mystery", ["Agatha Christie"], "en", "Hercule Poirot finds a murdered passenger on a train stuck in snow."),
    ("And Then There Were None", 1939, "Mystery", ["Agatha Christie"], "en", "Ten strangers on an island die one after another."),
    ("The Hound of the Baskervilles", 1902, "Mystery", ["Arthur Conan Doyle"], "en", "Sherlock Holmes investigates a family curse on the moors."),
    ("A Study in Scarlet", 1887, "Mystery", ["Arthur Conan Doyle"], "en", "Holmes and Watson meet and solve their first case together."),
    ("The Murders in the Rue Morgue", 1841, "Mystery", ["Edgar Allan Poe"], "en", "Detective Dupin solves an impossible double murder in Paris."),
    ("The Da Vinci Code", 2003, "Mystery", ["Dan Brown"], "en", "A murder in the Louvre leads to a chain of hidden codes."),
    ("The Girl with the Dragon Tattoo", 2005, "Mystery", ["Stieg Larsson"], "en", "A journalist and a hacker look for a girl missing for forty years."),
    ("Gone Girl", 2012, "Mystery", ["Gillian Flynn"], "en", "A wife disappears and her husband becomes the main suspect."),
    ("The Big Sleep", 1939, "Mystery", ["Raymond Chandler"], "en", "Private detective Philip Marlowe gets pulled into a rich family's troubles."),
    ("The Maltese Falcon", 1930, "Mystery", ["Dashiell Hammett"], "en", "Sam Spade chases a valuable statue after his partner is killed."),
    ("The Moonstone", 1868, "Mystery", ["Wilkie Collins"], "en", "A famous diamond disappears on the night of a birthday party."),
    ("The Talented Mr. Ripley", 1955, "Mystery", ["Patricia Highsmith"], "en", "A young man in Italy takes over the life of a rich friend."),
    ("In the Woods", 2007, "Mystery", ["Tana French"], "en", "A detective investigates a murder near the woods where his friends vanished."),
    ("The Girl on the Train", 2015, "Mystery", ["Paula Hawkins"], "en", "A woman sees something from her train window and gets involved."),
    ("The Silence of the Lambs", 1988, "Mystery", ["Thomas Harris"], "en", "An FBI trainee asks an imprisoned killer for help."),
    ("The Name of the Rose", 1980, "Mystery", ["Umberto Eco"], "en", "A monk investigates deaths in a medieval abbey library."),
    ("Whose Body?", 1923, "Mystery", ["Dorothy L. Sayers"], "en", "Lord Peter Wimsey finds a stranger's body in a bath."),
    ("Азазель", 1998, "Mystery", ["Борис Акунин"], "ru", "Молодой Эраст Фандорин расследует странное самоубийство."),
    # --- Non-Fiction ---
    ("Sapiens: A Brief History of Humankind", 2011, "Non-Fiction", ["Yuval Noah Harari"], "en", "How a weak ape became the ruler of the planet."),
    ("Homo Deus: A Brief History of Tomorrow", 2015, "Non-Fiction", ["Yuval Noah Harari"], "en", "What humans may want once hunger, plague and war are under control."),
    ("A Brief History of Time", 1988, "Non-Fiction", ["Stephen Hawking"], "en", "Black holes, the Big Bang and time explained for everyone."),
    ("The Grand Design", 2010, "Non-Fiction", ["Stephen Hawking", "Leonard Mlodinow"], "en", "Why there is a universe, according to modern physics."),
    ("Guns, Germs, and Steel", 1997, "Non-Fiction", ["Jared Diamond"], "en", "Why some societies conquered others: geography, food and disease."),
    ("Thinking, Fast and Slow", 2011, "Non-Fiction", ["Daniel Kahneman"], "en", "Two systems of thinking and the mistakes they cause."),
    ("Outliers", 2008, "Non-Fiction", ["Malcolm Gladwell"], "en", "Success depends on chance, culture and practice, not only talent."),
    ("Silent Spring", 1962, "Non-Fiction", ["Rachel Carson"], "en", "How pesticides harm nature; a book that started a movement."),
    ("Cosmos", 1980, "Non-Fiction", ["Carl Sagan"], "en", "A personal journey through the universe and the history of science."),
    ("The Selfish Gene", 1976, "Non-Fiction", ["Richard Dawkins"], "en", "Evolution seen from the point of view of genes."),
    ("A Short History of Nearly Everything", 2003, "Non-Fiction", ["Bill Bryson"], "en", "Science from the Big Bang to people, told with humour."),
    ("Atomic Habits", 2018, "Non-Fiction", ["James Clear"], "en", "Small daily changes that add up to big results."),
    ("Quiet", 2012, "Non-Fiction", ["Susan Cain"], "en", "The strengths of introverts in a world that loves talking."),
    ("On the Origin of Species", 1859, "Non-Fiction", ["Charles Darwin"], "en", "The theory of evolution by natural selection."),
    ("Freakonomics", 2005, "Non-Fiction", ["Steven Levitt", "Stephen J. Dubner"], "en", "An economist uses data to answer unusual questions."),
    ("How to Win Friends and Influence People", 1936, "Non-Fiction", ["Dale Carnegie"], "en", "Simple rules for getting along with people."),
    ("Man's Search for Meaning", 1946, "Non-Fiction", ["Viktor Frankl"], "en", "A psychiatrist survives the camps and writes about finding meaning."),
    ("The Wealth of Nations", 1776, "Non-Fiction", ["Adam Smith"], "en", "The classic study of markets, work and trade."),
    ("Аз и Я", 1975, "Non-Fiction", ["Олжас Сулейменов"], "ru", "Смелый взгляд на «Слово о полку Игореве» и тюркские слова в нём."),
    # --- Biography ---
    ("Steve Jobs", 2011, "Biography", ["Walter Isaacson"], "en", "The life of the Apple co-founder, based on many interviews."),
    ("Einstein: His Life and Universe", 2007, "Biography", ["Walter Isaacson"], "en", "The man behind the theory of relativity."),
    ("Becoming", 2018, "Biography", ["Michelle Obama"], "en", "From the South Side of Chicago to the White House."),
    ("The Diary of a Young Girl", 1947, "Biography", ["Anne Frank"], "en", "A Jewish girl's diary written while hiding in Amsterdam."),
    ("Long Walk to Freedom", 1994, "Biography", ["Nelson Mandela"], "en", "Mandela's own story of prison and the end of apartheid."),
    ("The Autobiography of Malcolm X", 1965, "Biography", ["Malcolm X", "Alex Haley"], "en", "The life and change of an American civil rights leader."),
    ("Alexander Hamilton", 2004, "Biography", ["Ron Chernow"], "en", "The founding father who built the American financial system."),
    ("Educated", 2018, "Biography", ["Tara Westover"], "en", "A girl who never went to school earns a PhD at Cambridge."),
    ("Elon Musk", 2015, "Biography", ["Ashlee Vance"], "en", "The story of an entrepreneur behind electric cars and rockets."),
    ("The Autobiography of Benjamin Franklin", 1791, "Biography", ["Benjamin Franklin"], "en", "Franklin tells how a printer's apprentice became a statesman."),
    ("I Know Why the Caged Bird Sings", 1969, "Biography", ["Maya Angelou"], "en", "Childhood memories of a poet growing up in the American South."),
    ("Shoe Dog", 2016, "Biography", ["Phil Knight"], "en", "How Nike started with a car full of running shoes."),
    ("Born a Crime", 2016, "Biography", ["Trevor Noah"], "en", "Growing up mixed-race in South Africa under apartheid."),
    ("When Breath Becomes Air", 2016, "Biography", ["Paul Kalanithi"], "en", "A young neurosurgeon faces his own terminal illness."),
    ("The Immortal Life of Henrietta Lacks", 2010, "Biography", ["Rebecca Skloot"], "en", "The woman whose cells changed medicine without her knowing."),
    ("The Story of My Life", 1903, "Biography", ["Helen Keller"], "en", "A deaf and blind girl learns to read, write and speak."),
    ("The Story of My Experiments with Truth", 1927, "Biography", ["Mahatma Gandhi"], "en", "Gandhi describes his life and his ideas of non-violence."),
]

# ---------------------------------------------------------------------
# Name pools for synthetic members
# ---------------------------------------------------------------------
KK_MALE = ["Ерлан", "Нұрлан", "Дәурен", "Ғалым", "Қуаныш", "Аңсар", "Өмірзақ", "Бауыржан", "Әлішер", "Шаһмардан", "Ерғали", "Мұрат"]
KK_FEMALE = ["Әлия", "Айгерім", "Мөлдір", "Ұлжан", "Үміт", "Іңкәр", "Гүлнұр", "Аружан", "Сәуле", "Жанар", "Дана", "Ақбота"]
KK_SURNAMES = [("Сәрсенбаев", "Сәрсенбаева"), ("Қасымов", "Қасымова"), ("Нұрғалиев", "Нұрғалиева"),
               ("Өтебаев", "Өтебаева"), ("Тұрсынов", "Тұрсынова"), ("Жұмабеков", "Жұмабекова"),
               ("Әбдірахманов", "Әбдірахманова"), ("Құдайбергенов", "Құдайбергенова"),
               ("Серікұлы", "Серікқызы"), ("Ахметұлы", "Ахметқызы"), ("Бекұлы", "Бекқызы")]
RU_MALE = ["Дмитрий", "Иван", "Сергей", "Алексей", "Андрей", "Михаил", "Никита", "Артём"]
RU_FEMALE = ["Анна", "Екатерина", "Ольга", "Мария", "Наталья", "Татьяна", "Юлия", "Ксения"]
RU_SURNAMES = [("Иванов", "Иванова"), ("Смирнов", "Смирнова"), ("Кузнецов", "Кузнецова"),
               ("Попов", "Попова"), ("Соколов", "Соколова"), ("Лебедев", "Лебедева"),
               ("Морозов", "Морозова"), ("Волков", "Волкова")]
EN_MALE = ["James", "Daniel", "Michael", "Thomas", "William", "Oliver"]
EN_FEMALE = ["Emily", "Sarah", "Olivia", "Emma", "Sophie", "Grace"]
EN_SURNAMES = [("Smith", "Smith"), ("Johnson", "Johnson"), ("Brown", "Brown"), ("Wilson", "Wilson"),
               ("Taylor", "Taylor"), ("Clark", "Clark"), ("Walker", "Walker")]
LAT_MALE = ["Dias", "Alikhan", "Timur", "Arman", "Nursultan"]
LAT_FEMALE = ["Aruzhan", "Dana", "Madina", "Aigerim", "Kamila"]
LAT_SURNAMES = [("Sadykov", "Sadykova"), ("Akhmetov", "Akhmetova"), ("Bekov", "Bekova"),
                ("Omarov", "Omarova"), ("Kim", "Kim"), ("Zhaksylykov", "Zhaksylykova")]

# (male names, female names, surnames, share of members)
NAME_GROUPS = [
    (KK_MALE, KK_FEMALE, KK_SURNAMES, 0.40),
    (RU_MALE, RU_FEMALE, RU_SURNAMES, 0.25),
    (EN_MALE, EN_FEMALE, EN_SURNAMES, 0.15),
    (LAT_MALE, LAT_FEMALE, LAT_SURNAMES, 0.20),
]

CITIES = {
    "Алматы": ["Абай даңғылы", "Достық даңғылы", "Әл-Фараби даңғылы", "Төле би көшесі", "улица Жибек Жолы"],
    "Астана": ["Республика даңғылы", "Қабанбай батыр даңғылы", "Сарыарқа даңғылы", "улица Кенесары"],
    "Шымкент": ["Тәуке хан даңғылы", "Байтұрсынұлы көшесі", "улица Казыбек би"],
    "Қызылорда": ["Абай даңғылы", "Әйтеке би көшесі", "Желтоқсан көшесі"],
    "Қарағанды": ["Бұқар жырау даңғылы", "улица Ерубаева", "Гоголь көшесі"],
    "Павлодар": ["улица Торайгырова", "Естай көшесі"],
    "Өскемен": ["улица Казахстан", "Ушанов көшесі"],
}

PHONE_PREFIXES = ["701", "702", "705", "707", "747", "771", "775", "777", "778"]

COMMENTS = {
    5: ["Absolutely loved it.", "One of the best books I have read.", "Керемет кітап, бәріне ұсынамын!",
        "Прочитал(а) на одном дыхании.", "Шедевр, перечитаю ещё раз.", "Өте әсерлі, ұнады."],
    4: ["Very good, a few slow chapters.", "Really enjoyed the characters.", "Хорошая книга, советую.",
        "Жақсы кітап, оқуға тұрарлық.", "Интересно и умно написано."],
    3: ["Good idea, average writing.", "Not bad, not great.", "Нормально, но ожидал(а) большего.",
        "Орташа, кейбір жерлері қызық."],
    2: ["Too long for me.", "Hard to finish.", "Скучновато.", "Маған онша ұнамады."],
    1: ["Not my kind of book.", "Совсем не понравилось.", "Мүлдем ұнамады."],
}

TRANSLIT = {
    "а": "a", "ә": "a", "б": "b", "в": "v", "г": "g", "ғ": "g", "д": "d", "е": "e", "ё": "yo",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "қ": "q", "л": "l", "м": "m", "н": "n",
    "ң": "ng", "о": "o", "ө": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ұ": "u",
    "ү": "u", "ф": "f", "х": "kh", "һ": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "shch",
    "ъ": "", "ы": "y", "і": "i", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
class Raw(str):
    """A SQL expression written as is, e.g. current_date - 5."""


def sql_value(value):
    # Python value -> SQL literal
    if value is None:
        return "NULL"
    if isinstance(value, Raw):
        return value
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def insert(table, columns, rows):
    # One INSERT statement with many rows
    lines = [f"INSERT INTO {table} ({', '.join(columns)}) VALUES"]
    values = ["    (" + ", ".join(sql_value(v) for v in row) + ")" for row in rows]
    return "\n".join(lines) + "\n" + ",\n".join(values) + ";\n"


def to_ascii(text):
    # Cyrillic/Kazakh -> Latin letters for e-mail addresses
    result = "".join(TRANSLIT.get(ch, ch) for ch in text.lower())
    return "".join(ch for ch in result if "a" <= ch <= "z")


def days_ago(n):
    # A date n days before the day the seed is loaded (negative n = in the future)
    if n < 0:
        return Raw(f"current_date + {-n}")
    return Raw(f"current_date - {n}")


# ---------------------------------------------------------------------
# Build the data
# ---------------------------------------------------------------------
def build():
    data = {}

    data["category"] = [(i + 1, name) for i, name in enumerate(CATEGORIES)]
    category_id = {name: i + 1 for i, name in enumerate(CATEGORIES)}

    data["librarian"] = [(i + 1, name, email) for i, (name, email) in enumerate(LIBRARIANS)]

    data["publisher"] = [(i + 1, name, country) for i, (name, country, lang) in enumerate(PUBLISHERS)]
    publishers_by_lang = {}
    for i, (name, country, lang) in enumerate(PUBLISHERS):
        publishers_by_lang.setdefault(lang, []).append(i + 1)

    author_names = list(AUTHORS)
    author_id = {name: i + 1 for i, name in enumerate(author_names)}
    data["author"] = [(author_id[n], n, AUTHORS[n][0], AUTHORS[n][1]) for n in author_names]

    # Books: Kazakh books get Kazakh publishers, Russian ones Russian publishers
    data["book"] = []
    data["book_author"] = []
    total_copies = {}
    for i, (title, year, genre, authors, lang, description) in enumerate(BOOKS):
        book_id = i + 1
        total_copies[book_id] = random.randint(1, 5)
        data["book"].append([
            book_id, title, year, None, category_id[genre],
            random.choice(publishers_by_lang[lang]), description, None,
            random.random() < 0.15, total_copies[book_id], None,  # available is set later
        ])
        for name in authors:
            data["book_author"].append((len(data["book_author"]) + 1, book_id, author_id[name]))

    # Members with names in Kazakh, Russian and English
    data["member"] = []
    used_names = set()
    used_emails = set()
    city_names = list(CITIES)
    while len(data["member"]) < 125:
        male, female, surnames, share = random.choices(NAME_GROUPS, weights=[g[3] for g in NAME_GROUPS])[0]
        is_female = random.random() < 0.5
        first = random.choice(female if is_female else male)
        last = random.choice(surnames)[1 if is_female else 0]
        # first and last name are stored separately; the pair must be unique
        if (first, last) in used_names:
            continue
        used_names.add((first, last))

        # E-mails are lower case, so they are also unique ignoring case
        email = f"{to_ascii(first)}.{to_ascii(last)}{random.randint(1, 99)}@example.com"
        if email in used_emails:
            continue
        used_emails.add(email)

        city = street = None
        if random.random() < 0.85:  # most members have an address
            city = random.choice(city_names)
            street = f"{random.choice(CITIES[city])}, {random.randint(1, 180)}"

        registered = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 364), hours=random.randint(8, 20))
        member_id = len(data["member"]) + 1
        data["member"].append((member_id, None, first, last, email, random.randint(1960, 2006),
                               city, street, registered.strftime("%Y-%m-%d %H:%M:%S")))
    member_ids = [m[0] for m in data["member"]]

    # Phones: everybody has one, about a third have a second one
    data["member_phone"] = []
    for member_id in member_ids:
        count = 2 if random.random() < 0.33 else 1
        phones = set()
        while len(phones) < count:
            phones.add("+7" + random.choice(PHONE_PREFIXES) + f"{random.randint(0, 9999999):07d}")
        for phone in sorted(phones):
            data["member_phone"].append((len(data["member_phone"]) + 1, member_id, phone))

    # Loans: returned, active (due in the future) and overdue (due in the past).
    # Active + overdue loans of a book never exceed its total copies.
    data["loan"] = []
    active = {book_id: 0 for book_id in total_copies}
    active_pairs = set()
    returned_pairs = []
    librarian_ids = [l[0] for l in data["librarian"]]
    while len(data["loan"]) < 180:
        kind = random.choices(["returned", "active", "overdue"], weights=[60, 22, 18])[0]
        book_id = random.choice(list(total_copies))
        member_id = random.choice(member_ids)
        librarian = random.choice(librarian_ids)
        if kind == "returned":
            n = random.randint(30, 680)          # loan_date = n days ago
            length = random.randint(3, 25)       # returned after this many days
            row = (book_id, member_id, librarian, days_ago(n), days_ago(n - 14), days_ago(n - length))
            returned_pairs.append((book_id, member_id))
        else:
            if active[book_id] >= total_copies[book_id] or (book_id, member_id) in active_pairs:
                continue
            n = random.randint(0, 13) if kind == "active" else random.randint(20, 300)
            row = (book_id, member_id, librarian, days_ago(n), days_ago(n - 14), None)
            active[book_id] += 1
            active_pairs.add((book_id, member_id))
        data["loan"].append((len(data["loan"]) + 1,) + row)

    # available copies = total copies - copies that are still out
    for book in data["book"]:
        book[10] = total_copies[book[0]] - active[book[0]]

    # Reservations: one pending reservation per member and book at most
    data["reservation"] = []
    pending_pairs = set()
    while len(data["reservation"]) < 110:
        book_id = random.choice(list(total_copies))
        member_id = random.choice(member_ids)
        status = random.choices(["pending", "fulfilled", "cancelled"], weights=[35, 40, 25])[0]
        if status == "pending":
            if (book_id, member_id) in pending_pairs or (book_id, member_id) in active_pairs:
                continue
            pending_pairs.add((book_id, member_id))
        reserved_at = Raw(f"now() - interval '{random.randint(1, 400)} days'")
        data["reservation"].append((len(data["reservation"]) + 1, book_id, member_id, reserved_at, status))

    # Reviews: mostly by people who returned the book; unique (book, member)
    data["review"] = []
    reviewed = set()
    while len(data["review"]) < 170:
        if returned_pairs and random.random() < 0.6:
            book_id, member_id = random.choice(returned_pairs)
        else:
            book_id, member_id = random.choice(list(total_copies)), random.choice(member_ids)
        if (book_id, member_id) in reviewed:
            continue
        reviewed.add((book_id, member_id))
        rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 20, 35, 30])[0]
        created_at = Raw(f"now() - interval '{random.randint(1, 600)} days'")
        data["review"].append((len(data["review"]) + 1, book_id, member_id, rating,
                               random.choice(COMMENTS[rating]), created_at))
    return data


# ---------------------------------------------------------------------
# Write seed.sql
# ---------------------------------------------------------------------
# book.is_recommended is not written here: the database default (false) is
# used, and post_seed_covers.sql marks the 12 "Recommended by Tamer" books.
COLUMNS = {
    "category": ["category_id", "name"],
    "librarian": ["librarian_id", "full_name", "email"],
    "publisher": ["publisher_id", "name", "country"],
    "author": ["author_id", "full_name", "birth_year", "country"],
    "book": ["book_id", "title", "publication_year", "isbn", "category_id", "publisher_id",
             "description", "cover_url", "is_bestseller", "total_copies", "available_copies"],
    "book_author": ["book_author_id", "book_id", "author_id"],
    "member": ["member_id", "user_id", "first_name", "last_name", "email", "birth_year",
               "city", "street", "registered_at"],
    "member_phone": ["member_phone_id", "member_id", "phone"],
    "loan": ["loan_id", "book_id", "member_id", "librarian_id", "loan_date", "due_date", "return_date"],
    "reservation": ["reservation_id", "book_id", "member_id", "reserved_at", "status"],
    "review": ["review_id", "book_id", "member_id", "rating", "comment", "created_at"],
}


def main():
    data = build()

    parts = [
        "-- Run order: 2 of 5 (schema -> seed -> procedures -> security -> post_seed_covers); "
        "queries.sql, structure.sql and call_functions.sql can run any time after step 4\n"
        "-- GENERATED by db/generate_seed.py (random.seed(42)). Do not edit by hand.\n"
        "-- Synthetic demo data: real books and authors, invented members and activity.\n"
        "-- Run after schema.sql. Safe to re-run: the tables are emptied first.\n"
        "-- Loan dates are relative to current_date, so overdue loans stay overdue.\n",
        "TRUNCATE review, reservation, loan, member_phone, member, librarian,\n"
        "         book_author, book, author, publisher, category RESTART IDENTITY CASCADE;\n",
    ]
    for table, columns in COLUMNS.items():
        parts.append(f"-- {table}: {len(data[table])} rows\n" + insert(table, columns, data[table]))

    # We inserted explicit ids, so move every identity counter past them
    parts.append("-- Continue the id counters after the inserted rows")
    for table, columns in COLUMNS.items():
        key = columns[0]
        parts.append(f"SELECT setval(pg_get_serial_sequence('{table}', '{key}'), "
                     f"(SELECT max({key}) FROM {table}));")

    OUT.write_text("\n".join(parts) + "\n", encoding="utf-8", newline="\n")

    print(f"Wrote {OUT}")
    for table in COLUMNS:
        print(f"  {table:13} {len(data[table]):4}")


if __name__ == "__main__":
    main()
