"""Security regression tests for local inference redirects."""

import unittest
from urllib.error import HTTPError
from urllib.request import Request, build_opener

from aurex.local_inference import LocalInferenceError, _NoRedirect


class RedirectSecurityTests(unittest.TestCase):

    def test_redirect_handler_rejects_redirects(self):
        handler = _NoRedirect()

        for code in (301, 302, 303, 307, 308):
            with self.subTest(code=code):
                with self.assertRaises(LocalInferenceError):
                    getattr(handler, f"http_error_{code}")(
                        Request("http://127.0.0.1:8080"),
                        None,
                        code,
                        "Redirect",
                        {},
                    )

    def test_custom_opener_contains_redirect_handler(self):
        opener = build_opener(_NoRedirect)

        self.assertTrue(
            any(isinstance(h, _NoRedirect) for h in opener.handlers)
        )


if __name__ == "__main__":
    unittest.main()
