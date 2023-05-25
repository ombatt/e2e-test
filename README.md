The project is based on Selenium. The entry point is parser.py file. The project interpret the JSON files in the tests-suites folder which contain the individual steps of each test case. There are 2 types of JSON files classified by the module attribute:
  - test → refers to an autonomous test case
  - module → contains multiple steps that can be called from test cases (module = test). It is not a standalone test case.
In the main branch there are 2 example files of the two types
Each step can be composed of the following attributes:
1) action → indicates the action to be performed:
   - click → to click an object in the dom
   - goto → to go to an address
   - send_keys → to type characters in a field
   - module → import all the steps of the module with the name equals to exp_value field
   - check_value_condition → to check a condition
   - erase → to erase characters from a field
2) link → to be specified with a url in the steps with goto action
3) exp_type → identifies the object on the page using the specified attribute: ["NAME","XPATH",CLASS_NAME]
4) exp_value → value that the exp_type must check for. Example: if I have to locate an input with name = "dummy" exp_type will be = "NAME" and exp_value will be "dummy"
5) input_value → indicates the characters to insert in the send_keys type steps and the characters to check in the check_value_condition type steps
6) description → description of the step
7) exp_times → number of erasures to do, must be specified in the erase step
8) exp_condition → specifies the condition to check in step with action check_value_condition. Example:        
        "exp_type":"NAME",
        "exp_value" : "field1",
        "exp_condition" : "eq",
        "input_value": "10",
        "action": "check_value_condition",
        "description": "check agency code value for test"
   it means that the step checks that field with name field1 is equal to 10. Other operators are: gt (greather than) and mt (minor than)
9) default_sleep → default sleep time before the next test step
10) exp_sleep → overrides default_sleep only for this step

At the end of all the test a xlsx is generated under test-reports dir with the resume of the test execution
