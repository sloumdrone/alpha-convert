#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sqlite3, sys, re, os, os.path

version = '\n   alpha-convert\n   Version 0.1\n'

class Book:
    def __init__(self,text_path):
        self.textfile = text_path
        self.word_map = {}
        self.unique_words = set()
        self.text_list = []

    def add_word_location(self, word, pos):
        if not self.word_map.has_key('word'):
            inner = {
                "translation": '',
                "loc": []
            }

            self.word_map[word] = inner

        self.word_map[word]['loc'].push(pos)

    def get_uniques(self):
        with open(self.textfile) as book:
            data = book.read().lower()

            data = data if isinstance(data, unicode) else data.decode('utf8')

            self.text_list = re.findall(r"[\w'’]+|\n|\r|\t|\S{1}",data)


        for word in self.text_list:
            self.unique_words.add(word)




def parse_args():
    args = sys.argv[1:]

    if len(args) < 1:
        print_error('INPUT ERROR: At least one operator must be provided\n    See: --help\n')
        return False

    command = args[0]

    if command == 'help' or command == '-h' or command == '--help':
        print '''
    alpha-convert command [options]

    commands:
    help, -h, --help                        Display this help message

    version, -v, --version                  Display the version number

    build input_file [new_db]               Add new words from input file to existing db,
                                            if no db is provided, or if the provided db does
                                            not exist, a db will be created and seeded with
                                            words from the input file

    convert input_file db                   Convert a file using a partifular db, if
                                            the db has empty words, you will be notified
                                            and given the option to fill them in or
                                            continue by inserting empty strings in place
                                            of unknown words

    update [db]                             Will go word by word to get updated
                                            transliterations for each word in the db
                                            that does not have a conversion set'''

    elif command == 'version' or command == '-v' or command == '--version':
        print version
    elif command == 'build':
        if len(args) < 4 and len(args) > 1:
            if len(args) == 3:
                db = args[2]
            else:
                db = './alpha-convert.db'

            text = args[1]

            book = Book(text)

            if not os.path.isfile(db):
                db_conn = sqlite3.connect(db)
                c = db_conn.cursor()
                c.execute("CREATE TABLE main (from_text text PRIMARY KEY, to_text text)")
                db_conn.commit()
                db_conn.close()

            book.get_uniques()

            # add code to write to table all of the words in book.unique_words
            # but do so without overwriting existin entries
            #
            db_conn = sqlite3.connect(db)
            c = db_conn.cursor()
            counter = 0
            for word in book.unique_words:
                try:
                    c.execute("INSERT INTO main (from_text,to_text) VALUES(?, '')",(word,))
                    counter += 1
                except:
                    continue
            db_conn.commit()
            db_conn.close()

            print str(counter) + ' words successfully added to the database'
        else:
            print 'INPUT ERROR:\nImproper number of parameters supplied to "build"'
    elif command == 'update':
        if len(args) == 2:
            db = args[1]
            try:
                db_conn = sqlite3.connect(db)
                c = db_conn.cursor()
                c.execute('''SELECT * FROM main WHERE to_text = '' or to_text is NULL ORDER BY length(from_text) ASC''',)
                word_list = []
                for word in c:
                    word_list.append(word[0])
                db_conn.commit()
                db_conn.close()
            except:
                print 'There was an error retrieving words from the database'
                return False


            print '\n*************************************\nFor each word, please provide the equivalent in the alternate script\nto quit before completing all text enter: \q\n*************************************\n'

            for index, word in enumerate(word_list):
                print '\n' + str(len(word_list) - index) + ' words remain.'
                query =  u'- {}: '.format(word).encode('utf8')
                # query = query if isinstance(query,unicode) else query.encode('utf8')
                to_text = raw_input(query)
                to_text = to_text if isinstance(to_text,unicode) else to_text.decode('utf8')
                if to_text == '\q':
                    sys.exit('          ...exiting')
                elif to_text == '\s':
                    print 'Skipped!'
                    continue
                elif to_text == '\d':
                    delete_entry(word,db)
                    continue
                elif to_text == '\c':
                    to_text = word
                    print 'Word copied!'


                if update_entry(word,to_text,db):
                    print 'Success!\n'
                else:
                    print 'That word did not get updated :(\n'
            print 'Finished updating the database!'


        else:
            print 'INPUT ERROR:\nImproper number of parameters supplied to "update"'
    else:
        print 'mumble mumble\nstuff stuff'


def update_entry(original,new,db):
    db_conn = sqlite3.connect(db)
    c = db_conn.cursor()
    c.execute("UPDATE main SET to_text = ? WHERE from_text = ?",(new,original))
    success = c.rowcount
    db_conn.commit()
    db_conn.close()
    if success:
        return True
    return False

def delete_entry(original, db):
    db_conn = sqlite3.connect(db)
    c = db_conn.cursor()
    c.execute("DELETE FROM main WHERE from_text = ?",(original,))
    success = c.rowcount
    db_conn.commit()
    db_conn.close()
    if success:
        return True
    return False


if __name__ == "__main__":
    parse_args()
