import optparse
import re

parser = optparse.OptionParser()
parser.add_option("-a", "--arga")
parser.add_option("-b", "--argb")
parser.add_option("-c", "--argc")
options, argv = parser.parse_args()
opt = {}
print "option =", dir(options)
print "argv =",  argv
print "opt =", opt
