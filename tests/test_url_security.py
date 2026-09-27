from unittest.mock import MagicMock, patch

from data_pipeline.url_validator import validate_and_convert_url


def test_url_validator_rejects_loopback_and_private_addresses():
    for address in ("127.0.0.1", "10.0.0.8", "169.254.169.254", "::1"):
        with patch(
            "data_pipeline.url_validator.socket.getaddrinfo",
            return_value=[(None, None, None, None, (address, 0))],
        ):
            result = validate_and_convert_url("http://resume.example/file.pdf")
        assert result["is_valid"] is False


def test_url_validator_rejects_mixed_public_and_private_dns_results():
    with patch(
        "data_pipeline.url_validator.socket.getaddrinfo",
        return_value=[
            (None, None, None, None, ("93.184.216.34", 0)),
            (None, None, None, None, ("10.0.0.2", 0)),
        ],
    ):
        result = validate_and_convert_url("https://resume.example/file.pdf")
    assert result["is_valid"] is False


def test_url_validator_rejects_url_credentials_and_invalid_ports():
    assert not validate_and_convert_url("https://user:pass@example.com/a")["is_valid"]
    assert not validate_and_convert_url("https://example.com:bad/a")["is_valid"]


def test_google_drive_domain_match_does_not_accept_lookalike_hosts():
    with patch(
        "data_pipeline.url_validator.socket.getaddrinfo",
        return_value=[(None, None, None, None, ("93.184.216.34", 0))],
    ):
        result = validate_and_convert_url(
            "https://drive.google.com.attacker.example/file/d/abc"
        )
    assert result["is_valid"] is True
    assert result["download_url"].startswith(
        "https://drive.google.com.attacker.example/"
    )


def test_downloader_revalidates_redirect_target_before_request():
    from data_pipeline.resume_downloader import download_resume_in_memory

    with patch(
        "data_pipeline.resume_downloader.validate_and_convert_url",
        side_effect=[
            {"is_valid": True, "download_url": "https://public.example/a"},
            {"is_valid": False, "reason": "Restricted host"},
        ],
    ), patch("data_pipeline.resume_downloader.requests.get") as get:
        response = MagicMock()
        response.__enter__.return_value.is_redirect = True
        response.__enter__.return_value.is_permanent_redirect = False
        response.__enter__.return_value.headers = {
            "Location": "http://127.0.0.1/latest/meta-data"
        }
        get.return_value = response
        result = download_resume_in_memory("https://public.example/a")

    assert result["success"] is False
    get.assert_called_once()
