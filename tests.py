from  functions.run_python_file import run_python_file

def test():
    result = run_python_file("calculator", "main.py")
    print("should print the calculator's usage instructions after running calculator's main.py file:")
    print(result)
    print("")

    result = run_python_file("calculator", "main.py", ["3 + 5"])
    print("Result for running calculator file:")
    print(result)
    print("")

    result = run_python_file("calculator", "tests.py")
    print("Result for running to 'tests.py' file:")
    print(result)
    print("")

    result = run_python_file("calculator", "../main.py")
    print("Running python file from a bad file path - this should return an error")
    print(result)
    print("")

    result = run_python_file("calculator", "nonexistent.py")
    print("Running a non existent python file - this should return an error")
    print(result)
    print("")

    result = run_python_file("calculator", "lorem.txt")
    print("Running file 'lorem.tx' should return error becuase it is not a python file :")
    print(result)
    print("")


if __name__ == "__main__":
    test()
