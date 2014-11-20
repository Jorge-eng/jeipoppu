#!/usr/bin/python
import numpy as np

k_fixed_point = 10

k_disturbance_threshold_db = 10

#numbers are in fixed point format
#numbers are log2, and we want to convert then to 20*log10
#we want maximum
#we want number of "disturbances" as compared to some threshold

def get_as_floating_point(x):
    return x.astype(float) / float((1 << k_fixed_point))
    
def get_as_db_from_log2(x):
    y = x*6.0; #every power of 2 is about 6dB

#supposed to operate on a minute's worth of data
def get_energy_summary(energysignal, maxenergies):
    xe = get_as_db_from_log2(get_as_floating_point(energysignal))
        
    maxenergy_in_db = np.amax(xe)
    
    disturbance_count = 0
    
    #make this simple
    if (maxenergy_in_db > k_disturbance_threshold_db):
        disturbance_count = 1;
        
        
    return (max_energy_in_db, disturbance_count)
    
