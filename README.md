# Customer-VF-Bracknell-CustomJobReporting
REQUIRED COMPONENTS:
1. Testshell test "set_job_id" must be in finalize of first test in job
2. Reporting Service Shell must be present in blueprint
3. Custom Teardown Script attached to trigger service. Collects job and sends email report.
4. SMTP Server Shell loaded and configured in inventory (NOT required to be in blueprint)

OPTIONAL:
1. Testshell test "Set_data" present to add additional custom data output to report.

Screenshots of sample testshell tests:
![set test id](https://raw.githubusercontent.com/QualiSystemsLab/Customer-VF-Bracknell-CustomJobReporting/master/images/set_job_id.png)