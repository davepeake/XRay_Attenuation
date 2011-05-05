'''
nistxcom.py

Retrieves various data from the NIST XCOM Site
'''
import urllib
import math
import pickle
    
url = 'http://physics.nist.gov/cgi-bin/Xcom/xcom3_1-t'

def getdata(zsym='',znum='',Energies=''):
    '''
    Retrieves the mass attenuation coefficients for the element defined by either
    znum or zsym. If both are provided, znum is used preferentially.
    '''

    if znum != '':
        zsym == ''
        
    postdict = { 'ZNum':znum,
                 #'ZSym':'Cu',
                 'ZSym':zsym,
                 'Name':'',
                 'Energies':Energies,
                 'Output':'on',
                 'OutOpt':'PIC'}

    #print 'Encoding Request'
    postdata = urllib.urlencode(postdict)
    #print 'Retrieving URL'
    a = urllib.urlopen(url,postdata)
    #a = urllib.urlopen(url,postdict)
    b = a.readlines()
   
    ''' 
    fout = open('test.html','w')
    for line in b:
        fout.write(line)
    fout.close()
    '''
             
    headers = b[0:12]

    datalines = b[13:len(b)-4]

    data = []
    energies = []

    skip = 0
    
    for line in datalines:
        line = line.rstrip('\n').lstrip(' ')
        linesplit = line.split(' ')
        if len(line) != 0:
            data.append(eval(linesplit[-2]))
            if not skip: # no shell information on the line
                energies.append(eval(linesplit[0]))
            else:
                coltry = 2
                while coltry < len(linesplit):
                    try:
                        energies.append(eval(linesplit[coltry]))
                    except:
                        coltry += 1
                    else:
                        break
                if coltry == len(linesplit):
                    data.remove(energies[-1]) # it didn't work, so just go to next line
                    print 'Problem at line', line
                skip = 0
        else:
            skip = 1

    return energies,data

def plotlengths(elements,energies=''):
    '''
    Plot attenuation lengths versus Energy
    '''
    import pylab

    densities = pickle.load(open('densities.dat','rb'))

    for element in elements:
        print 'Plotting',element
        try:
            rho = densities[element]
        except:
            print 'Unknown element, ', element
        else:
            [E,massatt] = getdata(element,Energies=energies)
            
            attlength = len(massatt) * [0]

            for i in range(len(massatt)):
                attlength[i] = 1.0 / (massatt[i] * rho)

            pylab.loglog(E,attlength,label=element)

    pylab.xlabel('Energy (MeV)')
    pylab.ylabel('Attenuation Length (cm)')
    pylab.legend(loc='lower right')
    pylab.grid()
    pylab.show()

def calclengths(elements,energies=''):
    '''
    Plot attenuation lengths versus Energy
    '''
    attlength = {}
    es = {}

    densities = pickle.load(open('densities.dat','rb'))

    for element in elements:
        #print 'Retrieving Data For: ',element
        try:
            rho = densities[element]
        except:
            print 'Unknown element, ', element
        else:
            [E,massatt] = getdata(element,Energies=energies)

            attlength_buff = len(massatt) * [0]

            for i in range(len(massatt)):
                attlength_buff[i] = 1.0 / (massatt[i] * rho)
	    
	    attlength[element] = attlength_buff 
	    es[element] = E

    return [es,attlength]
                 
def plotlengths(elements):
    '''
    Plot attenuation lengths versus Energy
    '''
    import pylab

    densities = pickle.load(open('densities.dat','rb'))

    for element in elements:
        print 'Plotting',element
        try:
            rho = densities[element]
        except:
            print 'Unknown element, ', element
        else:
            [E,massatt] = getdata(element)

            attlength = len(massatt) * [0]

            for i in range(len(massatt)):
                attlength[i] = 1.0 / (massatt[i] * rho)

            pylab.loglog(E,attlength,label=element)

    pylab.xlabel('Energy (MeV)')
    pylab.ylabel('Attenuation Length (cm)')
    pylab.legend(loc='lower right')
    pylab.grid()
    pylab.show()


def geteff(elements,energies='',length=100E-6):
    '''
    Plot attenuation lengths versus Energy
    '''
    length = length*100; # convert from m to cm

    densities = pickle.load(open('densities.dat','rb'))

    for element in elements:
        print 'Plotting',element
        try:
            rho = densities[element]
        except:
            print 'Unknown element, ', element
        else:
            [E,massatt] = getdata(element,Energies=energies)
            E.sort()
            attlength = len(massatt) * [0]
            abs_eff = len(massatt) * [0]
            
            for i in range(len(massatt)):
                attlength[i] = 1.0 / (massatt[i] * rho)
                abs_eff[i] = (1 - math.exp( - length / attlength[i])) * 100

    return [E,abs_eff]

def ploteff(elements,energies='',length=100E-6):
    '''
    Plot attenuation lengths versus Energy
    '''
    length = length*100; # convert from m to cm

    import pylab

    densities = pickle.load(open('densities.dat','rb'))

    for element in elements:
        print 'Plotting',element
        try:
            rho = densities[element]
        except:
            print 'Unknown element, ', element
        else:
            [E,massatt] = getdata(element,Energies=energies)
            E.sort()
            attlength = len(massatt) * [0]
            abs_eff = len(massatt) * [0]
            
            for i in range(len(massatt)):
                attlength[i] = 1.0 / (massatt[i] * rho)
                abs_eff[i] = (1 - math.exp( - length / attlength[i])) * 100

            pylab.plot([i*1000 for i in E],abs_eff,label='320 um Silicon',linewidth=3) #element)

    pylab.plot([10], [abs_eff[9]], 'r.', markersize=10,label='10 keV')
    pylab.plot([150], [abs_eff[18]], 'k.', markersize=10,label='150 keV')
    pylab.xlabel('Energy (keV)')
    pylab.ylabel('Absorbtion Efficiency (%)')
    pylab.legend(loc='upper right')
    pylab.title('Efficiency vs Energy')
    #pylab.xlim([0, 160])
    pylab.ylim([2,105])
    pylab.grid()

    pylab.show()

def calc_attenuation(element, length, energy):
    length = length * 100 # converts from m to cm
    '''
    Calculate the attenuation of a foil of element x and length y at xray energy y
    '''

    densities = pickle.load(open('densities.dat','rb'))

    try:
        rho = densities[element]
    except:
        print 'Unknown element, ', element
    else:
        [E, massatt_list] = getdata(zsym=element,Energies=str(energy))

        massatt = massatt_list[E.index(energy)]

        attlength = 1.0 / (massatt * rho)

    '''
    attenuation = No/Ni = exp(-length/attlength) ??
    '''
    print element
    print 'Attenuation Length: ', attlength
    print 'Attenuation: ', 1-math.exp(-length/attlength)
    print 'Transmission: ', math.exp(-length/attlength)
    
    return 1 - math.exp(-length/attlength)
