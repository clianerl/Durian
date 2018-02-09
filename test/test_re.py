import re

if __name__ == "__main__":
    if re.match(r'^(cvi|CVI)-\d{6}(\.xml)?', "cvi-100001.xml".strip()):
        if ".xml" in "cvi-100001.xml":
            print(2)
    print(1)