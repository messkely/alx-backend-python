#!/usr/bin/env python3
"""
File: test_client.py
Unit tests for GithubOrgClient with integration testing.
"""

import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient."""

    @parameterized.expand([
        ('google', {'message': 'success'}),
        ('abc', {'message': 'success'}),
    ])
    def test_org_property_returns_expected_data(self, org_name, expected_response):
        with patch('client.get_json', return_value=expected_response) as mock_get_json:
            client = GithubOrgClient(org_name)
            actual_response = client.org

            self.assertEqual(actual_response, expected_response)
            mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")

    def test_public_repos_url_property(self):
        expected_url = 'https://api.github.com/orgs/google/repos'
        with patch.object(GithubOrgClient, 'org', new_callable=PropertyMock) as mock_org:
            mock_org.return_value = {'repos_url': expected_url}
            client = GithubOrgClient('google')

            actual_url = client._public_repos_url

            self.assertEqual(actual_url, expected_url)
            mock_org.assert_called_once()

    @patch('client.get_json')
    def test_public_repos_returns_repo_names(self, mock_get_json):
        mock_repos_payload = [{"name": "repo1"}, {"name": "repo2"}]
        mock_get_json.return_value = mock_repos_payload
        expected_repo_names = ['repo1', 'repo2']
        repos_url = 'https://api.github.com/orgs/google/repos'

        with patch.object(GithubOrgClient, '_public_repos_url', new_callable=PropertyMock) as mock_url_property:
            mock_url_property.return_value = repos_url
            client = GithubOrgClient('google')

            actual_repo_names = client.public_repos()

            self.assertEqual(actual_repo_names, expected_repo_names)
            mock_url_property.assert_called_once()
            mock_get_json.assert_called_once_with(repos_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license_method(self, repo_data, license_key, expected_result):
        result = GithubOrgClient.has_license(repo_data, license_key)
        self.assertEqual(result, expected_result)


@parameterized_class(
    ('org_payload', 'repos_payload', 'expected_repos', 'apache2_repos'),
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient with mocked requests.get"""

    @classmethod
    def setUpClass(cls):
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()
        cls.mock_get.side_effect = cls._mocked_requests_get

    @classmethod
    def tearDownClass(cls):
        cls.get_patcher.stop()

    @classmethod
    def _mocked_requests_get(cls, url):
        mock_response = Mock()
        if url == GithubOrgClient.ORG_URL.format(org="google"):
            mock_response.json.return_value = cls.org_payload
        elif url == cls.org_payload.get("repos_url"):
            mock_response.json.return_value = cls.repos_payload
        else:
            mock_response.json.return_value = None
        return mock_response

    def test_public_repos(self):
        client = GithubOrgClient('google')
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        client = GithubOrgClient('google')
        self.assertEqual(client.public_repos(license="apache-2.0"), self.apache2_repos)
