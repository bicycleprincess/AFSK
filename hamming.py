import textwrap
import logging
import Queue
from convertions import *
from baudot import *

# https://en.wikipedia.org/wiki/Hamming(7,4)

zero = '0'
one = '1'
backup = Queue.Queue()

logging.basicConfig(level=logging.INFO)

TABLE = {
    "0000": "0000000",
    "1000": "1110000",
    "0100": "1001100", #0011001
    "1100": "0111100", #0011110
    "0010": "0101010", #0101010
    "1010": "1011010", #0101101
    "0110": "1100110", #0110011
    "1110": "0010110", #0110100
    "0001": "1101001", #1001011
    "1001": "0011001", #1001100
    "0101": "0100101", #1010010
    "1101": "1010101", #1010101
    "0011": "1000011", #1100001
    "1011": "0110011", #1100110
    "0111": "0001111", #1111000
    "1111": "1111111" 
}


def Hammingencoder(s, span=4):

    en = []

    if len(s) % span == 0:
        
        data = tuple(textwrap.wrap(s, span))

        for datum in data:
            for origin, code in TABLE.iteritems():
                if origin == datum:
                    en.extend(code) 

    else:
        remainder = len(s) % span
        main = s[:-remainder]
        sub = s[-remainder:]
        data = tuple(textwrap.wrap(main, span))
        
        for datum in data:
            for origin, code in TABLE.iteritems():
                if origin == datum:
                    en.extend(code)

        en.extend(sub)

    return list2string(en)


def _Hammingdecoder(s, span=7):
    print s
    de = []
    try:
        index_zero = s.index(zero*7)
        amount_zero = s.count(zero*7)
        string = s[index_zero:len(s)]
        strings = tuple(textwrap.wrap(string, span))
        for i in strings:
    
            if len(i) == span:
                for origin, code in TABLE.iteritems():
                    if code == i:
                        de.extend(origin)
            else:
                de.extend(i)
        return list2string(de)
    except ValueError:
        logging.info('error in hamming decoder')
    except AttributeError:
        logging.info('error')

    return list2string(de)    


def _Hammingcorrector(s, num=7):

    rst = []
    #p = (0,1,3)
    #d = (2,4,5,6)
    p1 = (0,2,4,6)
    p2 = (1,2,5,6)
    p4 = (3,4,5,6)

    if zero*8 in s:

        begin = s.index(zero*8)+1
        string = s[begin:len(s)]
        strings = tuple(textwrap.wrap(string, num))
        for i in strings:

            if len(i) == num:

                t4 = parity(i, p4)
                t2 = parity(i, p2)
                t1 = parity(i, p1)

            if t4+t2+t1 != zero*3:

                index = (int(t4+t2+t1, 2)) - 1
                sub = [e for e in i]
                if sub[index] == zero:
                    sub[index] = 1
                else:
                    sub[index] = 0
                rst.extend(sub)

            else:
                rst.extend(i)
    elif zero*num in s:

        begin = s.index(zero*7)
        string = s[begin:len(s)]
        strings = tuple(textwrap.wrap(string, num))

        for i in strings:

            if len(i) == num:

                t4 = parity(i, p4)
                t2 = parity(i, p2)
                t1 = parity(i, p1)

            if t4+t2+t1 != zero*3:
                index = (int(t4+t2+t1, 2)) - 1
                sub = [e for e in i]
                if sub[index] == zero:
                    sub[index] = 1
                else:
                    sub[index] = 0
                rst.extend(sub)

            else:
                rst.extend(i)
    else:
        logging.info('error in hamming corrector')

    return list2string(rst)
    #return decodeBaudot(rst)


def _Hammingcorrector(s, num=7):

    global backup

    pattern = one*num+zero*num
    pitfall = one*8+zero*8
    n = s.count(pattern)
    #print n

    if n == 2:
        if backup.empty():
            #print 1
            if s.index(pattern) <= len(s)/2:

                if zero*8 in s:
                    try:    
                        begin = s.index(zero*8)+1
                        string = s[begin:len(s)]
                        new_begin = string.index(zero*num)
                        end = string.index(pattern)
                        new_string = string[new_begin:end]
                        sub = string[end+num:]
                        backup.put(sub)
                        return check(new_string)
                    except ValueError:
                        logging.info('error n=2 zero*8')

                elif zero*num in s:
                    #print 3
                    try:
                        begin = s.index(zero*num)
                        string = s[begin:len(s)]
                        new_begin = string.index(zero*num)
                        end = string.index(pattern)
                        new_string = string[new_begin:end]
                        sub = string[end+num:]
                        backup.put(sub)
                        return check(new_string)
                    except ValueError:
                        logging.info('error n=2 zero*7')

        else:
            #print 3
            sub = s[:s.index(pattern)]
            glue(sub)
            string = s[s.index(pattern)+7:]
            new_begin = string.index(zero*num)
            end = string.index(pattern)
            new_string = string[new_begin:]
            return check(new_string)

    elif n == 1:
        if pitfall not in s:
            #print 'no pitfall'
            if s.index(pattern) < len(s)/2:
                #if zero*8 in s:
                #    #print 4
                #    begin = s.index(zero*8)+1
                #    string = s[begin:len(s)]
                #    new_begin = string.index(zero*num)
                #    new_string = string[new_begin:len(string)]
                #    return check(new_string)

                if zero*num in s:
                    #print 5
                    begin = s.index(pattern)
                    string = s[begin:len(s)]
                    new_begin = string.index(zero*num)
                    new_string = string[new_begin:len(string)]
                    return check(new_string)

            else:
                if s.index(zero*num) != s.index(pattern)+num:
                    #print 6
                    begin = s.index(zero*num)
                    string = s[begin:len(s)]
                    new_begin = string.index(zero*num)
                    new_string = string[new_begin:len(string)]
                    sub_begin = s.index(pattern)
                    sub_string = s[sub_begin:len(s)]
                    backup.put(sub_string)
                    #logging.info('put one')
                    return check(new_string)

                else:
                    begin = s.index(pattern)
                    string = s[begin:len(s)]
                    if zero*8 in string:
                        #print 7
                        new_begin = string.index(zero*8) + 1
                        new_string = string[new_begin:len(string)]
                        backup.put(new_string)
                        #logging.info('put two')
                    elif zero*num in string:
                        #print 8
                        new_begin = string.index(zero*num)
                        new_string = string[new_begin:len(string)]
                        backup.put(new_string)
                        #logging.info('put three')
        else:

            if s.index(pattern) > len(s)/2:
                #print 9
                string = s[:s.index(pattern)]
                #logging.info('glue process four')
                return glue(string)
    else:
        if n == 0:
      #      if zero*8 in s:
      #          #print 10
      #          begin = s.index(zero*8)+1
      #          new_string = s[begin:len(s)]
      #          return check(new_string)

      #      elif zero*num in s:
      #          #print 11
      #          begin = s.index(zero*num)
      #          new_string = s[begin:len(s)]
      #          return check(new_string)
      #      
      #      else:
      #          print 12
      #          #logging.info('glue process two')
                return glue(s)


def Hammingdecoder(s, span=7):
    de = []
    if s != None:
        try:
            strings = tuple(textwrap.wrap(s, span))
    
            for i in strings:
        
                if len(i) == span:
                    for origin, code in TABLE.iteritems():
                        if code == i:
                            de.extend(origin)
                else:
                    de.extend(i)
            return list2string(de)
        except ValueError:
            logging.info('error in hamming decoder')
        except AttributeError:
            logging.info('error')


def parity(s, indicies):
    alist = [s[i] for i in indicies]
    sub = ''.join(alist)
    return str(str.count(sub, '1') % 2) 


def check(s, num=7):
    rst = []

    p1 = (0,2,4,6)
    p2 = (1,2,5,6)
    p4 = (3,4,5,6)

    strings = tuple(textwrap.wrap(s, num))

    for i in strings:
        #print i
        if len(i) == num:
            #print i
            t4 = parity(i, p4)
            t2 = parity(i, p2)
            t1 = parity(i, p1)

            if t4+t2+t1 != zero*3:
                #print i
                index = (int(t4+t2+t1, 2)) - 1
                sub = [e for e in i]
    
                if sub[index] == zero:
                    sub[index] = 1
                else:
                    sub[index] = 0
                
                rst.extend(sub)
            else:
                rst.extend(i)
        else:
            rst.extend(i)
    return list2string(rst)


def Hammingcorrector(s, num=7):

    global backup
    #print ''
    sign = '101010101010'
    n = s.count(sign)
    #print s
    #print n

    if n == 2:
        if backup.empty():
            #print 'n = 2 and empty'
            try:
                #print s
                #print 'here'
                begin = s.index(sign) + len(sign)
                string = s[begin:]
                new_begin = string.index(sign)
                new_string = string[new_begin+len(sign):]
                backup.put(new_string)
                #print 'put ', new_string
                #print 'check ', string 
                return check(string)
            except ValueError:
                logging.info('n=2 first try')

        else:
            sub = s[:s.index(sign)]
            glue(sub)
            string = s[s.index(sign)+len(sign):]
            return check(string)

    elif n == 1:
        #print 'yes'
        if not backup.empty():
            #print 'n = 1 and not empty'
            try:
                sub = s[:s.index(sign)]
                glue(sub)
                string = s[s.index(sign)+len(sign):]
                #print 'check ', string
                return check(string)
            except ValueError:
                logging.info('n = 1 and first try')
        else:
            #print 'n = 1 and empty'
            if s.index(sign) <= len(s) / 2:
                #print 'yes'
                try:
                    string = s[s.index(sign)+len(sign):]
                    return check(string)
                except ValueError:
                    logging.info('n = 1 and second try')

            elif s.index(sign) > len(s) / 2:
               # print 'hi'
                string = s[s.index(sign)+len(sign):]
                backup.put(string)
    elif n == 0:
        if not backup.empty():
            #print 'n = 0 and not empty'
            #print s
            glue(s)
        else:
            #print 'n = 0 and empty'
            return check(s)


def _glue(piece):

    global backup
    if not backup.empty():

        if backup.qsize() > 2:
            backup.queue.clear()
        else:
            begin = backup.get()
            s = begin + piece
            Hammingcorrector(s)
            #return Hammingcorrector(s)
    
    # THINK!!!
#   else:
#       return Hammingcorrector(piece)

def glue(piece):

    global backup
    if not backup.empty():

        if backup.qsize() > 2:
            backup.queue.clear()
        else:
            begin = backup.get()
            #print 'in glue ', piece
            s = begin + piece
            #print 'in glue ', s
            crct = Hammingcorrector(s)
            de = Hammingdecoder(crct)
            print decodeBaudot(de)
            #return hammingcorrector(s)
            #return check(s)
    # THINK!!!


def _test_for_corrector():

    print 'test_for_corrector'
    s = 'x=1.23 y=4.56'
    baudot = list2string(encodeBaudot(s))
    en = Hammingencoder(baudot)
    print en    
    wrong = '0000000101001010011000100101011001110100001001100010010100001001001100110100111100001001100111000001010101010101101010101010101000011011110000110010'
    print wrong
    crct = Hammingcorrector(wrong)
    print crct
    de = Hammingdecoder(crct)
    decodeBaudot(de)
    print ''


def _main():

    print 'main'
    s = 'x1234567890'
    baudot = list2string(encodeBaudot(s))
    en = Hammingencoder(baudot)
    crct = Hammingcorrector(en)
    #print crct
    de = Hammingdecoder(crct)
    decodeBaudot(de)
    print originaldecodeBaudot(de)
    print ' '


def _test_for_glue():

    print 'test_for_glue'
    
    s1 = '1111111111111111111111111111111111100000001011010100110001001010000000100110011010010101010001100101111000011001010101011100001010101110011111111000000010110101001100010010100000001001100110100'
    s2 = '1010101000110010111100001100101010101110000101010111001111111100000001011010100110001001010000000100110011010010101010001100101111000011001010101011100001010101110011011111110000000101101010011'
    s3 = '00100101000000010011001101001010101000110010111100001100101010101110000101010111001101111111000000010110101001100010010100000001001100110100101010100011001011110000110010101010111000010101011100'
    s4 = '1101111111110000000101101010011000100101000000010011001101001010101000110010111100001100101010101110000101010111001111111111000000010110101001100010010100000001001100110100101010100011001011110'
    s5 = '00011001010101011100001010101110011111111111111111111000000010110101001100010010100000001001100110100101010100011001011110000110010101010111000010101011100111111111111111110000000101101010011000'
    s6 = '1001010000000100110011010010101010001100101111000011001010101011100001010101110011111111111111111111111111111111111111111111111111111111111100000001011010100110001001010000000100110011010010101'
    s7 = '0100011001011110000110010101010111000010101011100111111111111111111111111111111111111111111111111111111111111111111100000000000000000000000000000000000000111111111101111111011111111111111111111'

    crct = Hammingcorrector(s1)
    de = Hammingdecoder(crct)
    decodeBaudot(de)
    #print 2
    crct = Hammingcorrector(s2)
    de = Hammingdecoder(crct)
    decodeBaudot(de)
    #print 3
    crct = Hammingcorrector(s3)
    de = Hammingdecoder(crct)
    decodeBaudot(de)

    crct = Hammingcorrector(s4)
    de = Hammingdecoder(crct)
    decodeBaudot(de)

    crct = Hammingcorrector(s5)
    de = Hammingdecoder(crct)
    decodeBaudot(de)

    crct = Hammingcorrector(s6)
    de = Hammingdecoder(crct)
    decodeBaudot(de)    

    crct = Hammingcorrector(s7)
    de = Hammingdecoder(crct)
    decodeBaudot(de)

    print ''


def new_test():
    s1 = '1111111110101010101011010011001100110100100000001001100101101000011110101010100110010110101000011010010101111111111111111111111111111111111111111101010101010110100100011111011010011110011001100'
    s2 = '1001011001100011001100110011001100010101001010100111111111111111111111111111111111111111111111111111111111010101010101101001100110001010100111100110011000110010001111101101001001010010110111000'
    s3 = '0101010100001110101011111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111101010101010110100111010010101010100001100000001011010100110010000110011001110011'
    s4 = '0100110010011000111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111110101010101011010011001100010101010101011100110111111110011001101001000000011100'
    s5 = '0011111110001111111111111111111111111111111111000000000000000000000001100010000000010000011111111111111110111111111111111111111111111111111111111111111111111100000000000000000000000001100000000'

    crct = Hammingcorrector(s1)
    de = Hammingdecoder(crct)
    print originaldecodeBaudot(de)

    crct = Hammingcorrector(s2)
    de = Hammingdecoder(crct)
    print originaldecodeBaudot(de)

    crct = Hammingcorrector(s3)
    de = Hammingdecoder(crct)
    print originaldecodeBaudot(de)

    crct = Hammingcorrector(s4)
    de = Hammingdecoder(crct)
    print originaldecodeBaudot(de)

    crct = Hammingcorrector(s5)
    de = Hammingdecoder(crct)
    print originaldecodeBaudot(de)
#"""
if __name__ == '__main__':
#    main()
#    test_for_glue()
#    test_for_corrector()
    new_test()
#"""
