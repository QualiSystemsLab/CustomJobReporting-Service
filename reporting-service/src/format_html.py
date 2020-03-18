import json
from cloudshell.api.cloudshell_api import SandboxDataKeyValueInfo
import helper_code.time_helpers as time_help


def _format_params(params):
    if not params:
        return ""

    outp = ""
    for index, param in enumerate(params):
        outp += "{} - {}<br/>".format(param["ParameterName"], param["ParameterValue"])
    return outp


def _get_test_rows(tests):
    outp = ""
    for test in tests:
        row = """<tr>
        <td>{path}</td>
        <td>{params}</td>
        <td>{result}</td>
        <td><a href={link}>Test Report</a></td>
        </tr>""".format(path=test["TestPath"],
                        result=test["Result"],
                        params=_format_params(test["Parameters"]),
                        link=test["ReportLink"])
        outp += row
    return outp


def _get_job_report_link(server_address, protocol, job_id):
    return "{}://{}/SnQ/JobStatus/Index/{}".format(protocol, server_address, job_id)


def _get_ms_timestamp_from_key(sb_data_obj):
    val = sb_data_obj.Key
    time_stamp_str = val.split("_")[1]
    time_stamp = int(time_stamp_str)
    return time_stamp


def _get_test_data_html(sorted_test_data):
    """
    sort data keys and convert to html
    :param test_id:
    :param list SandboxDataKeyValueInfo sandbox_data:
    :return:
    """
    outp = ""
    for data in sorted_test_data:
        time_stamp_ms = _get_ms_timestamp_from_key(data)
        time_stamp = time_help.get_date_string_from_ms_timestamp(time_stamp_ms)
        time_stamp += " (UTC)"
        outp += """
        <div>
            <p>Time Stamp: <em>{time_stamp}</em></p>
            <p><pre>{data}</pre></p>
        </div>
        <br/>
        """.format(time_stamp=time_stamp,
                   data=data.Value)
    return outp


def _get_html_custom_test_data(sandbox_data, job_tests_list):
    outp = ""
    for test in job_tests_list:
        test_id = test["ReportId"]
        test_path = test["TestPath"]
        test_data = [data for data in sandbox_data if test_id in data.Key]
        sorted_data = sorted(test_data, key=_get_ms_timestamp_from_key)
        if not sorted_data:
            return outp
        outp += """
        <div style="background:lightgray;padding:1em;border-radius:5px">
            <h4>{test_path}</h4>
            <h5>Result: {result}</h5>
            <h5>Params:
                <br/> 
                <div>{params}</div>
            </h5>
            {test_data}
        </div>
        <br/>
        <br/>
        """.format(test_path=test_path,
                   test_data=_get_test_data_html(sorted_data),
                   result=test["Result"],
                   params=_format_params(test["Parameters"]))
    return outp


def format_html_template(html_path, job_details, server_address, server_date_time, protocol, sb_data):
    job_report_link = _get_job_report_link(server_address, protocol, job_details["Id"])
    tests = job_details["Tests"]
    failure_reason = job_details["JobFailureDescription"] if job_details["JobFailureDescription"] else ""
    execution_server = job_details["SelectedExecutionServer"]
    custom_data = _get_html_custom_test_data(sb_data, tests)
    with open(html_path) as template_file:
        file_data = template_file.read()
        formatted = file_data.format(JobName=job_details["Name"],
                                     SuiteName="test suite",
                                     EndDate=server_date_time,
                                     Result=str(job_details["JobResult"]),
                                     Owner=job_details["OwnerName"],
                                     Description=job_details["Description"],
                                     TopologyName=job_details["Topology"]["Name"],
                                     TotalNumberOfTests=str(len(tests)),
                                     State=job_details["JobState"],
                                     FailureReason=failure_reason,
                                     TestData=_get_test_rows(tests),
                                     JobReportLink=job_report_link,
                                     SelectedExecutionServer=execution_server,
                                     CustomTestData=custom_data)
    return formatted


if __name__ == "__main__":
    from helper_code.quali_api_wrapper import QualiAPISession
    quali_api = QualiAPISession(host="localhost", username="admin", password="admin", domain="Global")
    current_job_id = "4893a773-7523-4b72-ac54-d0660ce21de5"
    job_details = quali_api.get_job_details(current_job_id)
    html_path = "JobExecutionEnded.htm"
    content = format_html_template(html_path, job_details, "qs-il-lt-nattik", "https")
    pass
