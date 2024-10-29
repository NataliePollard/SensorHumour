PRINTER = "printer"
AUDIO = "audio"
DOLLHOUSE = "dollhouse"
OTHER1 = "other1"
OTHER2 = "other2"
OTHER3 = "other3"
SCALE = "scale"


def getDefaultTagData():
    return {
        [PRINTER]: False,
        [AUDIO]: False,
        [DOLLHOUSE]: False,
        [OTHER1]: False,
        [OTHER2]: False,
        [OTHER3]: False,
        [SCALE]: False,
    }


class TagData(object):
    printer = False
    audio = False
    dollhouse = False
    other1 = False
    other2 = False
    other3 = False
    scale = False

    def __init__(self, tag_data_string=None):
        self.update_data(tag_data_string)

    def update_data(self, tag_data_str):
        if not is_valid_tag_data_string(tag_data_str):
            return
        tag_data_str = tag_data_str.split("|")
        self.printer = bool(int(tag_data_str[0]))
        self.audio = bool(int(tag_data_str[1]))
        self.dollhouse = bool(int(tag_data_str[2]))
        self.other1 = bool(int(tag_data_str[3]))
        self.other2 = bool(int(tag_data_str[4]))
        self.other3 = bool(int(tag_data_str[5]))
        self.scale = bool(int(tag_data_str[6]))

    def serialize(self):
        def get_prop(prop):
            if prop is None or prop is False:
                return 0
            return 1

        return f"{get_prop(self.printer)}|{get_prop(self.audio)}|{get_prop(self.dollhouse)}|{get_prop(self.other1)}|{get_prop(self.other2)}|{get_prop(self.other3)}|{get_prop(self.scale)}"


def is_valid_tag_data_string(tag_data_string):
    if tag_data_string is None:
        return False
    tag_data = tag_data_string.split("|")
    if len(tag_data) != 7:
        return False
    return True
