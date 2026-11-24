from django.test.runner import DiscoverRunner


# The Supabase pooler keeps its own connection to a test database open,
# so Django cannot drop "test_postgres" after the tests. Instead we run the
# tests on the existing database: every TestCase test runs inside a
# transaction that is rolled back, so no test data is ever saved.
class ExistingDatabaseRunner(DiscoverRunner):
    def setup_databases(self, **kwargs):
        return None

    def teardown_databases(self, old_config, **kwargs):
        pass
