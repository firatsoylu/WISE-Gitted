SELECT n.id, n.nodeid, n.nodetype, ui.workgroupid, wandu.username, wandu.period, r.id, r.name, wandu.sgender, prj.parentprojectid, s.data  FROM
sail_database.runs r, 
sail_database.projects prj,
vle_database.node n, 
vle_database.stepwork s,
vle_database.userinfo ui,

(SELECT w.id as workgroupid, ud.username as username, g.name as period, sud.gender as sgender, sud.birthday as sbirthday FROM
sail_database.runs r,
sail_database.workgroups w,
sail_database.wiseworkgroups ww,
sail_database.groups g,
sail_database.groups_related_to_users grtu,
sail_database.users u,
sail_database.student_user_details sud,
sail_database.user_details ud
WHERE
r.name like '%PNoM%Test%' and 
r.id=w.offering_fk and
w.group_fk=grtu.group_fk and
w.id=ww.id and
ww.period=g.id and
grtu.user_fk=u.id and
u.user_details_fk=sud.id and
sud.id=ud.id) wandu
WHERE
r.name like '%PNoM%Test%' and 
r.start_time > '2013-11-1' and 
r.id=n.runid and 
n.id=s.node_id and 
s.data like '%nodeStates":[{%' and 
s.userinfo_id=ui.id and 
prj.id=r.project_fk and
ui.workgroupid=wandu.workgroupid;