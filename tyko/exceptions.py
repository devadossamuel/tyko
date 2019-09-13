class DataError(Exception):
    status_code = 500

    def __init__(self, *args, message="Problem accessing data",
                 status_code=None, payload=None, **kwargs):

        super().__init__(*args, **kwargs)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
