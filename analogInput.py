import math

def temperatureReading(temp):
    # calculate Temperature
    try:

        R1 = 1000
        c1 = 1.009249522e-03
        c2 = 2.378405444e-04
        c3 = 2.019202697e-07
        R2 = R1 * (1023.0 / temp - 1.0)
        logR2 = math.log(R2, 10)
        T = (1.0 / (c1 + c2 * logR2 + c3 * logR2 * logR2 * logR2))
        temperature = T - 373.15
        print('Temperature : ', temperature, 'C')
        return temperature

    except:
        print('Temperature Value Error!!!!!')

