#import sys
#sys.path.append("/home/mpet/rr/midastoeva/")

from os.path import basename
from collections import Counter
#from MidasToEva7 import MidasToEva
from midas2eva import MidasToEva


class SDA(MidasToEva):
    '''
    SDA (Simplified Data Analysis) subclasses the MidasToEva class
    writen by R.R.

    The only added function is 'sda_write' that generates the data files for
    Stephan's simplifiend1Danalysis script.
    '''
    def __init__(self, filename):
        MidasToEva.__init__(self, filename)

    def sda_write(self, path='/triumfcs/trshare/titan/MPET/Data/'):
        '''
        sda_write writes the tof data to a file that can be read by stephan's
        simplified1Danalyis script.
        '''
        evafilename = self.filename[:-4] + '_se_test.dat'
        path2 = path + basename(evafilename)

        try:
            datafile2 = open(path2, 'w')
        except IOError:
            print 'Could not open ' + path2 + ' for writing.'
            return

        datafile2.write('data:' + str(self.startfreq) + '\n')

        for i in xrange(len(self.bindata)):
            hist = Counter(self.bindata[i])
            for j in hist:
                    datafile2.write(str(i) + ' ' + str(j) +
                                    ' ' + str(hist[j]) + '\n')
        datafile2.close()

    def getbindata(self):
        return self.bindata
