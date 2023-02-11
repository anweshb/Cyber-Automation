def hello_world(file, make_new = False):
    if make_new:
        with open(file, "a+") as f:
            pass
    else:
        with open(file, "a+") as f:
            f.write("Hello World\n")
    