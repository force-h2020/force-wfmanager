from force_bdss.api import BaseUIHooksFactory, BaseUIHooksManager


class NullUIHookManager(BaseUIHooksManager):
    def __init__(self, *args, **kwargs):
        super(NullUIHookManager, self).__init__(*args, **kwargs)

        self.before_execution_called = False
        self.after_execution_called = False
        self.before_save_called = False

    def before_execution(self, task):
        self.before_execution_called = True

    def after_execution(self, task):
        self.after_execution_called = True

    def before_save(self, task):
        self.before_save_called = True


class NullUIHookFactory(BaseUIHooksFactory):
    def create_ui_hooks_manager(self):
        return NullUIHookManager(self)
