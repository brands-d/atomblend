from json import load
from pathlib import Path

# References:
# Atomic radii: 10.1063/1.1725697
# Color: CPK variant jmol


class PeriodicTable:
    elements_directory = Path(__file__).parent / "resources" / "elements"

    def __init__(self):
        self.elements = {}

    def __getitem__(self, symbol):
        if symbol not in self.elements:
            self.elements.update({symbol: Element(symbol)})

        return self.elements[symbol]


class Element:
    def __init__(self, symbol):
        self.parse(self.load(symbol))

    def load(self, symbol):
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
        self.name = data["name"]
        self.symbol = data["symbol"]
        self.radius = data["radius"]
        self.covalent_radius = data["covalent radius"]


PeriodicTable = PeriodicTable()
