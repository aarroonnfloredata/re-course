def pytest_configure(config):
    config.addinivalue_line(
        "markers", "objective(*numbers): module objectives this test checks"
    )
