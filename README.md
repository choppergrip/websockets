**Requirements**:

- Python 3.9

**Installation:**

- Clone the repository.
- Run pip install -r requirements.txt.
- To execute tests: pytest -s.

**Task Overview**

- I aimed to design a framework structure that is easy to extend to various data feeds and test types, rather than cramming everything into a single file.
- The coinbase.py wrapper currently lacks validation and could be improved in many ways, but since this is just a toy example created in 2-3 hours, I kept it simple.
- Occasionally, I observe negative latency values, which could be due to either my local machine or the remote server.
- The measured latency includes both network latency and application latency. In my tests, I did not focus on optimizing application latency (e.g., pre-allocating memory for arrays or using faster alternatives to json), but this can certainly be addressed if required.
- It would be beneficial to further analyze data distribution and conduct deeper statistical analyses, such as a t-test.

**Bonus:**

The repository is integrated with GitHub CI, so you can view the test results directly without needing to clone the repo or set up the environment locally!
https://github.com/choppergrip/websockets/actions/runs/13996948032/job/39194374348
