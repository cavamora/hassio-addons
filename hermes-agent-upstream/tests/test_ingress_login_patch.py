"""Regression contract for the HA Ingress dashboard-login wrapper patch."""

from pathlib import Path
import unittest


DOCKERFILE = Path(__file__).parents[1] / "Dockerfile"


class IngressLoginPatchTests(unittest.TestCase):
    def test_password_login_and_return_path_remain_under_ingress_prefix(self):
        dockerfile = DOCKERFILE.read_text(encoding="utf-8")

        # A leading slash escapes Home Assistant's dynamic ingress path.  The
        # login page must post relatively, and the backend must prepend the
        # proxy prefix when returning the authenticated browser to the app.
        self.assertIn("fetch('auth/password-login'", dockerfile)
        self.assertIn(
            'return f"{_prefix(request)}{(_validate_post_login_target(next_raw) or "/")}", False',
            dockerfile,
        )

    def test_oauth_login_link_is_relative_to_the_ingress_path(self):
        dockerfile = DOCKERFILE.read_text(encoding="utf-8")

        self.assertIn('href="auth/login?provider=', dockerfile)


if __name__ == "__main__":
    unittest.main()
