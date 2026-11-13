import io
import json
import unittest
from urllib.error import HTTPError

from tr_auto.paper_healthcheck import PaperConnectionError, inspect_paper_account


class ReadOnlyPaperCheckTests(unittest.TestCase):
    def test_only_paper_host_get_no_body(self):
        def mock_open(request, timeout):
            self.assertEqual(request.full_url, "https://paper-api.alpaca.markets/v2/account")
            self.assertEqual(request.get_method(), "GET")
            self.assertIsNone(request.data)
            self.assertEqual(timeout, 10)
            self.assertEqual(request.get_header("Apca-api-key-id"), "test-key")
            return io.BytesIO(json.dumps({"status": "ACTIVE", "shorting_enabled": True}).encode())
        result = inspect_paper_account("test-key", "test-secret", opener=mock_open)
        self.assertEqual(result.status, "ACTIVE")
        self.assertTrue(result.shorting_enabled)

    def test_missing_key_does_not_connect(self):
        with self.assertRaises(PaperConnectionError):
            inspect_paper_account("", "secret", opener=lambda *_args, **_kwargs: self.fail("network touched"))

    def test_http_error_does_not_leak_credentials(self):
        def mock_open(_request, timeout):
            raise HTTPError("https://paper-api.alpaca.markets/v2/account", 401, "token bad", {}, None)
        with self.assertRaisesRegex(PaperConnectionError, "HTTP 401") as caught:
            inspect_paper_account("a-test-key", "secret-value", opener=mock_open)
        self.assertNotIn("secret-value", str(caught.exception))

    def test_invalid_account_response_fails(self):
        with self.assertRaises(PaperConnectionError):
            inspect_paper_account("key", "secret", opener=lambda *_a, **_kw: io.BytesIO(b'{}'))


if __name__ == "__main__":
    unittest.main()
