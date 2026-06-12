"""Pytest integration for StoryForge Framework."""

import pytest
from backend.testing.runners.runner import StoryTestRunner

# We can reuse the runner instance
runner = StoryTestRunner()

# Optional: Run with `--update-goldens` to capture new goldens.
# In pytest, you would add a custom CLI flag. For this V1, we can manually toggle it.
UPDATE_GOLDENS = False

@pytest.mark.smoke
@pytest.mark.regression
def test_sell_moonlight():
    result = runner.run("sell_moonlight", update_goldens=UPDATE_GOLDENS)
    assert result is True

@pytest.mark.regression
@pytest.mark.staging
def test_police_argument():
    result = runner.run("police_argument", update_goldens=UPDATE_GOLDENS)
    assert result is True

@pytest.mark.regression
@pytest.mark.crowd
def test_market_crowd():
    result = runner.run("market_crowd", update_goldens=UPDATE_GOLDENS)
    assert result is True

@pytest.mark.failure
def test_quantum_portal():
    result = runner.run("quantum_portal", update_goldens=UPDATE_GOLDENS)
    assert result is True

@pytest.mark.failure
def test_overflow_failure():
    result = runner.run("overflow_failure", update_goldens=UPDATE_GOLDENS)
    assert result is True

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    
    if "--update-goldens" in args:
        print("Running in UPDATE GOLDENS mode...")
        UPDATE_GOLDENS = True
        args.remove("--update-goldens")
        
    pytest.main([__file__, "-v"] + args)
