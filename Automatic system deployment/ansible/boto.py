
import boto
import time
from boto.ec2.regioninfo import RegionInfo

region=RegionInfo(name='melbourne', endpoint='nova.rc.nectar.org.au')
ec2_connection = boto.connect_ec2(aws_access_key_id='eddbc9ec9d5b4ead91937e2b91bbad80', aws_secret_access_key='09e0b92c95614d28b2623f772e274698', is_secure=True, 
	region=region, port=8773, path='/services"})/Cloud', validate_certs=False)

VM_IPs = []
volume_IDs = []
print("connection is successed!")

def verify_group_status(groupname):
	check = False
	group = ec2_connection.get_all_security_groups()
	for g in group:
	    if g.name == groupname:
	        check = True
	return check

def create_security_group(groupname):
	check = verify_group_status(groupname)
	if check == False:
		print("creating security group for %s!" %groupname)
		security_group = ec2_connection.create_security_group(groupname,"allowing %s access!" %groupname)
		if groupname == 'ssh':
			print("adding the new rules for %s!" %groupname)
			security_group.authorize("tcp",22,22,"0.0.0.0/0")
		elif groupname == 'http':
		    print("adding the new rules for %s!" %groupname)
		    security_group.authorize("tcp",80,80,"0.0.0.0/0")
		    security_group.authorize("tcp",443,443,"0.0.0.0/0")
		    security_group.authorize("tcp",5984,5984,"0.0.0.0/0")
	else:
	    print("This Security Group of \"%s\" is available to use!" %groupname)

create_security_group('http')
create_security_group('ssh')

def create_volume():
    for k in range(4):
	    ec2_connection.create_volume(60,"melbourne-qh")

def create_instance(num_of_instance):
	count = num_of_instance
	for i in range(count):
		ec2_connection.run_instances('ami-000037b9', key_name='cloudtweet', placement='melbourne',instance_type='m1.small', security_groups=['http','ssh'])

def verify_state():
	print("Start creating instances")
	create_instance(4)
	current_volume = ec2_connection.get_all_volumes()
	for vol in current_volume:
	    volume_IDs.append(vol.id)
	reservations = ec2_connection.get_all_reservations()
	for i in range(len(reservations)):
		instance = reservations[i].instances[0]
		instance_state = reservations[i].instances[0].update()
		while instance_state == 'pending':
			time.sleep(30)
			print("Instance%s is %s" %(i,instance_state))
			instance_state = reservations[i].instances[0].update()
		if instance_state == 'running':
			instance.add_tag("Name","Instance%s"%i)
			VM_IPs.append(instance.ip_address)
			print("Instance %s is now ready to use" %i)
		else:
			print('Instance %s instance_state:' %i + instance_state)		

def printing_host():
    info = '\n'.join(VM_IPs)
    path = '/Users/sunshine/desktop/Nectarhost'
    user = 'ansible_user=ubuntu'
    key = 'ansible_private_key_file=/Users/sunshine/Desktop/cloudtweet.pem'
    with open(path,'w') as f:
    	f.write('[cloudservers]\n'+info+'[webservers]\n'+str(VM_IPs[3])+'\n\n'+'[allclouds:children]\ncloudservers\nwebservers\n'+'\n\n[allclouds:vars]\n'+ user + '\n'+ key)
    print('Generate hostfile Successfully!')

create_volume()
verify_state()
printing_host()
print("Successful!")