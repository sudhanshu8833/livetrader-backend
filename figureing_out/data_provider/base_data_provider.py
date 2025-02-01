

class BaseDataProvider:
    def __init__(self):
        self.callback = None  

    def subscribe(self, callback_function):
        """Register the logic class's callback to be called when data is available"""
        self.callback = callback_function

    def on_new_data(self, data):
        """Call the callback function whenever there is new data"""
        if self.callback:
            self.callback(data)

    def start_data_feed(self):
        """Start fetching data - this method will be overridden by subclasses"""
        pass