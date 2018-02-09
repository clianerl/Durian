#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import time
import argparse
import logging
import traceback

from .log import logger
from .cli import start

from .__version__ import __title__, __introduction__, __url__, __version__
from .__version__ import __author__, __author_email__, __license__
from .__version__ import __copyright__, __epilog__

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except NameError as e:
    pass


def main():
    try:
        # arg parse
        t1 = time.time()
        parser = argparse.ArgumentParser(prog=__title__, description=__introduction__, epilog=__epilog__, formatter_class=argparse.RawDescriptionHelpFormatter)

        parser_group_scan = parser.add_argument_group('Scan')
        parser_group_scan.add_argument('-t', '--target', dest='target', action='store', default='None', metavar='<target>', help='file, folder')
        parser_group_scan.add_argument('-o', '--output', dest='output', action='store', default='None', metavar='<output>', help='vulnerability output MAIL')
        parser_group_scan.add_argument('-r', '--rule', dest='special_rules', action='store', default="None", metavar='<rule_id>', help='specifies rules e.g: CVI-100001,cvi-190001')

        args = parser.parse_args()

        if args.target == "None" or not os.path.isdir(args.target) or not os.path.isdir(args.target):
            parser.print_help()
            exit()
        else:
            logger.info("target ==" + args.target)
            logger.info("output == " + args.output)
            logger.info("rule == " + args.special_rules)
            cli.start(args.target, args.output, args.special_rules)
        t2 = time.time()
        logger.info('[INIT] Done! Consume Time:{ct}s'.format(ct=t2 - t1))
    except Exception as e1:
        logger.critical('main exception ({e})'.format(e=e1.message))
        exc_msg = traceback.format_exc()
        logger.warning(exc_msg)


if __name__ == '__main__':
    main()
