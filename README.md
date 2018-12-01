# Github-Mining

A program that extracts all commits from GitHub repository and detects methods or functions whose number of parameters have been increased.
`Note: The program requires a good internet connection.`

Example:
* Method in previous commit: assertArrayEquals ( long [] expecteds, long [] actuals )
* Method in next commit: assertArrayEquals ( String  message, Object [] expecteds, Object [] actuals )
Here, the parameter count is increased from two to three in "assertArrayEquals". Such functions are detected by the program.
## Requirements
###### Python 2.7.14 
###### javalang
###### PyGithub

### Installing
Install and activate Virtual Environment
```
sudo apt-get install python-pip
pip install virtualenv
virtualenv <name>
source <name>/bin/activate
```
Install Javalang (to parse Java source)
```
pip install javalang
```
Install PyGithub (to extract data from GitHub repositories )
```
pip install PyGithub
```
## Running the code
Checkout this repository:

```	
	$ git clone https://github.com/AkarshRK/Github-Mining.git
```
Add your `Personal API token` in the main.py source code. Then edit the `repositories.txt` file to add the name of the GitHub repositories that you would like to analyze. Now run the code as follows:
```
$ cd Github-Mining
$ python main.py
```
	
## Results
The result will be a csv file and there will be three columns, namely "Commit SHA", "Java File", "Old function signature", "New function signature". The csv files will be automatically generated in the "report/" directory.

## My test results
The above program is executed and tested on following top Java repositories:

| Repository | Description | Number of commits |
| --- | --- | --- |
| iluwatar/java-design-patterns | Design patterns implemented in Java http://java-design-patterns.com | 2,168 |
| PhilJay/MPAndroidChart | A powerful Android chart view / graph view library, supporting line- bar- pie- radar- bubble- and candlestick charts as well as scaling, dragging and animations. (Written in Java) | 2,003 |
| junit-team/junit4| A programmer-oriented testing framework for Java. https://junit.org/junit4/ | 2,359 |
| AkarshRK/Java-Prog | Short sample test code for Github-Mining project.| 9 |

The report files can be found in "report/" directory.

## The above project was run on a system with following configurations or settings:
* Operating system: Linux Mint 18.3 "Sylvia" - Cinnamon (64-bit)
* Processor: Intel® Core™ i7-7500U Processor  2.70GHz 2 Core(s)
* Memory (RAM): 15.5 GB
	

