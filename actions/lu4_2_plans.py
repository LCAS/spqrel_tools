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
  ( "SAY(message=\"joke\",beneficiary=\"%2\",goal=\"%1\") ")),
  (r'answer a question (.*)',
  ( "ANSWER(message=\"joke\") ")),
  (r'navigate (.*) ',
  ( "SAY(message=\"joke\") ")),
  (r'(tell me|say) how many (.*) there are (.*)',
  ( "BEING_LOCATED(located=\"%2\", theme=\"%1\") ")),
  (r'(.*) how many (.*) there are (.*)',
  ( "BEING_LOCATED(located=\"%2\", theme=\"%1\") ")),
)


#
if __name__ == "__main__":

    re_plans = [(re.compile(x, re.IGNORECASE),y) for (x,y) in pairs_say]
    re_upper=re.compile(r'[A-Z]+')

    message = ""
    while message != quit:
        message = quit
        try: message = raw_input("Enter your message: ")
        except EOFError:
            print 'except'
            print(message)
        if message:
            answer=None
            for (pattern, response) in re_plans:
                
                match = pattern.match(message)
                
                if match:
                    answer=response
            print 'BOT>> ', answer
