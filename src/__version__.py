import sys
import platform

__title__ = 'cobra'
__description__ = 'Code Security Audit'
__url__ = 'https://github.com/DurianCoder/Durian'
__issue_page__ = 'https://github.com/DurianCoder/Durian'
__python_version__ = sys.version.split()[0]
__platform__ = platform.platform()
__version__ = '1.0-Durian'
__author__ = 'jiang'
__author_email__ = 'jiangying1110@outlook.com'
__license__ = 'MIT License'
__copyright__ = 'Copyright (C) 2017 jiang. All Rights Reserved'
__introduction__ = """
    ____    __  __    ____     ____    ___     _   __
   / __ \  / / / /   / __ \   /  _/   /   |   / | / /
  / / / / / / / /   / /_/ /   / /    / /| |  /  |/ / 
 / /_/ / / /_/ /   / _, _/  _/ /    / ___ | / /|  /  
/_____/  \____/   /_/ |_|  /___/   /_/  |_|/_/ |_/   
                                                     
                                            v{version}
GitHub: https://github.com/DurianCoder/Durian.git
Durian is a static code analysis system that automates the detecting vulnerabilities and security issue.""".format(version=__version__)
__epilog__ = """Usage:
  python {m} -t {td}
  python {m} -t {td} -r cvi-100001,cvi-100002
""".format(m='cobra.py', td='tests/vulnerabilities')
