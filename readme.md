Fixing bugs log
#####9/6/22
I have successfully implemented docker and ran one test `python -m unittest unit_tests.TestRawRequest.test_raw_from_excel` however other tests are failing likely because the data is not properly loaded. What I need to do is spin up the container with `docker run -it portfolio_calc bash` then cd into the test folder. Then I need to read the code on how to generate data and read each test to see how it gets its data.

Once the tests are working I need to try and load an excel workbook.

#####10/17/2018
I have decided to eliminate the get prices. Its really not the job of this process to get prices and it should be handled by another process. So for now when receiving a request every security must have a price. If a request contains two different prices for the same security an error is thrown.

#####10/16/2018
#### todo 
Need to create a better error message highlighting that a price is missing.
Need to handle when send duplicate prices.
Need to send better error message when "account_cash"  is not included for each account's cash.


##### 10/15/2018
I would get different bad responses from a clients sheet submission. After several tries I realized the sheet was wrong but also I had an issue in my portmgr algorithm. It was returning a key error. I fixed the issue.

getting to the point to be able to identify and fix was tedious so I thought I'd explain process.

After cloning and setting up the environment I had to run the test_data_generator.py using the sheet that caused the initial error. Now test_data_generator actually runs the process so it popped up the same error as the site was giving. 

I could have created a tam and ran it in the test environment but I was in a hurry so I just kept running the test_data_generator until I found the issue.

Really think a better test workflow is needed on this project. It's actually not that bad but poorly documented. 