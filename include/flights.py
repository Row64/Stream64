import os
import math
import numbers

def lon_lat_to_xyz(v):
	x = v[0]*0.01745329
	y = v[1]*0.01745329
	return (math.cos(x)*math.cos(y),math.sin(y),math.sin(x)*math.cos(y))
def xyz_to_lon_lat(v):return (math.atan2(v[2],v[0])*57.29578,math.asin(v[1])*57.29578)
def cross(a, b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def dot(v1, v2):return v1[0]*v2[0]+v1[1]*v2[1]+v1[2]*v2[2]
def normalize(v, tolerance=0.00001):
	mag2 = sum(n*n for n in v)
	if abs(mag2-1.0)>tolerance:mag=math.sqrt(mag2);v=tuple(n/mag for n in v)
	return v
def axisang_to_q(v, ang):
    v = normalize(v)
    ang /= 2
    return math.cos(ang),v[0]*math.sin(ang),v[1]*math.sin(ang),v[2]*math.sin(ang)
def q_mult(q1, q2):
    w1,x1,y1,z1 = q1
    w2,x2,y2,z2 = q2
    return w1*w2-x1*x2-y1*y2-z1*z2,w1*x2+x1*w2+y1*z2-z1*y2,w1*y2+y1*w2+z1*x2-x1*z2,w1*z2+z1*w2+x1*y2-y1*x2
def q_conjugate(q):return (q[0],-q[1],-q[2],-q[3])
def qv_mult(q1, v1):
    q2 = (0.0,) + v1
    return q_mult(q_mult(q1,q2),q_conjugate(q1))[1:]
def get_flight_pos(start_ll,end_ll,f_perc):
	start = lon_lat_to_xyz(start_ll)
	end = lon_lat_to_xyz(end_ll)
	axis_of_rot = cross(start,end)
	ang_of_rot = math.acos( dot(start, end) )
	rot_quat = axisang_to_q(axis_of_rot, ang_of_rot * f_perc)
	
	# rot_quat = axisang_to_q(cross(start,end), math.acos( dot(start, end) ) * f_perc)
	newStart = qv_mult(rot_quat, start)
	return xyz_to_lon_lat(newStart)

class flights(object):
	
	def __init__(self):
		
		self.loaded = False
		self.rows = []
		self.load()

	def load(self):
		print("Running Air West Simulator")
		self.loaded = True
		self.rows = []
		fPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fpaths.csv")
		with open(fPath, "r") as file:
			rlist = file.read().split("\n")
			for ln in rlist:
				r = ln.split(",")
				self.rows.append([int(r[0]),r[1],r[2], float(r[3]),float(r[4]),float(r[5]), int(r[6])  ,float(r[7]),float(r[8]), float(r[9]), float(r[10]), r[11]])
		

	def get_flight_time(self, inH):
		hour = int(inH)
		mdec = inH - hour
		minutes = int(mdec * 60)
		ap = "AM"
		if hour < 1: hour = 12
		elif hour > 12:ap="PM";hour -= 12
		return str(hour)+":"+str(minutes).zfill(2) + " " + ap + " PDT"

	def gen_flight_data(self, inH):

		if not self.loaded:self.load()
		ms = [ [],[],[],  [],[],  [],[] , []]
		for r in self.rows:
			WRAP = r[6]
			if inH > r[3]: # hour > stime
				if inH < r[4] or WRAP == 1:
					perc = (inH - r[3])/r[5] # (ctime - stime)/dur
					ll = get_flight_pos( (r[7],r[8]), (r[9],r[10]), perc)
					ms[0].append(r[0])
					ms[1].append(r[1])
					ms[2].append(r[2])
					ms[3].append(r[3])
					ms[4].append(r[5])
					ms[5].append(ll[0])
					ms[6].append(ll[1])
					ms[7].append(WRAP)
			elif WRAP == 1 and inH < r[4]: # WRAP and ctime < etime
				perc = 1-(r[4]-inH)/r[5]
				ll = get_flight_pos( (r[7],r[8]), (r[9],r[10]), perc)
				ms[0].append(r[0])
				ms[1].append(r[1])
				ms[2].append(r[2])
				ms[3].append(r[3])
				ms[4].append(r[5])
				ms[5].append(ll[0])
				ms[6].append(ll[1])
				ms[7].append(1)
		return ms