import json
from unittest.mock import patch

from django.test import SimpleTestCase
from django.test import RequestFactory

from . import functions
from .views import _safe_login_redirect


class ProviderRecoveryTests(SimpleTestCase):
    def setUp(self):
        functions._Provider = None
        functions._provider_retry_after = 0
        functions._provider_last_error = None

    @patch("hexoweb.functions.save_setting")
    @patch("hexoweb.functions.get_provider")
    @patch("hexoweb.functions.get_setting")
    def test_recovers_provider_from_qexo_1_settings(
            self, get_setting, get_provider, save_setting):
        settings = {
            "PROVIDER": "",
            "GH_TOKEN": "secret-token",
            "GH_REPO": "owner/blog",
            "GH_REPO_BRANCH": "main",
            "GH_REPO_PATH": "blog/"
        }
        get_setting.side_effect = lambda name: settings.get(name, "")
        expected_provider = object()
        get_provider.return_value = expected_provider

        result = functions.Provider(force_refresh=True)

        self.assertIs(result, expected_provider)
        get_provider.assert_called_once_with(
            "github",
            token="secret-token",
            repo="owner/blog",
            branch="main",
            path="blog/",
            config="Hexo"
        )
        saved_config = json.loads(save_setting.call_args.args[1])
        self.assertEqual(saved_config["params"]["path"], "blog/")
        self.assertEqual(saved_config["params"]["config"], "Hexo")

    @patch("hexoweb.functions.save_setting")
    @patch("hexoweb.functions.get_provider")
    @patch("hexoweb.functions.get_setting")
    def test_repairs_python_dict_provider_value(
            self, get_setting, get_provider, save_setting):
        get_setting.side_effect = lambda name: {
            "PROVIDER": "{'provider': 'github', 'params': {'token': 't', "
                        "'repo': 'o/r', 'branch': 'master', 'path': ''}}"
        }.get(name, "")
        expected_provider = object()
        get_provider.return_value = expected_provider

        result = functions.Provider(force_refresh=True)

        self.assertIs(result, expected_provider)
        self.assertEqual(get_provider.call_args.kwargs["config"], "Hexo")
        json.loads(save_setting.call_args.args[1])

    @patch("hexoweb.functions.get_provider", side_effect=TimeoutError("timeout"))
    @patch("hexoweb.functions.get_setting")
    def test_provider_failure_is_degraded_and_rate_limited(
            self, get_setting, get_provider):
        config = {
            "provider": "github",
            "params": {
                "token": "t",
                "repo": "o/r",
                "branch": "main",
                "path": "",
                "config": "Hexo"
            }
        }
        get_setting.side_effect = lambda name: json.dumps(config) if name == "PROVIDER" else ""

        self.assertIsNone(functions.Provider(force_refresh=True))
        self.assertIsNone(functions.Provider())
        self.assertEqual(get_provider.call_count, 1)
        self.assertIn("TimeoutError", functions.get_provider_error())


class LoginRedirectTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_decodes_local_root_redirect(self):
        request = self.factory.get("/login/?next=%2F")

        self.assertEqual(_safe_login_redirect(request), "/")

    def test_rejects_external_redirect(self):
        request = self.factory.get("/login/?next=https%3A%2F%2Fevil.example")

        self.assertEqual(_safe_login_redirect(request), "/")

# Create your tests here.
