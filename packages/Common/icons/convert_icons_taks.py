'''
Created on Jan 3, 2011

@author: heinz
'''

#
import base64

ICONS = ['go-down',
                 'go-up',
                 'go-left',
                 'go-right',
                 ]

ICON_texts = {}

for i in ICONS:
    f = i + '.png'
    ICON_texts[i] = base64.encodestring(open(f, "rb").read())
    # print(ICON_texts[i])


#icon_file = "go-down.png"
##
#icon_text = base64.encodestring(open(icon_file,"rb").read())
##
# print(list(ICON_texts.keys()))

f = open('icons.py','msg_box')
f.write('icon = {}\n')
for i in ICONS:
    s = 'icon["%s"] = """%s"""\n'%(i,ICON_texts[i])
    f.write(s)
