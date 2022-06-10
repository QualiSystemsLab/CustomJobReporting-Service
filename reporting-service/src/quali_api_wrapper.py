import requests
import json


class QualiAPISession:
    def __init__(self, host, username='', password='', domain='Global', token_id='', port=9000,
                 timezone='UTC', date_time_format='MM/dd/yyyy HH:mm'):
        self.cs_host = host
        self.username = username
        self.password = password
        self.domain = domain
        self.token_id = token_id
        self.cs_api_port = port
        self._api_base_url = "http://{0}:{1}/Api".format(host, port)
        self.req_session = requests.session()
        self.set_auth_headers()

    def set_auth_headers(self):
        token_body = {"Token": self.token_id, "Domain": self.domain}
        creds_body = {"Username": self.username, "Password": self.password, "Domain": self.domain}
        login_headers = {"Content-Type": "application/json"}
        if self.token_id:
            login_result = requests.put(url=self._api_base_url + "/Auth/Login",
                                        data=json.dumps(token_body),
                                        headers=login_headers)
        elif self.username and self.password:
            login_result = requests.put(url=self._api_base_url + "/Auth/Login",
                                        data=json.dumps(creds_body),
                                        headers=login_headers)
        else:
            raise ValueError("Must supply either username / password OR admin token")

        if login_result.status_code not in [200, 202, 204]:
            exc_msg = "Quali API login failure. Status Code: {}. Error: {}".format(str(login_result.status_code),
                                                                                   login_result.text)
            raise Exception(exc_msg)
        auth_token = login_result.text[1:-1]
        formatted_token = "Basic {}".format(auth_token)
        auth_header = {"Authorization": formatted_token}
        self.req_session.headers.update(auth_header)

    def get_installed_standards(self):
        """
        Acquire a list of installed CloudShell Shell standards on the CloudShell Server
        :return: The list of installed Shell Standards
        :rtype: json
        """
        get_standards_result = self.req_session.get(url=self._api_base_url + "/Standards")
        if 200 <= get_standards_result.status_code < 300:
            return get_standards_result.json()
        else:
            return get_standards_result.content

    def get_suite_details(self, suite_id):
        get_details_result = self.req_session.get(url=self._api_base_url + "/Scheduling/Suites/{}".format(suite_id))
        if 200 <= get_details_result.status_code < 300:
            return get_details_result.json()
        else:
            return get_details_result.content

    def get_job_details(self, job_id):
        get_details_result = self.req_session.get(url=self._api_base_url + "/Scheduling/Jobs/{}".format(job_id))
        if 200 <= get_details_result.status_code < 300:
            return get_details_result.json()
        else:
            raise Exception("Issue with job details api call. Status {}: {}".format(str(get_details_result.status_code),
                                                                                    get_details_result.content))

    def get_running_jobs(self):
        url = self._api_base_url + "/Scheduling/Executions"
        running_jobs_res = self.req_session.get(url)
        if 200 <= running_jobs_res.status_code < 300:
            jobs = running_jobs_res.json()
            return jobs
        else:
            raise Exception(
                "Issue with get_running_jobs api call. Status code {}. {}".format(str(running_jobs_res.status_code),
                                                                                  running_jobs_res.content))


if __name__ == "__main__":
    api = QualiAPISession(host="localhost", username="admin", password="admin")
    results = api.get_installed_standards()
    pass
