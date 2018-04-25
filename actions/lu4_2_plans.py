#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re
import random
from collections import namedtuple


pairs_say = (
  (r'(tell me|say) something about yourself',
  ( "SAY(message=\"peppino\") ")),
  (r'(tell me|say) the time',
  ( "SAY(message=\"time\") ")),
  (r'(tell me|say) what day is tomorrow',
  ( "SAY(message=\"tomorrow\") ")),
  (r'(tell me|say) what day is today',
  ( "SAY(message=\"day\") ")),
  (r'(tell me|say) your team name',
  ( "SAY(message=\"teamname\") ")),
  (r'(tell me|say) your country ',
  ( "SAY(message=\"teamcountry\") ")),
  (r'(tell me|say) your team affiliation',
  ( "SAY(message=\"teamaffiliation\") ")),
  (r'(tell me|say) (.*) day (.*) week',
  ( "SAY(message=\"weekday\") ")),
  (r'(tell me|say) (.*) day (.*) month',
  ( "SAY(message=\"monthday\") ")),
  (r'(tell me|say) (.*) joke',
  ( "SAY(message=\"joke\") ")),
  (r'(tell|say) (.*) joke to (.*) in (.*)',
  ( "SAY(message=\"joke\",beneficiary=\" %2 \",goal=\" %1 \") ")),
  (r'answer a question (.*)',
  ( "ANSWER(message=\"joke\") ")),
  (r'navigate (.*) ',
  ( "SAY(message=\"joke\") ")),
  (r'(tell me|say) how many (.*) there are (.*)',
  ( "BEING_LOCATED(located=\"%3\", theme=\"%2\") ")),
  (r'how many (.*) there are (.*)',
  ( "BEING_LOCATED(located=\"%2\", theme=\"%1\")")),
)

reflections = {
  "the "       : "",
  "in the "       : "",
  "to the "       : "",
  "at the "       : "",  
  "on the "       : "" 
}

#

Inputnamefile='./GPSR_examples' #'./test_input_lu4'
Inputmode='file' # file, terminal

class Test2lu4(object):
    def __init__(self, pairs, reflections={}):

        self._pairs = [(re.compile(x, re.IGNORECASE),y) for (x,y) in pairs_say]
        self._reflections = reflections
        self._regex = self._compile_reflections()


    def _compile_reflections(self):
        sorted_refl = sorted(self._reflections.keys(), key=len,
                reverse=True)
        return  re.compile(r"\b({0})\b".format("|".join(map(re.escape,
            sorted_refl))), re.IGNORECASE)

    def _substitute(self, str):

        #Substitute words in the string, according to the specified reflections,

        return self._regex.sub(lambda mo:
                self._reflections[mo.string[mo.start():mo.end()]],
                    str.lower())

    def _wildcards(self, response, match):
        pos = response.find('%')
        while pos >= 0:
            num = int(response[pos+1:pos+2])
            response = response[:pos] + \
                self._substitute(match.group(num)) + \
                response[pos+2:]
            pos = response.find('%')
        return response


    def inputtext(self, txt):
        # check each pattern
        for (pattern, response) in self._pairs:
            #print 'pattern=',str(pattern)
            match = pattern.match(txt)

            if match:
                if len(response)>1:
                    resp = response    
                
                resp = self._wildcards(resp, match) # process wildcards

                return resp


        
if __name__ == "__main__":

    text2lu4=Test2lu4(pairs_say, reflections)
    
    if  Inputmode == 'file':
        
        finput = open(Inputnamefile, 'r')
        for message in finput:
            message=message.lower()

            answer=text2lu4.inputtext(message)
            print message
            print 'LU4>> ', answer
            print '_____'
