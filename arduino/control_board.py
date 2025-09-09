from chat.arduino_util import chat_solver, smart_describe

class ControlBoard:
    def __init__(self):
        self.components = []


class Component:
    def __init__(self, name, log_len=5):
        self.name = name

        self.context = None
        self.expiring_context = False

        # rounding, filters, etc
        self.transform_function = None

        self.component_log = []
        self.log_len = log_len

    def reprogram(self, context, is_expiring, lambda_string):
        self.context = context
        self.expiring_context = is_expiring

        lambda_function = eval(lambda_string)
        self.transform_function = lambda_function

    def live_filter(self):
        state = yield
        if self.context:
            if self.transform_function:
                state = self.transform_function(state)

            # forward to chat solver with context
            loggable = yield from chat_solver(state)
            self.log(loggable)
            yield loggable

            if self.expiring_context:
                self.context = None

    def _to_dict(self):
        # make a json of all states
        return {}

    def smart_describe(self):
        return smart_describe(self._to_dict())

    def log(self, message):
        if len(self.component_log) > self.log_len:
            self.component_log.pop(0)
        self.component_log.append(message)

# component_listener = component.live_filter()