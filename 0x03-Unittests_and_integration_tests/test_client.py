#!/usr/bin/env python3
"""Unit tests for client.GithubOrgClient and integration tests
"""
import unittest
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
import fixtures  # Assuming fixtures.py is accessible via PYTHONPATH


class TestGithubOrgClient(unittest.TestCase):
    """Tests for GithubOrgClient (Unit Tests)"""

    @parameterized.expand([
        ("google", {"login": "google"}),  # Simplified payload for this unit test
        ("abc", {"login": "abc"}),        # Simplified payload for this unit test
    ])
    @patch("client.get_json")
    def test_org(self, org_name, expected_payload, mock_get_json):
        """Test that GithubOrgClient.org returns correct data and calls get_json once"""
        mock_get_json.return_value = expected_payload
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, expected_payload)
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    def test_public_repos_url(self):
        """Test that _public_repos_url returns the correct URL from mocked org property"""
        expected_repos_url = "https://api.github.com/orgs/testorg/repos"
        # Mock the .org property of GithubOrgClient
        with patch.object(GithubOrgClient, "org", new_callable=PropertyMock) as mock_org_property:
            # Set the return value of the mocked .org property
            mock_org_property.return_value = {"repos_url": expected_repos_url}
            client = GithubOrgClient("testorg")
            self.assertEqual(client._public_repos_url, expected_repos_url)

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """Test that public_repos returns list of repo names correctly,
        mocking _public_repos_url and get_json.
        """
        # Example payload that get_json (for repos) should return
        repos_api_payload = [
            {"name": "repo1"},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3"},
        ]
        mock_get_json.return_value = repos_api_payload

        # Mock the _public_repos_url property
        with patch.object(
            GithubOrgClient, "_public_repos_url", new_callable=PropertyMock
        ) as mock_public_repos_url_property:
            fake_repos_url = "https://fake.api/orgs/test/repos"
            mock_public_repos_url_property.return_value = fake_repos_url
            client = GithubOrgClient("test")

            # Test without license filter
            self.assertEqual(client.public_repos(), ["repo1", "repo2", "repo3"])

            # Test with license filter
            self.assertEqual(client.public_repos(license="apache-2.0"), ["repo2"])

            mock_public_repos_url_property.assert_called_once()
            mock_get_json.assert_called_once_with(fake_repos_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({"license": None}, "my_license", False),  # Repo with no license field
        ({}, "my_license", False),  # Repo with license field missing
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test that has_license returns the correct boolean"""
        self.assertEqual(GithubOrgClient.has_license(repo, license_key), expected)


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    fixtures.TEST_PAYLOAD,
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient using fixtures.
    Mocks only external calls (requests.get).
    """

    @classmethod
    def setUpClass(cls):
        """Set up class method to mock requests.get.
        This method is called once before tests in an individual class run.
        """
        if not isinstance(cls.org_payload, dict) or "login" not in cls.org_payload:
            raise ValueError("Fixture 'org_payload' must be a dict and contain 'login'.")
        if "repos_url" not in cls.org_payload:
            raise ValueError("Fixture 'org_payload' must contain 'repos_url'.")

        org_name = cls.org_payload["login"]
        cls.expected_org_url = GithubOrgClient.ORG_URL.format(org=org_name)
        cls.expected_repos_url = cls.org_payload["repos_url"]

        def mock_requests_get_side_effect(url):
            """Side effect function for mocked requests.get."""
            response_mock = Mock()
            if url == cls.expected_org_url:
                response_mock.json.return_value = cls.org_payload
            elif url == cls.expected_repos_url:
                response_mock.json.return_value = cls.repos_payload
            else:
                response_mock.status_code = 404
                response_mock.json.return_value = {
                    "message": "Not Found - URL not mocked for this test case"
                }
            return response_mock

        cls.get_patcher = patch("utils.requests.get")
        cls.mock_get = cls.get_patcher.start()
        cls.mock_get.side_effect = mock_requests_get_side_effect

    @classmethod
    def tearDownClass(cls):
        """Tear down class method to stop the patcher."""
        cls.get_patcher.stop()

    def test_public_repos_integration(self):
        """Test GithubOrgClient.public_repos against expected fixture data."""
        client = GithubOrgClient(self.org_payload["login"])
        actual_repos = client.public_repos()
        self.assertEqual(actual_repos, self.expected_repos)

    def test_public_repos_with_license_integration(self):
        """Test public_repos with license filter against expected fixture data."""
        client = GithubOrgClient(self.org_payload["login"])
        actual_repos = client.public_repos(license="apache-2.0")
        self.assertEqual(actual_repos, self.apache2_repos)


if __name__ == "__main__":
    unittest.main()
