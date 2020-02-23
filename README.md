# Customer-VF-Bracknell-CustomJobReporting
REQUIRED COMPONENTS:
1. Testshell test "set_job_id" in finalize of first test in job
2. Reporting Service Shell Present in blueprint
3. Custom Teardown Script to collect data and send report
4. SMTP Server Shell loaded and configured in inventory (NOT required to be in blueprint)

OPTIONAL:
1. Testshell test "Set_data" present to add custom data output to report