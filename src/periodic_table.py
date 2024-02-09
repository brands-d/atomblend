from json import load
from pathlib import Path


class PeriodicTable:
    """
    A class representing a periodic table.

    Attributes:
        elements_directory (Path): The directory path to the elements resource files.

    Methods:
        __init__(): Initializes an instance of the PeriodicTable class.
        __getitem__(symbol): Retrieves an element from the periodic table by its symbol.
    """

    elements_directory = Path(__file__).parent / "resources" / "elements"

    def __init__(self):
        """
        Initializes an instance of the PeriodicTable class.
        """
        self.elements = {}

    def __getitem__(self, symbol):
        """
        Retrieves an element from the periodic table by its symbol.

        Args:
            symbol (str): The symbol of the element.

        Returns:
            Element: The element object corresponding to the symbol.
        """
        if symbol not in self.elements:
            self.elements.update({symbol: Element(symbol)})

        return self.elements[symbol]


class Element:
    """
    A class representing an element in the periodic table.

    Attributes:
        name (str): The name of the element.
        symbol (str): The symbol of the element.
        radius (float): The radius of the element.
        covalent_radius (float): The covalent radius of the element.

    Methods:
        __init__(symbol): Initializes an instance of the Element class.
        load(symbol): Loads the element data from the JSON file.
        parse(data): Parses the element data and assigns the attributes.
    """

    def __init__(self, symbol):
        """
        Initializes an instance of the Element class.

        Args:
            symbol (str): The symbol of the element.
        """
        self.parse(self.load(symbol))

    def load(self, symbol):
        """
        Loads the element data from the JSON file.

        Args:
            symbol (str): The symbol of the element.

        Returns:
            dict: The element data as a dictionary.

        Raises:
            KeyError: If the element data cannot be found.
        """

        def _load(path):
            with open(path) as file:
                data = load(file)

            for element in data:
                if element["symbol"] == symbol:
                    return element

            raise KeyError

        try:
            return _load(PeriodicTable.elements_directory / f"elements_user.json")
        except KeyError:
            try:
                return _load(PeriodicTable.elements_directory / f"elements.json")
            except KeyError:
                symbol = "X"
                return _load(PeriodicTable.elements_directory / f"elements.json")

    def parse(self, data):
        """
        Parses the element data and assigns the attributes.

        Args:
            data (dict): The element data as a dictionary.
        """
        self.name = data["name"]
        self.symbol = data["symbol"]
        self.radius = data["radius"]
        self.covalent_radius = data["covalent radius"]


PeriodicTable = PeriodicTable()
