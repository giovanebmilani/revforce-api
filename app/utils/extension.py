class Extension:
    @staticmethod
    def try_parse_to_int(val):
        try:
            return int(val)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def try_parse_to_float(val):
        try:
            return float(val)
        except (ValueError, TypeError):
            return None
