import tornado.options
import argparse

def load(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', default='config.py')
    args, remaining = parser.parse_known_args(args)
    try:
        tornado.options.parse_config_file(args.config)
    except IOError:
        print 'Missing file %s. Using defaults.' % (args.config,)

    # parse_command_line ignores first argument
    remaining = [''] + remaining
    tornado.options.parse_command_line(remaining)

    return tornado.options.options

if __name__ == '__main__':
    for k in sorted(tornado.options.options.iterkeys()):
        line = k + '='
        value = tornado.options.options[k].value()
        if type(value) == str:
            line += "'%s'" % value.replace("\\", "\\\\").replace("'", "\\'")
        else:
            line += str(value)
        print line


def out():
    load()
    for k in sorted(tornado.options.options.iterkeys()):
        line = k + '='
        value = tornado.options.options[k].value()
        if type(value) == str:
            line += "'%s'" % value.replace("\\", "\\\\").replace("'", "\\'")
        else:
            line += str(value)
        print line
