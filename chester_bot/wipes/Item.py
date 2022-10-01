class Item:
    def __init__(self, name, id):
        self.name = name
        self.id = id

    @staticmethod
    def from_dict(raw_dict):
        return Item(raw_dict["name"], raw_dict["id"])
