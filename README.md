# Customer-VF-Bracknell-CustomJobReporting

This solution depends on sandbox data (Cloudshell 9.2)

### Purpose
This solution creates a custom email report of jobs. Added data fields are:
    - test inputs
    - pass / fail status
    - execution server used
    - custom data aggregated at end of report


### Solution Flow
Testshell test sets job id onto service. 
During teardown this job id is used to get job data from quali api and populate a custom report.
The report is then mailed to users. 
Additionally tests in job can store custom data in sandbox data store which will also be added to report.

### Solution Components
1. Testshell test "set_job_id" must be in finalize of first test in job
2. Reporting Service Shell must be present in blueprint
3. Custom Teardown Script attached to trigger service. Collects job and sends email report.
4. SMTP Server Shell loaded and configured in inventory (NOT required to be in blueprint)

### Attached TS Helpers
The testshell helper tests are in the ts-tests folder along with screenshots of implementation. 
    - NOTE: the attached TS tests were created in 9.3 patch 5. Can NOT be migrated to older version
    - for older version, refer to screenshots and recreate tests

### TS Helpers Overview
1. set_job_id - uses testshell api SetServiceAttribute method to executionDetails.jobId onto service
    -  this test is MANDATORY. Otherwise service will not be able to get job details from Quali API

2. set_test_data - uses testshell api ExecuteCommand to trigger method on reporting service.
    - this method will set custom data in sandbox data, using the test id as a key
    - this helper relies on sandbox data, which is only available staring in 9.2

3. sample_custom_data_pass - sample test showing the implementation of the two helper tests