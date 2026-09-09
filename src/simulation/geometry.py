from math import *

EARTH_RADIUS_KM = 6371


# uses haversines formula to calculate the distance between 2 coordinates in km
def distBetween(latlong1, latlong2):
    #converts the coordinates into radians
    lat1 = radians(latlong1[0])
    lat2 = radians(latlong2[0])
    lon1 = radians(latlong1[1])
    lon2 = radians(latlong2[1])
    #finds the difference in the latitudes and longitudes of the coordinates
    dLat = (lat2-lat1)
    dLon = (lon2-lon1)
    #uses haversines formula to get distance
    a = sin(dLat/2) * sin(dLat/2) + cos(lat1) * cos(lat2) * sin(dLon/2) * sin(dLon/2)
    distance = EARTH_RADIUS_KM * 2 * atan2(sqrt(a), sqrt(1-a))
    return distance


# calculates bearing based on the start and direction coordinates
def calcBearing(coords1, coords2):
    # Converts latitudes and longitudes to radians
    lat1, lon1 = map(radians, coords1)
    lat2, lon2 = map(radians, coords2)	
    
    lonDiff = lon2 - lon1  #calculates the difference in longitudes
    
    # calculates the x and y coordinates of the bearing
    x = sin(lonDiff) * cos(lat2)
    y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(lonDiff)
    
    # calculates the bearing and converts to degrees
    bearing = atan2(x, y)
    bearing = degrees(bearing)

    #normalises the bearing to make it between 0 & 360 degrees
    return (bearing + 360) % 360  #returns the result


# function to calculate the new point of the drone depending on the initial location, target location and the distance in that direction
def calcNewPoint(originalCoords, directionCoords, distance):
    # converts the initial coordinates to radians
    lat1 = radians(originalCoords[0])
    lon1 = radians(originalCoords[1])
    
    #uses the calcBearing function to generate the bearing and converts it to radians
    bearing = radians(calcBearing(originalCoords, directionCoords))

    # calculates new latitude using haversine formula
    lat2 = asin(
        sin(lat1) * cos(distance / EARTH_RADIUS_KM) +
        cos(lat1) * sin(distance / EARTH_RADIUS_KM) * cos(bearing)
    )

    # calculates new longitude using haversine formula
    lon2 = lon1 + atan2(
        sin(bearing) * sin(distance / EARTH_RADIUS_KM) * cos(lat1),
        cos(distance / EARTH_RADIUS_KM) - sin(lat1) * sin(lat2)
    )

    # converts back to degrees
    lat2 = degrees(lat2)
    lon2 = degrees(lon2)

    return (lat2, lon2) #returns the new point as a coordinate tuple

    
    