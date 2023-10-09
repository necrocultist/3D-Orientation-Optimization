#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np


class Partition:
    def __init__(self, a, b, c):  # Each vertex expressed as a (x,y,z) tuple
        self.v1 = np.array(a)
        self.v2 = np.array(b)
        self.v3 = np.array(c)

    def center(self):
        res = ((self.v1[0] + self.v2[0] + self.v3[0]) / 3,
               (self.v1[1] + self.v2[1] + self.v3[1]) / 3,
               (self.v1[2] + self.v2[2] + self.v3[2]) / 3)
        return round(res[0], 3), round(res[1], 3), round(res[2], 3)

    def angle(self):
        planeV = [0, 0, 1]  # Using the horizontal plane as our "surface"
        normalV = np.cross(self.v2 - self.v1, self.v3 - self.v1)
        angle_rad = np.arccos(np.dot(normalV, planeV) / (np.linalg.norm(normalV) * np.linalg.norm(planeV)))
        res = np.degrees(angle_rad)  # Converting radian to hexadecimal
        return round(res, 3)

# In[2]:


# TEST
v1 = (0, 0, 0)
v2 = (10, 0, 0)
v3 = (0, 10, 10)
test = Partition(v1, v2, v3)
a = test.angle()
a


# Now we would obtain points on the surface of our object as (x,y,z) tuples and add them to a list, from which we would start building partitions. We create a function that receives as input the aforementioned list and a threshold angle. This last parameter will allow us to determine whether a partition would need support in order to stand still on a surface (e.g. if the inclination of an object is below 45º, it could fall, so it would need external support).

# In[3]:


def supportLevel(incl, points):
    total = 0
    supp = 0
    for i in range(len(points) - 2):
        t = Partition(points[i], points[i + 1], points[i + 2])
        if t.angle() < incl:
            supp += 1
        total += 1
    return (supp / total) * 100


# This function would return misleading results, as it reads the points on a FCFS basis, and not based on proximity. This is why we should include as a parameter a list/set of partitions instead of a list of points:

# In[4]:


def supportLevel_alt(incl, partitions):
    total = 0
    supp = 0
    for p in partitions:
        if p.angle() < incl:
            supp += 1
        total += 1
    return (supp / total) * 100


# Additionally, we could rescale our problem to work with bigger parts. If we retrieved too many points from a bigger surface, we could just reduce this amount using a recursive function; we would create partitions from our list of points and obtain their centers, in order to work with a shorter list.

# In[5]:


def rescale(points, n):
    if len(points) < n:
        return points
    partitions = []
    centers = []
    for i in range(len(points) - 2):
        t = Partition(points[i], points[i + 1], points[i + 2])
        partitions.append(t)
    for p in partitions:
        c = t.center()
        centers.append(c)
    return rescale(centers, n)
