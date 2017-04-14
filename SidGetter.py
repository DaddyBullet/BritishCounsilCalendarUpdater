from HTMLParser import HTMLParser

class SidGetter(HTMLParser, object):
    def __init__(self):
        super(SidGetter, self).__init__()
        self.find_tag = 0
        self.sid = ''


    def handle_starttag(self, tag, attrs):
        if tag == 'div' and attrs == [('class', 'rightContent')]:
            self.find_tag = 1

    def handle_data(self, data):
        if self.find_tag == 1 :
            self.find_tag += 1
        elif self.find_tag == 2:
            self.sid = data[data.index('=')+2:data.index(';')]
            self.find_tag = 0
