class PriceFeedRouter:
    """
    A database router to route `Index` model operations to the `market_data` database.
    """
    def db_for_read(self, model, **hints):
        """
        Point read operations for specific models to the `market_data` database.
        """
        if model._meta.app_label == 'price_feed_app':  # Replace with your app's name
            return 'market_data'
        return None

    def db_for_write(self, model, **hints):
        """
        Point write operations for specific models to the `market_data` database.
        """
        if model._meta.app_label == 'price_feed_app':  # Replace with your app's name
            return 'market_data'
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure only the `market_data` database is used for specific models.
        """
        if app_label == 'price_feed_app':  # Replace with your app's name
            return db == 'market_data'
        return None
