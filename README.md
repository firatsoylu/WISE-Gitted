# Getting and Cleaning ModelSim Data

## How do I get data from WISE into a format I can actually use?

There are two steps to getting the WISE data in a usable format. The first step is to pull the appropriate data down from the WISE server onto your local machine. And the second, is to restructure that data so that you can analyze it.


### STEP 1: Getting the data from the WISE server

First, you’ll need access to the SQL server — request an account from Jason. Once you have an account with access, download MySQLWorkbench (http://dev.mysql.com/downloads/tools/workbench/). Make a new connection with the following info:

Connection Method: “Standard TCP/IP over SSH”
SSH Hostname: abmplus.tech.northwestern.edu:22
SSH Username: *the username jason created for you*
username: *the username jason created for you*

Open a connection

In the next screen you should see an area to type a Query.  Copy and paste the following:

‘’’
SELECT n.id, n.nodeid, n.nodetype, ui.workgroupid, wandu.username, r.id, r.name,wandu.sgender, prj.parentprojectid, s.data  FROM
sail_database.runs r, 
sail_database.projects prj,
vle_database.node n, 
vle_database.stepwork s,
vle_database.userinfo ui,
(SELECT w.id as workgroupid, ud.username as username, sud.gender as sgender, sud.birthday as sbirthday FROM
sail_database.runs r,
sail_database.workgroups w,
sail_database.groups_related_to_users g,
sail_database.users u,
sail_database.student_user_details sud,
sail_database.user_details ud
WHERE
r.name like ‘%PNoM%Test%' and 
r.id=w.offering_fk and
w.group_fk=g.group_fk and
g.user_fk=u.id and
u.user_details_fk=sud.id and
sud.id=ud.id) wandu
WHERE
r.name like ‘%PNoM%Test%' and 
r.start_time > '2013-11-1' and 
r.id=n.runid and 
n.id=s.node_id and 
s.data like '%nodeStates":[{%' and 
s.userinfo_id=ui.id and 
prj.id=r.project_fk and
ui.workgroupid=wandu.workgroupid;
‘’’

Now, before we continue, there are some things you’ll want to edit to be sure you’re getting what you actually want. In particular, you’ll want to change the text that says “r.name like '%PNoM%Test%’” to look for the name of the run you actually want. Notice, the % is a wildcard which allows anything in it’s place, so the query above actually returns any run with the strings “PNoM” and “Test” somewhere in the middle. If I remove the last %, then it will look for runs that end in with “Test”, if I remove the first % it will look for runs that begin with “PNoM”, etc. Note you can also add to or change this section to look for a particular run (replace “r.name like '%PNoM%Test%'” with “n.runid like 294”, to look for runs with a particular name after a specific time (as we do in the query above), etc. If you need help tweaking this query let Firat or I know.

Next we need to run the query. First, on the menu bar go to, Query -> Limit Rows and make sure “don’t limit” is checked. Next, click the lightening bolt button on the query menu bar (not the one with the cursor) or on the main menu bar, go to Query -> Execute (All or Selection). Depending on how large of a sample you’re retrieving, this can take some time. Once it finishes, you should notice a table with the data below your query and in the pane at the bottom you should see how many rows were returned. If all looks ok, it’s time to export this data.

To export, on the main menu bar, go to Query -> Export Results.  Make sure you have csv selected, name the file, and then save it.  Now that you’ve exported the file it’s time to parse it…


### STEP 2: Parse the data so you can actually do something useful with it

If you haven’t already, copy the WISEcsv_1.1.py (downloaded from git) file and place it in the same directory as your new SQL results csv file. Open your terminal and navigate to that directory. Type the following command replacing “myData.csv” with the name of the csv you want to parse.

‘’’
python WISEcsv.py -i myData.csv
‘’’

After the script runs, you should see “file written to myDataOut.csv”. That’s your parsed file! Get analyzing!


## What’s in the myDataOut.csv file?

This file will output a row for each question. This row contains the following items: runID (unique id for each run), userID (id for each user per run—so will be different for pre and post test), username, node (WISE way of saving steps and questions), step, type (multiple choice or open response), response, prepost, gender (0=male, 1=female, 2=no answer), parent project (the master project this run was copied from), teacher, and school.

Coming soon… Teacher variables (self report and observation ratings)

With the data in this format you can easily create pivot tables in excel to do some basic analsis of the data.


## Things to know about the script…

Some types of questions are more challenging to parse than others. For that reason my script does NOT parse the draw step, mach sequence questions, or table steps. Those questions just get tossed during the parse. In other words, they’ll be in your SQL query, but not in your “out.csv” file

WISE keeps track of revisions, my script doesn’t. The answer that ends up in the parsed file will be the last answer recorded.


## But your script didn’t work! It just threw a stupid error!

Take it back! My script is perfect!  …OK so it’s probably NOT perfect…Go ahead and copy and paste the trace into an email to me (nholbert@northwestern.edu). It probably wouldn’t hurt to also email me the csv file you were trying to parse. 