#!/usr/bin/env python

# Copyright (C) 2017 Udacity Inc.
#
# This file is part of Robotic Arm: Pick and Place project for Udacity
# Robotics nano-degree program
#
# All Rights Reserved.

# Author: Harsh Pandya

# import modules
import rospy
import tf
from kuka_arm.srv import *
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from geometry_msgs.msg import Pose
from mpmath import *
from sympy import symbols, cos, sin, pi, simplify, sqrt, atan2, acos
from sympy.matrices import Matrix


def handle_calculate_IK(req):
		rospy.loginfo("Received %s eef-poses from the plan" % len(req.poses))
		if len(req.poses) < 1:
				print "No valid poses received"
				return -1
		else:
				### Your FK code here
				# Create symbols
				q1, q2, q3, q4, q5, q6, q7 = symbols('q1:8')
				d1, d2, d3, d4, d5, d6, d7 = symbols('d1:8')
				a0, a1, a2, a3, a4, a5, a6 = symbols('a0:7')
				alpha0, alpha1, alpha2, alpha3, alpha4, alpha5, alpha6 = symbols('alpha0:7')
	#
	# Create Modified DH parameters
				s = {alpha0:     0,  a0:      0,  d1:  0.75, 
					 alpha1: -pi/2.,  a1:   0.35,  d2:     0,  q2: q2-pi/2.,
					 alpha2:     0,  a2:   1.25,  d3:     0,  
					 alpha3: -pi/2.,  a3: -0.054,  d4:   1.5,
					 alpha4:  pi/2.,  a4:      0,  d5:     0,
					 alpha5: -pi/2.,  a5:      0,  d6:     0,
					 alpha6:     0,  a6:      0,  d7: 0.303,  q7:       0}
	#
	#
	# Define Modified DH Transformation matrix
				T0_1 = Matrix([[             cos(q1),            -sin(q1),            0,              a0],
							   [ sin(q1)*cos(alpha0), cos(q1)*cos(alpha0), -sin(alpha0), -sin(alpha0)*d1],
							   [ sin(q1)*sin(alpha0), cos(q1)*sin(alpha0),  cos(alpha0),  cos(alpha0)*d1],
							   [                   0,                   0,            0,               1]])
				T0_1 = T0_1.subs(s)

				T1_2 = Matrix([[             cos(q2),            -sin(q2),            0,              a1],
							   [ sin(q2)*cos(alpha1), cos(q2)*cos(alpha1), -sin(alpha1), -sin(alpha1)*d2],
							   [ sin(q2)*sin(alpha1), cos(q2)*sin(alpha1),  cos(alpha1),  cos(alpha1)*d2],
							   [                   0,                   0,            0,               1]])
				T1_2 = T1_2.subs(s)

				T2_3 = Matrix([[             cos(q3),            -sin(q3),            0,              a2],
							   [ sin(q3)*cos(alpha2), cos(q3)*cos(alpha2), -sin(alpha2), -sin(alpha2)*d3],
							   [ sin(q3)*sin(alpha2), cos(q3)*sin(alpha2),  cos(alpha2),  cos(alpha2)*d3],
							   [                   0,                   0,            0,               1]])
				T2_3 = T2_3.subs(s)

				T3_4 = Matrix([[             cos(q4),            -sin(q4),            0,              a3],
							   [ sin(q4)*cos(alpha3), cos(q4)*cos(alpha3), -sin(alpha3), -sin(alpha3)*d4],
							   [ sin(q4)*sin(alpha3), cos(q4)*sin(alpha3),  cos(alpha3),  cos(alpha3)*d4],
							   [                   0,                   0,            0,               1]])
				T3_4 = T3_4.subs(s)

				T4_5 = Matrix([[             cos(q5),            -sin(q5),            0,              a4],
							   [ sin(q5)*cos(alpha4), cos(q5)*cos(alpha4), -sin(alpha4), -sin(alpha4)*d5],
							   [ sin(q5)*sin(alpha4), cos(q5)*sin(alpha4),  cos(alpha4),  cos(alpha4)*d5],
							   [                   0,                   0,            0,               1]])
				T4_5 = T4_5.subs(s)

				T5_6 = Matrix([[             cos(q6),            -sin(q6),            0,              a5],
							   [ sin(q6)*cos(alpha5), cos(q6)*cos(alpha5), -sin(alpha5), -sin(alpha5)*d6],
							   [ sin(q6)*sin(alpha5), cos(q6)*sin(alpha5),  cos(alpha5),  cos(alpha5)*d6],
							   [                   0,                   0,            0,               1]])
				T5_6 = T5_6.subs(s)

				T6_G = Matrix([[             cos(q7),            -sin(q7),            0,              a6],
							   [ sin(q7)*cos(alpha6), cos(q7)*cos(alpha6), -sin(alpha6), -sin(alpha6)*d7],
							   [ sin(q7)*sin(alpha6), cos(q7)*sin(alpha6),  cos(alpha6),  cos(alpha6)*d7],
							   [                   0,                   0,            0,               1]])
				T6_G = T6_G.subs(s)

		#		# Better way to define these transformation matrix
		# 		def TF_Mat(alpha, a, d, q):
		# 			TF = Matrix([[            cos(q),           -sin(q),           0,             a],
		# 						[ sin(q)*cos(alpha), cos(q)*cos(alpha), -sin(alpha), -sin(alpha)*d],
		# 						[ sin(q)*sin(alpha), cos(q)*sin(alpha),  cos(alpha),  cos(alpha)*d],
		# 						[                 0,                 0,           0,             1]])
		# 			return TF
		
		# 		# Create individual transformation matrices
		# 		# Substitute DH_Table
		# 		T0_1 = TF_Mat(alpha0, a0, d1, q1).subs(dh)
		# 		T1_2 = TF_Mat(alpha1, a1, d2, q2).subs(dh)
		# 		T2_3 = TF_Mat(alpha2, a2, d3, q3).subs(dh)
		# 		T3_4 = TF_Mat(alpha3, a3, d4, q4).subs(dh)
		# 		T4_5 = TF_Mat(alpha4, a4, d5, q5).subs(dh)
		# 		T5_6 = TF_Mat(alpha5, a5, d6, q6).subs(dh)
		# 		T6_7 = TF_Mat(alpha6, a6, d7, q7).subs(dh)
	
		# 3x3 correction matrix
				R_corr_z = Matrix([[     cos(pi),     -sin(pi),           0],
								   [     sin(pi),      cos(pi),           0],
								   [           0,            0,           1]])
				R_corr_y = Matrix([[  cos(-pi/2.),            0,  sin(-pi/2.)],
								   [           0,            1,           0],
								   [ -sin(-pi/2.),            0,  cos(-pi/2.)]])
				# R_corr = simplify(R_corr_z * R_corr_y)
				R_corr = R_corr_z * R_corr_y

				# print(R_corr)

		# simple R_xyz
				r, p, y = symbols('r p y')
				R_x = Matrix([[ 1,             0,        0],
							  [ 0,        cos(r),  -sin(r)],
							  [ 0,        sin(r),   cos(r)]])

				R_y = Matrix([[ cos(p),        0,   sin(p)],
							  [      0,        1,        0],
							  [-sin(p),        0,   cos(p)]])

				R_z = Matrix([[ cos(y),  -sin(y),        0],
							  [ sin(y),   cos(y),        0],
							  [ 0,             0,        1]])
				# R_xyz = simplify(R_z*R_y*R_x) * R_corr
				R_xyz = R_z*R_y*R_x * R_corr


				###
				# Transform matrix to be used get value matrix
				# T0_3 = simplify(T0_1*T1_2*T2_3)
				T0_3 = T0_1*T1_2*T2_3
				R0_3 = T0_3[0:3, 0:3]
				
				# Initialize service response
				joint_trajectory_list = []
				# print("len of req.poses are: ", len(req.poses))
				for x in xrange(0, len(req.poses)):
						# IK code starts here
						joint_trajectory_point = JointTrajectoryPoint()

			# Extract end-effector position and orientation from request
			# px,py,pz = end-effector position
			# roll, pitch, yaw = end-effector orientation
						px = req.poses[x].position.x
						py = req.poses[x].position.y
						pz = req.poses[x].position.z

						(roll, pitch, yaw) = tf.transformations.euler_from_quaternion(
								[req.poses[x].orientation.x, req.poses[x].orientation.y,
										req.poses[x].orientation.z, req.poses[x].orientation.w])

						### Your IK code here
						# Get t_WC
						# R_xyz_new = R_xyz.evalf(subs={r: roll, p: pitch, y: yaw})
						R_xyz_new = R_xyz.subs({r: roll, p: pitch, y: yaw})
						t_EE = Matrix([px, py, pz])
						displacement = 0.303 * R_xyz_new * Matrix([0,0,1])
						t_WC = t_EE - displacement
		
				# Calculate joint angles using Geometric IK method
				# Get theta 1-3
						theta1 = float(atan2(t_WC[1], t_WC[0]))
						# theta2 is tricky
						theta2_ang1 = atan2(t_WC[2]-0.75, sqrt(t_WC[0]**2+t_WC[1]**2)-0.35)
						theta2_len1 = 1.25
						theta2_len2 = sqrt((t_WC[2]-0.75)**2 + (sqrt(t_WC[0]**2+t_WC[1]**2)-0.35)**2)
						theta2_len3 = sqrt(1.5**2 + 0.054**2)
						theta2_ang2 = acos((theta2_len1**2 + theta2_len2**2 - theta2_len3**2)/(2*theta2_len1*theta2_len2))
						theta2 = float(pi/2 - theta2_ang1 - theta2_ang2)

						theta3_ang1 = atan2(0.054, 1.5)
						theta3_ang2 = acos((theta2_len1**2 + theta2_len3**2 - theta2_len2**2)/(2*theta2_len1*theta2_len3))
						theta3 = float(pi/2 - theta3_ang1 - theta3_ang2)

						# Transform matrix to be used get value matrix (need to be here)
						# T0_3 = T0_1*T1_2*T2_3
						# R0_3 = T0_3[0:3, 0:3]
						R0_3_val = R0_3.evalf(subs={q1: theta1, q2: theta2, q3: theta3})
						# R3_6_val = R0_3_val.inv("LU") * R_xyz_new # This .inv function somehow returns funky value at
						# certain joint angles' combinations!!! Caused me a few days to find this bug!
						R3_6_val = R0_3_val.transpose() * R_xyz_new

						# After printing the matrix, get equations like below:
						# theta4 = float(atan2(R3_6_val[2,2], -R3_6_val[0,2]))
						# theta5 = float(atan2(sqrt(R3_6_val[0,2]**2 + R3_6_val[2,2]**2), R3_6_val[1,2]))
						# theta6 = float(atan2(-R3_6_val[1,1], R3_6_val[1,0]))
						theta5 = atan2(sqrt(R3_6_val[0,2]*R3_6_val[0,2] + R3_6_val[2,2]*R3_6_val[2,2]),R3_6_val[1,2])
			
						if (theta5 > pi):
							theta4 = atan2(-R3_6_val[2,2], R3_6_val[0,2])
							theta6 = atan2(R3_6_val[1,1],-R3_6_val[1,0])
						else:
							theta4 = atan2(R3_6_val[2,2], -R3_6_val[0,2])
							theta6 = atan2(-R3_6_val[1,1],R3_6_val[1,0])
						# print("poses are: ", [req.poses[x].orientation.x, req.poses[x].orientation.y,
						# 				req.poses[x].orientation.z, req.poses[x].orientation.w])
						# print("thetas are: ", theta1, theta2, theta3, theta4, theta5, theta6)

								# Populate response for the IK request
								# In the next line replace theta1,theta2...,theta6 by your joint angle variables
						joint_trajectory_point.positions = [theta1, theta2, theta3, theta4, theta5, theta6]
						joint_trajectory_list.append(joint_trajectory_point)

				rospy.loginfo("length of Joint Trajectory List: %s" % len(joint_trajectory_list))
				return CalculateIKResponse(joint_trajectory_list)


def IK_server():
		# initialize node and declare calculate_ik service
		rospy.init_node('IK_server')
		s = rospy.Service('calculate_ik', CalculateIK, handle_calculate_IK)
		print "Ready to receive an IK request"
		rospy.spin()

if __name__ == "__main__":
		IK_server()
