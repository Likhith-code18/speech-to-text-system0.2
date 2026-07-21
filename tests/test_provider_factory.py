@pytest.mark.parametrize("provider_name", ["deepgram", "google"])
def test_planned_providers_raise_not_implemented(provider_name):
    with pytest.raises(NotImplementedError):
        create_speech_provider(provider_name, _FakeConfig())