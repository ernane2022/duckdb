class DatabaseRouter:
    """
    Router para múltiplos databases do benchmark
    """
    
    def db_for_read(self, model, **hints):
        """Retorna None para permitir escolha manual do database"""
        return None
    
    def db_for_write(self, model, **hints):
        """Retorna None para permitir escolha manual do database"""
        return None
    
    def allow_relation(self, obj1, obj2, **hints):
        """Permite relações entre objetos"""
        return True
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Permite migrações em todos os databases para o app benchmark"""
        if app_label == 'benchmark_app':
            return True
        return None