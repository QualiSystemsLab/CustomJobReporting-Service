# CustomJobReporting Service

This solution depends on "sandbox data" feature released in Cloudshell 9.2 to log custom data. \
The custom table changes will still work pre 9.2.

### Purpose
This solution creates a custom email report of jobs. Added data fields are:
 1. test inputs
 2. pass / fail status
 3. execution server used
 4. custom data aggregated at end of report
 
##### === Sample Email ===
 ![Reporting Sample Mail](images/custom_report_sample.png?raw=true "Custom Report Sample")
 
##### === Custom Data Appended to bottom of Email Report ===
 ![Reporting Sample Mail](images/custom_data_sample.png?raw=true "Custom Data Sample")


### Solution Flow
-   Only one TS test in job needs to set job ID onto Reporting service. 
-   During teardown this job id is used to get job data vial REST call to quali api. This data is used to populate a custom report template.
-   The report is then mailed to users configured on service. (by default sandbox owner is mailed) This solution uses the attached SMTP resource shell which must be inventoried and configured.
-   Additionally tests in job can store custom data in sandbox data store which will also be added to report.

### Solution Components
1. Testshell test "set_job_id" must be in finalize of first test in Cloudshell job
2. Reporting Service Shell must imported and be present in blueprint
3. Custom Teardown Script attached to trigger service. Collects job and sends email report.
4. SMTP Server Shell loaded and configured in inventory (NOT required to be in blueprint)
(attach all shells, script, and offline dependencies to [pypi server repository]() if working offline)

### Attached TS Helper Scripts Needed
The testshell helper tests are provided below: 
-   NOTE: the attached TS tests were created in 9.3 patch 5. Can NOT be migrated to older version
-   for older version, refer to screenshots and recreate tests (they are quick to re-write)

### TS Helper Tests Overview
1. set_job_id - uses testshell api SetServiceAttribute method to executionDetails.jobId onto service
    - This test is MANDATORY. Otherwise service will not be able to get job details from Quali API
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
 
 ### Reporting Service Attributes
-	Additional Recipients – appended to sandbox owner in primary email list
-	CC Recipients – added to mail in CC
-	Error report all – Boolean switch to send error report to all users. On by default. If off, only sandbox owner gets error report if something goes wrong with report.
-   SMTP Resource - Name of configured cloudshell SMTP resource which will send mail
-   CS HTTPS - used when generating link to report in mail (if your portal is https set to true)
-  Current Job ID - Do not touch this attribute. This is populated by automation. Left visible for debugging purposes


