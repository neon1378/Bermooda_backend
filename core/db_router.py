
class MultiDBRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'mongo':
            return 'mongo'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'mongo':
            return 'mongo'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True  # Allow relations across databases

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'mongo':
            return db == 'mongo'
        return db == 'default'
