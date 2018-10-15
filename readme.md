Fixing bugs log

10/15/2008
I would get different bad responses from a clients sheet submission. After several tries I realized the sheet was wrong but also I had an issue in my portmgr algorithm. It was returning a key error. I fixed the issue.

getting to the point to be able to identify and fix was tedious so I thought I'd explain process.

After cloning and setting up the environment I had to run the test_data_generator.py using the sheet that caused the initial error. Now test_data_generator actually runs the process so it popped up the same error as the site was giving. 

I could have created a tam and ran it in the test environment but I was in a hurry so I just kept running the test_data_generator until I found the issue.

Really think a better test workflow is needed on this project. It's actually not that bad but poorly documented. 