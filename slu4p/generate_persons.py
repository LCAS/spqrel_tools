import slu_utils

drinks = slu_utils.lines_to_list('resources/persons_dictionary.txt')

print drinks

for drink in drinks:
    print '\t<category>\n\t\t<pattern>* ' + drink.upper() + ' *</pattern>'
    print '\t\t<template>\n\t\t\t<think>'
    print '\t\t\t\t<set name="Operator">' + drink + '</set>'
    print '\t\t\t</think>\n\t\t\t<srai>START</srai>\n\t\t</template>\n\t</category>\n'
    #print '\t\t\t\t<set name="Customer">' + drink + '</set>'
    #print '\t\t\t\t<set name="topic">TAKEORDER</set>\n\t\t\t</think>\n\t\t\t<srai>START</srai>\n\t\t</template>\n\t</category>\n'

    print '\t<category>\n\t\t<pattern>' + drink.upper() + ' *</pattern>'
    print '\t\t<template>\n\t\t\t<think>'
    print '\t\t\t\t<set name="Operator">' + drink + '</set>'
    print '\t\t\t</think>\n\t\t\t<srai>START</srai>\n\t\t</template>\n\t</category>\n'
    #print '\t\t\t\t<set name="Customer">' + drink + '</set>'
    #print '\t\t\t\t<set name="topic">TAKEORDER</set>\n\t\t\t</think>\n\t\t\t<srai>START</srai>\n\t\t</template>\n\t</category>\n'

    print '\t<category>\n\t\t<pattern>* ' + drink.upper() + '</pattern>'
    print '\t\t<template>\n\t\t\t<think>'
    print '\t\t\t\t<set name="Operator">' + drink + '</set>'
    print '\t\t\t</think>\n\t\t\t<srai>START</srai>\n\t\t</template>\n\t</category>\n'
    #print '\t\t\t\t<set name="Customer">' + drink + '</set>'
    #print '\t\t\t\t<set name="topic">TAKEORDER</set>\n\t\t\t</think>\n\t\t\t<srai>START</srai>\n\t\t</template>\n\t</category>\n'

    print '\t<category>\n\t\t<pattern>' + drink.upper() + '</pattern>'
    print '\t\t<template>\n\t\t\t<think>'
    print '\t\t\t\t<set name="Operator">' + drink + '</set>'
    print '\t\t\t</think>\n\t\t\t<srai>START</srai>\n\t\t</template>\n\t</category>\n'
    #print '\t\t\t\t<set name="Customer">' + drink + '</set>'
    #print '\t\t\t\t<set name="topic">TAKEORDER</set>\n\t\t\t</think>\n\t\t\t<srai>START</srai>\n\t\t</template>\n\t</category>\n'

