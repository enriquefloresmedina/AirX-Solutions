def quality(pm25):
    if pm25 < 0:
        return "Not a valid input"
    
    if pm25 <= 15:
        return "Optimal air quality"
    elif pm25 > 15 and pm25 <= 25:
        return "Good air quality"
    elif pm25 > 25 and pm25 <= 50:
        return "Acceptable air quality" 
    elif pm25 > 50 and pm25 <= 100:
        return "Low air quality" 
    elif pm25 > 100 and pm25 <= 150:
        return "Very low air quality" 
    elif pm25 > 150 and pm25 <= 200:
        return "High risk PM2.5 concentration" 
    elif pm25 > 200 and pm25 <= 300:
        return "Very high risk PM2.5 concentration"
    else:
        return "Critical amount of PM2.5"
    