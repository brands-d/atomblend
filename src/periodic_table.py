from json import load
from pathlib import Path


class PeriodicTable:
    """
    A class representing the periodic table. Mainly for internal use.
    """

    elements_directory = Path(__file__).parent / "resources" / "elements"
    elements_file = elements_directory / "elements.json"
    elements_user_file = elements_directory / f"elements_user.json"

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
        name (str): The name of the element (i.e. Hydrogen).
        symbol (str): The symbol of the element (i.e. H).
        radius (float): The radius of the element in Angstrom. Default is half of the covalent radius.
        covalent_radius (float): The covalent radius of the element in Angstrom. Source: https://en.wikipedia.org/wiki/Atomic_radius.
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
        Loads the element data from the JSON file(s). User file is preferred.

        Note:
            If unknown element is loaded, it will default to the element with dummy element called Veritasium with the symbol "X".

        Args:
            symbol (str): The symbol of the element.

        Returns:
            dict: The element data as a dictionary.
        """

        def _load(path):
            with open(path) as file:
                data = load(file)

            for element in data:
                if element["symbol"] == symbol:
                    return element

            raise KeyError

        try:
            return _load(PeriodicTable.elements_user_file)
        except KeyError:
            try:
                return _load(PeriodicTable.elements_file)
            except KeyError:
                symbol = "X"
                return _load(PeriodicTable.elements_file)

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
