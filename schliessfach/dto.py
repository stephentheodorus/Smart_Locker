class UserDTO:
    def __init__(self, id, name, email, last_pickup):
        self.id = id
        self.name = name
        self.email = email
        self.last_pickup = last_pickup

class AvgItemTypeTimeDTO:
    def __init__(self, item_type, avg_time):
        self.item_type = item_type
        self.avg_time = avg_time

class AvgItemSizeTimeDTO:
    def __init__(self, item_size, avg_time):
        self.item_size = item_size
        self.avg_time = avg_time