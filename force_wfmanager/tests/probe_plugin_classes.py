from traits.api import Bool
from force_bdss.api import BaseUIHooksFactory, BaseUIHooksManager


class ProbeUIHooksManager(BaseUIHooksManager):
    before_execution_called = Bool()
    after_execution_called = Bool()
    before_save_called = Bool()

    def before_execution(self, task):
        self.before_execution_called = True

    def after_execution(self, task):
        self.after_execution_called = True

    def before_save(self, task):
        self.before_save_called = True


class ProbeUIHooksFactory(BaseUIHooksFactory):
    def create_ui_hooks_manager(self):
        return ProbeUIHooksManager(self)
