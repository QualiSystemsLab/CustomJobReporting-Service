# Customer-VF-Bracknell-CustomJobReporting

This solution depends on "sandbox data" feature released in Cloudshell 9.2 to log custom data.
The custom table changes will still work pre 9.2.

### Purpose
This solution creates a custom email report of jobs. Added data fields are:
 1. test inputs
 2. pass / fail status
 3. execution server used
 4. custom data aggregated at end of report
 
##### === Sample Email ===
 ![Reporting Sample Mail](images/custom_report_sample.png?raw=true "Custom Report Sample")
 
##### === Custom Data Appended to bottom of test ===
 ![Reporting Sample Mail](images/custom_data_sample.png?raw=true "Custom Data Sample")


### Solution Flow
-   Only one TS test in job needs to set job ID onto Reporting service. 
-   During teardown this job id is used to get job data vial REST call to quali api. This data is used to populate a custom report.
-   The report is then mailed to users configured on service. (by default sandbox owner is mailed) 
-   Additionally tests in job can store custom data in sandbox data store which will also be added to report.

### Solution Components
1. Testshell test "set_job_id" must be in finalize of first test in job
2. Reporting Service Shell must be present in blueprint
3. Custom Teardown Script attached to trigger service. Collects job and sends email report.
4. SMTP Server Shell loaded and configured in inventory (NOT required to be in blueprint)

### Attached TS Helper Scripts Needed
The testshell helper tests are provided below: 
-   NOTE: the attached TS tests were created in 9.3 patch 5. Can NOT be migrated to older version
-   for older version, refer to screenshots and recreate tests (they are quick to re-write)

### TS Helper Tests Overview
1. set_job_id - uses testshell api SetServiceAttribute method to executionDetails.jobId onto service
    -  this test is MANDATORY. Otherwise service will not be able to get job details from Quali API
    - This test is required in only ONE test per job. I recommend to put it in the finalize of the first test as shown in the sample usage below.

##### === Set Job Id (Required) ===
 ![Reporting Sample Mail](images/set_job_id.png?raw=true "Set Job Id")
 
2. set_test_data - uses testshell api ExecuteCommand to trigger method on reporting service.
    - this method will set custom data in sandbox data, using the test id as a key
    - Create variable "custom_test_data" and publish to input interface of helper
    - this helper relies on sandbox data, which is only available staring in 9.2

 ##### === Set Custom Data (Optional) ===
 ![Reporting Sample Mail](images/set_custom_data.png?raw=true "Set Custom Data")
 
3. sample_custom_data_pass - sample test showing the usage of the two helper scripts in a job's test
    - Note the use of set job id in Finalize
    - 3 instances of custom data logged to sandbox data

##### === Sample Usage ===
 ![Reporting Sample Mail](images/sample_usage.png?raw=true "Sample Usage")